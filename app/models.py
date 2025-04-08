import json
import os
import time
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import climateservaccess as ca
import numpy as np
import requests
from app.process.utils import get_location_name
from app.process.climate_analysis import categoria_climatica, risco_desertificacao, recomendar_irrigacao
from app.process.file_operations import criar_diretorios
from app.process.visualization import PlotGrafico
from app.process.data_processing import status, precipitacao_ano
from app.process.map_operations import criar_mapa
from app.process.graphics import gerar_grafico_precipitacao, mostraGraficoDoAno

# ...restante do código...
_user = os.getenv('USER_ENV_VAR', '')
_password = os.getenv('PASSWORD_ENV_VAR', '')

# Função principal para processar os dados
def processar_dados(latitude, longitude, cultura, estagio, _ano_inicial=2001, _ano_final=2023):
    # Configurações iniciais
    _res = 10
    inDir = 'app/static/cache_data'
    api = 'https://appeears.earthdatacloud.nasa.gov/api/'

    # Caminho para o arquivo de cache de parâmetros
    parametros_cache_path = os.path.join(inDir, "parametros_cache.json")

    # Verificar se o cache de parâmetros existe
    parametros_atual = {
        "latitude": latitude,
        "longitude": longitude,
        "cultura": cultura,
        "estagio": estagio,
        "ano_inicial": _ano_inicial,
        "ano_final": _ano_final,
        "res": _res
    }

    if os.path.exists(parametros_cache_path):
        with open(parametros_cache_path, "r") as f:
            parametros_salvos = json.load(f)

        # Comparar os parâmetros atuais com os salvos
        if parametros_atual != parametros_salvos:
            print("Parâmetros diferentes detectados. Limpando o cache...")
            # Apagar todo o conteúdo da pasta inDir
            for root, dirs, files in os.walk(inDir, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
    else:
        print("Nenhum cache encontrado. Continuando com a execução...")

    # Salvar os parâmetros atuais no cache
    with open(parametros_cache_path, "w") as f:
        json.dump(parametros_atual, f)

    _localdataName, _graficos = criar_diretorios(inDir, latitude, longitude, _res)


    # Obter o nome da localização
    _NomeLocal = get_location_name(latitude, longitude)
    print(f"Nome da região: {_NomeLocal}")
    
    _quadrado = ca.getBox(latitude, longitude, _res)
    mapa_path, data_Json, geo_json_data = criar_mapa(latitude, longitude, _quadrado, _graficos)

    _precipitacao = {}
    for i in range(_ano_inicial, _ano_final + 1):
        _precipitacao[i] = precipitacao_ano(i, _quadrado, _localdataName)

    _dados = pd.DataFrame()
    _dados["Ano"] = []
    _dados["Precipitacao"] = []
    for i in range(_ano_inicial, _ano_final + 1):
        total = _precipitacao[i].sum()
        _dados.loc[len(_dados.index)] = [i, total]
    _dados["Ano"] = _dados["Ano"].astype(int)

    grafico_precipitacao_path = gerar_grafico_precipitacao(_dados, _ano_inicial, _ano_final, _NomeLocal, _graficos)

    token_response = requests.post('{}login'.format(api), auth=(_user, _password)).json()
    token = token_response['token']                 
    head = {'Authorization': 'Bearer {}'.format(token)}
    print(token_response, token)

    produto_usado = "MOD16A3GF.061"
    lst_response = requests.get('{}product/{}'.format(api, produto_usado)).json()
    list(lst_response.keys())
    
    projections = requests.get('{}spatial/proj'.format(api)).json()
    projs = {}  # Create an empty dictionary
    for p in projections:
        projs[p['Name']] = p
    print(projs.keys()) 

    prodLayer = []
    bandas_usadas = ['ET_500m',  'PET_500m']
    for l in lst_response.keys():
        if l in bandas_usadas:
            prodLayer.append({
                    "layer": l,
                    "product": produto_usado
                })
    print("Prodlayer",prodLayer)

    #Configuraçoes de tarefa
    task_type = ['point','area']        # Type of task, area or point
    proj = projs['geographic']['Name']  # Set output projection 
    outFormat = ['geotiff', 'netcdf4']  # Set output file format type
    recurring = True                   # Specify True for a recurring date range
    yearRange = [_ano_inicial, _ano_final]
    task_name = _NomeLocal+" "+str(_ano_inicial)
    task = {
            'task_type': task_type[1],
            'task_name': task_name,
            'params': {
                'dates': [
                {
                    'startDate': '01-01',
                    'endDate': '12-31',
                    'yearRange': yearRange,
                    'recurring': recurring
                }],
                'layers': prodLayer,
                'output': {
                        'format': {
                                'type': outFormat[0]}, 
                                'projection': proj},
                'geo': data_Json,
            }
        }
    
    print(task)

    task_response = ""
    _appEEARsDir = _localdataName+"/"+task_name
    if not os.path.exists(_appEEARsDir):
        os.makedirs(_appEEARsDir)
        task_response = requests.post('{}task'.format(api), json=task, headers=head).json()
        print(task_response)
    else:
        print("Os dados iniciais já haviam sido baixados.")

    # Verificar se os arquivos necessários já existem
    statistics_file = os.path.join(_appEEARsDir, "MOD16A3GF-061-Statistics.csv")
    if not os.path.exists(statistics_file):
        if task_response != "":
            task_id = task_response.get('task_id')
            if task_id:
                status_response = requests.get('{}status/{}'.format(api, task_id), headers=head).json()
                print(status_response)
                starttime = time.time()
                intervalo = 20.0
                _status = status(task_id, api, head)
                while _status != 'done':
                    _status = status(task_id, api, head)
                    time.sleep(intervalo - ((time.time() - starttime) % intervalo))
                    print(_status)
                print(_status)

                if _status == 'done':
                    try:
                        bundle = requests.get('{}bundle/{}'.format(api, task_id), headers=head).json()
                        print("Bundle", bundle)
                        files = {}
                        for f in bundle['files']: files[f['file_id']] = f['file_name']
                        cont = 0
                        numero = len(files)
                        for f in files:
                            if files[f].endswith('.tif'):
                                filename = files[f].split('/')[1]
                            else:
                                filename = files[f]
                            if os.path.exists(_appEEARsDir + "/" + filename):
                                cont += 1
                            else:
                                dl = requests.get('{}bundle/{}/{}'.format(api, task_id, f), headers=head, stream=True, allow_redirects=True)
                                filepath = os.path.join(_appEEARsDir, filename)
                                with open(filepath, 'wb') as file:
                                    for data in dl.iter_content(chunk_size=8192):
                                        file.write(data)
                                cont += 1
                            print(f"Baixando arquivos {cont} / {numero}")
                        print('Todos os arquivos da tarefa salvos em: {}'.format(_appEEARsDir))
                    except Exception as e:
                        print(f"Erro ao baixar os arquivos da tarefa: {e}")
                else:
                    print("A tarefa não foi concluída com sucesso.")
            else:
                print("Nenhum task_id encontrado na resposta da tarefa.")
        else:
            print("A resposta da tarefa está vazia ou os dados já haviam sido baixados.")
    else:
        print(f"O arquivo {statistics_file} já existe. Pulando o download.")

    # Verificar novamente se o arquivo MOD16A3GF-061-Statistics.csv existe antes de tentar lê-lo
    if os.path.exists(statistics_file):
        _dataEvapo = pd.read_csv(statistics_file)
    else:
        print(f"Arquivo {statistics_file} não encontrado. Verifique se os dados foram baixados corretamente.")

    mean_1, mean_2 = np.array_split(_dataEvapo["Mean"], 2)
    nova_tabela1 = pd.DataFrame({"ET": mean_1})
    nova_tabela2 = pd.DataFrame( {"PET": mean_2.to_list()})
    _dados["ET"] = nova_tabela1["ET"]
    _dados["PET"] = nova_tabela2["PET"]

    #Com o ET e PET, podemos recomendar a irrigação
    recomendacoes = recomendar_irrigacao(cultura, estagio, _dados["ET"], _dados["PET"])

    plt.figure(figsize=(10,5))
    plt.plot(_dados["Ano"], _dados["Precipitacao"], label="Precipitation")
    plt.plot(_dados["Ano"], _dados["ET"], label="Evaporation")
    plt.xticks(np.arange(_ano_inicial, _ano_final+1, 1), [str(i) for i in range(_ano_inicial, _ano_final+1)],  rotation=45)
    plt.xlabel('Year')
    plt.ylabel('Annual Total (mm)')
    plt.title(f'Average annual precipitation/evaporation')
    plt.legend()
    plt.savefig(os.path.join(_graficos, "precipitacao e evaporacao.png"), format="png")

    _dados['Indice de Aridez UNEP'] = _dados["Precipitacao"] / _dados["PET"]
    _dados['Aridez'] = _dados["Precipitacao"] / _dados["ET"]


    z = np.polyfit(_dados["Ano"], _dados["Indice de Aridez UNEP"], 1)
    p = np.poly1d(z) # Criando um objeto polinomial
    plt.figure(figsize=(10,5))
    plt.plot(_dados["Ano"], _dados["Indice de Aridez UNEP"],label="Aridity index")
    plt.plot(_dados["Ano"], p(_dados["Ano"]), 'r-',label="Trend")
    plt.xticks(np.arange(_ano_inicial, _ano_final+1, 1), [str(i) for i in range(_ano_inicial, _ano_final+1)], rotation=45)
    plt.xlabel('Year')
    plt.ylabel('Aridity index')
    plt.title(f'Aridity index in the chosen region')
    plt.legend()
    plt.savefig(os.path.join(_graficos, "IA.png"), format="png")



    _Aridez = _dados['Indice de Aridez UNEP'].mean()
    _AriderN = (p(_dados["Ano"])).mean()
    aridez = _dados.iloc[-1]['Indice de Aridez UNEP']
    print(f"Essa região está classificada atualmente como sendo uma região {aridez:.2f}, o que lhe classifica como uma região {categoria_climatica(aridez)}")
    print(f"Entre os anos de {_ano_inicial } e {_ano_final}, a região teve um indice medio de {_AriderN:.2f}, o que lhe classifica como uma região {categoria_climatica(_AriderN)}")
    print(f"A chance de desertificação da região está classificada como {risco_desertificacao(_AriderN)}")
    #if a < 0:
    #    print("Foi observado um processo de diminuição do total de chuva em relação ao total de evaporação")

    _dados["Aridez2"] = _dados["ET"] / _dados["PET"]
    _Aridez2 = _dados['Aridez2'].mean()
    print(f"Comparando os 2 indices para verificar equivalencia {_Aridez:.2f} ~= {_Aridez2:.2f}")


    nomes = os.listdir(_appEEARsDir) 

    _dado = []
    for i in range(_ano_inicial,_ano_final,2):
        _dado.append(mostraGraficoDoAno(i, _appEEARsDir, nomes))
    _final = np.mean(_dado, axis=0) 

    mapaIA_path = PlotGrafico(_final,"2000-2022", _NomeLocal, _graficos)

    def rai(precipitacao, media, desvio):
        return (precipitacao - media) / desvio * 100
    # Calcula a media e o desvio da coluna Precipitacao
    media = _dados['Precipitacao'].mean()
    desvio = _dados['Precipitacao'].std()

    # Cria uma nova coluna RAI aplicando a funcao rai a cada valor da coluna Precipitacao
    _dados['RAI'] = _dados['Precipitacao'].apply(rai, args=(media, desvio))


    _dados.plot(kind='bar', x='Ano', y='RAI', title='Rain Anomaly Index (RAI)', xlabel='Anos', ylabel='RAI', color='blue')
    plt.savefig(os.path.join(_graficos, "RAI.png"), format="png")

    grafico_precipitacao_path = os.path.join(f"cache_data/{latitude}_{longitude}_{_res}/resultados/precipitacao.png").replace("\\", "/")
    grafico_rai_path = os.path.join(f"cache_data/{latitude}_{longitude}_{_res}/resultados/RAI.png").replace("\\", "/")
    grafico_aridez = os.path.join(f"cache_data/{latitude}_{longitude}_{_res}/resultados/IA.png").replace("\\", "/")
    mapaIA_path = os.path.join(f"cache_data/{latitude}_{longitude}_{_res}/resultados/mapaIA2000-2022.png").replace("\\", "/")

    print(f"Gráfico de precipitação salvo em: {mapaIA_path}")
    return {
        "nome_local": _NomeLocal,
        "ano_inicial": _ano_inicial,
        "ano_final": _ano_final,
        "area": _res,
        "latitude": latitude,
        "longitude": longitude,
        "grafico_precipitacao": grafico_precipitacao_path,
        "recomendacoes": recomendacoes.to_dict(orient="records"),
        "indice_aridez": _Aridez,
        "indice_aridez_ano": aridez,
        "indice_aridez_ano_medio": _AriderN,
        "risco_desertificacao": risco_desertificacao(_AriderN),
        "grafico_rai": grafico_rai_path,
        "grafico_aridez": grafico_aridez,
        "mapa_IA": mapaIA_path,
    }