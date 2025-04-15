import os
import time
import pandas as pd
import requests
import gzip
import shutil
import rioxarray
import geopandas as gpd
from shapely.geometry import shape

def status(id_tarefa, api, head):
    return requests.get(f'{api}task/{id_tarefa}', headers=head).json()['status']

def balanco_hidrico_ano(ano, data_Json, _localdataName, api, head, stop_event):
    """
    Baixa os dados de ET e PET para o ano especificado e retorna os totais anuais.
    """
    if stop_event.is_set():
        print(f"Processo interrompido pelo usuário antes de iniciar o ano {ano}.")
        return 0, 0

    produto_usado = "MOD16A3GF.061"
    bandas_usadas = ['ET_500m', 'PET_500m']
    task_name = f"BALANCO_HIDRICO_{ano}"
    _appEEARsDir = os.path.join(_localdataName, task_name)
    statistics_file = os.path.join(_appEEARsDir, "MOD16A3GF-061-Statistics.csv")

    # Verificar se os dados já existem localmente
    if os.path.exists(statistics_file):
        print(f"Carregando dados de {ano} localmente...")
        try:
            return processar_dados_localmente(statistics_file)
        except Exception as e:
            if not stop_event.is_set():
                print(f"Erro ao processar o arquivo local {statistics_file}: {e}")
            return 0, 0

    # Caso os dados não existam, criar e processar a tarefa
    try:
        if stop_event.is_set():
            print(f"Processo interrompido pelo usuário antes de criar a tarefa para o ano {ano}.")
            return 0, 0

        task_id = criar_tarefa(api, produto_usado, bandas_usadas, task_name, data_Json, _appEEARsDir, ano, head)
        if not task_id:
            raise ValueError(f"Falha ao criar a tarefa para o ano {ano}.")
        
        aguardar_tarefa(task_id, api, head, stop_event)
        baixar_arquivos(task_id, api, head, _appEEARsDir)
        return processar_dados_localmente(statistics_file)
    except Exception as e:
        if not stop_event.is_set():
            print(f"Erro ao processar dados para o ano {ano}: {e}")
        return 0, 0


def processar_dados_localmente(statistics_file):
    """
    Processa os dados locais do arquivo CSV e retorna os totais anuais de ET e PET como Series.
    """
    df = pd.read_csv(statistics_file)
    if 'Dataset' not in df.columns or 'Mean' not in df.columns:
        raise ValueError("Colunas 'Dataset' ou 'Mean' ausentes no arquivo de estatísticas.")
    
    et_total = df[df['Dataset'] == 'ET_500m']["Mean"].fillna(0).iloc[0]
    pet_total = df[df['Dataset'] == 'PET_500m']["Mean"].fillna(0).iloc[0]

    # Retornar os valores como Series
    return pd.Series([et_total], index=[0]), pd.Series([pet_total], index=[0])

def criar_tarefa(api, produto_usado, bandas_usadas, task_name, data_Json, _appEEARsDir, ano, head):
    """
    Cria uma tarefa na API para baixar os dados.
    """
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
                'format': {'type': 'geotiff'},
                'projection': proj
            },
            'geo': data_Json
        }
    }

    os.makedirs(_appEEARsDir, exist_ok=True)
    print(f"Enviando tarefa para {ano}...")
    task_response = requests.post(f'{api}task', json=task, headers=head).json()
    print(f"Resposta da API ao criar tarefa para {ano}: {task_response}")

    return task_response.get('task_id')


def aguardar_tarefa(task_id, api, head, stop_event):
    """
    Aguarda a conclusão da tarefa na API.
    """
    starttime = time.time()
    intervalo = 20.0
    _status = status(task_id, api, head)
    while _status != 'done':
        if stop_event.is_set():
            print(f"Processo interrompido pelo usuário durante a execução da tarefa {task_id}.")
            return
        print(f"Status: {_status}")
        time.sleep(intervalo - ((time.time() - starttime) % intervalo))
        _status = status(task_id, api, head)
    if _status != 'done':
        raise RuntimeError(f"Tarefa {task_id} não foi concluída com sucesso.")


def baixar_arquivos(task_id, api, head, _appEEARsDir):
    """
    Baixa os arquivos gerados pela tarefa.
    """
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

def precipitacao_ano_chirps(ano, data_Json, _localdataName, stop_event):
    """
    Processa os dados anuais de precipitação do CHIRPS-2.0 (global_annual, resolução p05)
    para um determinado ano, recortando pela área de interesse (definida em data_Json)
    e retornando o total anual de precipitação (mm) na área.
    """
    if stop_event.is_set():
        print(f"Processo interrompido pelo usuário antes de iniciar o ano {ano}.")
        return 0

    # Criar diretório para armazenar os arquivos do ano
    pasta_ano = os.path.join(_localdataName, f"CHIRPS_annual")
    os.makedirs(pasta_ano, existindo=True)

    # Nome do arquivo anual
    nome_tif = f"chirps-v2.0.{ano}.tif"
    destino_tif = os.path.join(pasta_ano, nome_tif)
    url = f"https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_annual/tifs/{nome_tif}"

    # Baixar o arquivo se não existir
    if not os.path.exists(destino_tif):
        if stop_event.is_set():
            print(f"Processo interrompido pelo usuário antes de baixar o arquivo para o ano {ano}.")
            return 0

        print(f"Baixando {url} ...")
        try:
            r = requests.get(url, stream=True)
            if r.status_code != 200:
                if not stop_event.is_set():
                    print(f"Erro ao baixar {url}. Código de status: {r.status_code}")
                return 0
            with open(destino_tif, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if stop_event.is_set():
                        print(f"Processo interrompido pelo usuário durante o download do ano {ano}.")
                        return 0
                    f.write(chunk)
            print(f"Arquivo {destino_tif} baixado com sucesso.")
        except Exception as e:
            if not stop_event.is_set():
                print(f"Erro ao baixar o arquivo {url}: {e}")
            return 0

    # Processar o arquivo GeoTIFF
    try:
        if stop_event.is_set():
            print(f"Processo interrompido pelo usuário antes de processar o arquivo para o ano {ano}.")
            return 0

        ds = rioxarray.open_rasterio(destino_tif)
        ds = ds.where(ds != -9999.0)
        geometria = data_Json["features"][0]["geometry"] if data_Json.get("type").lower() == "featurecollection" else data_Json
        gdf = gpd.GeoDataFrame({'geometry': [shape(geometria)]}, crs="EPSG:4326")
        ds_clip = ds.rio.clip(gdf.geometry, gdf.crs, drop=True)
        media_anual = ds_clip.mean().item()
        print(f"Média anual de precipitação: {media_anual:.2f} mm")
    except Exception as e:
        if not stop_event.is_set():
            print(f"Erro ao processar o arquivo {destino_tif}: {e}")
        return 0

    return media_anual