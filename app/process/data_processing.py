import os
import time
import pandas as pd
import requests
import gzip
import shutil
import datetime
from shapely.geometry import shape
import rioxarray
import geopandas as gpd

def status(id_tarefa, api, head):
    return requests.get(f'{api}task/{id_tarefa}', headers=head).json()['status']

def balanco_hidrico_ano(ano, data_Json, _localdataName, api, head):
    """
    Baixa os dados de ET e PET para o ano especificado e retorna duas Series com os valores mensais.
    """
    produto_usado = "MOD16A3GF.061"
    bandas_usadas = ['ET_500m', 'PET_500m']
    task_name = f"BALANCO_HIDRICO_{ano}"
    _appEEARsDir = os.path.join(_localdataName, task_name)
    statistics_file = os.path.join(_appEEARsDir, "MOD16A3GF-061-Statistics.csv")

    if os.path.exists(statistics_file):
        print(f"Carregando dados de {ano} localmente...")
        try:
            df = pd.read_csv(statistics_file)
            # Verificar se as colunas 'Dataset' e 'Mean' existem
            if 'Dataset' not in df.columns or 'Mean' not in df.columns:
                print(f"Erro: O arquivo {statistics_file} não contém as colunas esperadas ('Dataset' e 'Mean').")
                return pd.Series(dtype=float), pd.Series(dtype=float)
            
            # Filtrar os dados com base na coluna 'Dataset'
            et_series = df[df['Dataset'] == 'ET_500m']["Mean"].fillna(0)
            pet_series = df[df['Dataset'] == 'PET_500m']["Mean"].fillna(0)
            return et_series, pet_series
        except Exception as e:
            print(f"Erro ao processar o arquivo {statistics_file}: {e}")
            return pd.Series(dtype=float), pd.Series(dtype=float)

    # Criar tarefa
    lst_response = requests.get(f'{api}product/{produto_usado}').json()
    projections = requests.get(f'{api}spatial/proj').json()

    proj = next((p['Name'] for p in projections if p['Name'] == 'geographic'), None)
    prodLayer = [{"layer": l, "product": produto_usado} for l in lst_response if l in bandas_usadas]

    task = {
        'task_type': 'area',
        'task_name': task_name,
        'params': {
            'dates': [{
                'startDate': '01-01',
                'endDate': '12-31',
                'yearRange': [ano, ano],
                'recurring': True
            }],
            'layers': prodLayer,
            'output': {
                'format': {'type': 'geotiff'},  # Alterado para 'geotiff'
                'projection': proj
            },
            'geo': data_Json
        }
    }

    os.makedirs(_appEEARsDir, exist_ok=True)
    print(f"Enviando tarefa para {ano}...")
    task_response = requests.post(f'{api}task', json=task, headers=head).json()

    # Adicionar logs para depuração
    print(f"Resposta da API ao criar tarefa para {ano}: {task_response}")

    task_id = task_response.get('task_id')

    if not task_id:
        print(f"Erro ao criar tarefa para {ano}. Resposta da API: {task_response}")
        return pd.Series(dtype=float), pd.Series(dtype=float)

    # Esperar a tarefa finalizar
    starttime = time.time()
    intervalo = 20.0
    _status = status(task_id, api, head)
    while _status != 'done':
        print(f"Status: {_status}")
        time.sleep(intervalo - ((time.time() - starttime) % intervalo))
        _status = status(task_id, api, head)

    # Download dos arquivos
    if _status == 'done':
        try:
            bundle = requests.get(f'{api}bundle/{task_id}', headers=head).json()
            for f in bundle['files']:
                filename = f['file_name'].split('/')[-1]
                filepath = os.path.join(_appEEARsDir, filename)
                if not os.path.exists(filepath):
                    print(f"Baixando {filename}")
                    dl = requests.get(f'{api}bundle/{task_id}/{f["file_id"]}', headers=head, stream=True)
                    with open(filepath, 'wb') as file:
                        for data in dl.iter_content(chunk_size=8192):
                            file.write(data)
        except Exception as e:
            print(f"Erro ao baixar arquivos da tarefa: {e}")
            return pd.Series(dtype=float), pd.Series(dtype=float)

    # Processar os dados no formato 'geotiff'
    try:
        import rasterio
        et_series = []
        pet_series = []
        for f in os.listdir(_appEEARsDir):
            if 'ET_500m' in f:
                with rasterio.open(os.path.join(_appEEARsDir, f)) as src:
                    et_series.append(src.read(1).mean())
            elif 'PET_500m' in f:
                with rasterio.open(os.path.join(_appEEARsDir, f)) as src:
                    pet_series.append(src.read(1).mean())

        return pd.Series(et_series), pd.Series(pet_series)
    except Exception as e:
        print(f"Erro ao processar arquivos GeoTIFF: {e}")
        return pd.Series(dtype=float), pd.Series(dtype=float)




def baixar_e_descompactar(url, destino_gz, destino_tif):
    """
    Baixa um arquivo se não existir e descompacta (.gz para .tif).
    """
    if not os.path.exists(destino_gz):
        print(f"Baixando {url} ...")
        r = requests.get(url, stream=True)
        if r.status_code != 200:
            print(f"Erro ao baixar {url}. Código de status: {r.status_code}")
            return False
        with open(destino_gz, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    else:
        print(f"Arquivo {destino_gz} já existe.")
    
    # Descompactar se o .tif ainda não existir
    if not os.path.exists(destino_tif):
        try:
            with gzip.open(destino_gz, 'rb') as f_in:
                with open(destino_tif, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            print(f"Descompactado para {destino_tif}.")
        except Exception as e:
            print(f"Erro ao descompactar {destino_gz}: {e}")
            return False
    return True

def precipitacao_ano_chirps(ano, data_Json, _localdataName):
    """
    Processa os dados anuais de precipitação do CHIRPS-2.0 (global_annual, resolução p05)
    para um determinado ano, recortando pela área de interesse (definida em data_Json)
    e retornando a média anual de precipitação (mm) na área.

    Parâmetros:
      - ano: inteiro (ex.: 2025)
      - data_Json: GeoJSON (dicionário) representando a área de interesse
      - _localdataName: pasta local para armazenar os dados

    Retorna:
      - Uma pandas Series com a média anual de precipitação (mm) na área
    """
    import os
    import requests
    import rioxarray
    import pandas as pd
    import geopandas as gpd
    from shapely.geometry import shape

    # Criar diretório para armazenar os arquivos do ano
    pasta_ano = os.path.join(_localdataName, f"CHIRPS_annual")
    os.makedirs(pasta_ano, exist_ok=True)

    # Nome do arquivo anual
    nome_tif = f"chirps-v2.0.{ano}.tif"
    destino_tif = os.path.join(pasta_ano, nome_tif)
    url = f"https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_annual/tifs/{nome_tif}"

    # Baixar o arquivo se não existir
    if not os.path.exists(destino_tif):
        print(f"Baixando {url} ...")
        try:
            r = requests.get(url, stream=True)
            if r.status_code != 200:
                print(f"Erro ao baixar {url}. Código de status: {r.status_code}")
                return pd.Series([])
            with open(destino_tif, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Arquivo {destino_tif} baixado com sucesso.")
        except Exception as e:
            print(f"Erro ao baixar o arquivo {url}: {e}")
            return pd.Series([])

    # Converter data_Json para GeoDataFrame
    try:
        if data_Json.get("type").lower() == "featurecollection":
            geometria = data_Json["features"][0]["geometry"]
        else:
            geometria = data_Json
        gdf = gpd.GeoDataFrame({'geometry': [shape(geometria)]}, crs="EPSG:4326")
    except Exception as e:
        print(f"Erro na conversão do data_Json: {e}")
        return pd.Series([])

    # Processar o arquivo GeoTIFF
    try:
        ds = rioxarray.open_rasterio(destino_tif)
        print(f"Arquivo {destino_tif} carregado. Valores brutos: min={ds.min().item()}, max={ds.max().item()}")

        # Substituir valores de "NoData" (-9999.0) por NaN
        ds = ds.where(ds != -9999.0)

        # Clip dos dados para a área definida
        ds_clip = ds.rio.clip(gdf.geometry, gdf.crs, drop=True)
        print(f"Recorte realizado. Valores após o recorte: min={ds_clip.min().item()}, max={ds_clip.max().item()}")

        # Cálculo da média espacial de precipitação
        media_anual = ds_clip.mean().item()
        print(f"Média anual de precipitação: {media_anual:.2f} mm")
    except Exception as e:
        print(f"Erro ao processar o arquivo {destino_tif}: {e}")
        return pd.Series([])

    return pd.Series([media_anual])
