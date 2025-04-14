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
from app.process.data_processing import precipitacao_ano_chirps, status, balanco_hidrico_ano
from app.process.map_operations import criar_mapa
from app.process.graphics import gerar_grafico_balanco_hidrico, gerar_grafico_precipitacao, mostraGraficoDoAno
from app.globals import stop_event  # Atualize a importação


_user = os.getenv('USER_ENV_VAR', '')
_password = os.getenv('PASSWORD_ENV_VAR', '')

# Função principal para processar os dados
def processar_dados(latitude, longitude, cultura, estagio, _ano_inicial=2001, _ano_final=2010):
    # Configurações iniciais
    _res = 10
    inDir = 'app/static/cache_data'
    api = 'https://appeears.earthdatacloud.nasa.gov/api/'

    #cria a pasta cache_data se não existir
    if not os.path.exists(inDir):
        os.makedirs(inDir)

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
    

    token_response = requests.post('{}login'.format(api), auth=(_user, _password)).json()
    token = token_response['token']                 
    head = {'Authorization': 'Bearer {}'.format(token)}
    print(token_response, token)

    _quadrado = ca.getBox(latitude, longitude, _res)
    mapa_path, data_Json, geo_json_data = criar_mapa(latitude, longitude, _quadrado, _graficos)

    _balanco = pd.DataFrame(columns=["Ano", "ET", "PET", "Deficit"])
    

    for i in range(_ano_inicial, _ano_final + 1):
        if stop_event.is_set():
            print("Processo interrompido pelo usuário no loop principal.")
            break

        print(f"Processando ano: {i}")
        et_series, pet_series = balanco_hidrico_ano(i, data_Json, _localdataName, api, head)

        if not (isinstance(et_series, pd.Series) and isinstance(pet_series, pd.Series)):
            print(f"Erro ao recuperar dados de ET/PET para o ano {i}")
            continue

        et_total = et_series.sum()
        pet_total = pet_series.sum()
        deficit = pet_total - et_total

        _balanco.loc[len(_balanco)] = [i, et_total, pet_total, deficit]

    _balanco["Ano"] = _balanco["Ano"].astype(int)

    grafico_balanco_hidrico_path = gerar_grafico_balanco_hidrico(
        _balanco,            # DataFrame com os dados
        _ano_inicial,        # Ano inicial
        _ano_final,          # Ano final
        _NomeLocal,          # Nome da localização (string)
        _graficos            # Caminho da pasta de saída
    )

    _precipitacao_df = pd.DataFrame(columns=["Ano", "Precipitacao"])

    for i in range(_ano_inicial, _ano_final + 1):
        if stop_event.is_set():
            print("Processo interrompido pelo usuário no loop principal.")
            break
        print(f"Processando precipitação para o ano: {i}")
        precip_series = precipitacao_ano_chirps(i, data_Json, _localdataName)
        if isinstance(precip_series, pd.Series) and not precip_series.empty:
            precip_total = precip_series.iloc[0]
            _precipitacao_df.loc[len(_precipitacao_df)] = [i, precip_total]
        else:
            print(f"Erro ao recuperar dados de precipitação para o ano {i}")

    _precipitacao_df["Ano"] = _precipitacao_df["Ano"].astype(int)
    print(_precipitacao_df)

    # Converter o DataFrame para Series com o ano como índice
    precip_series = _precipitacao_df.set_index("Ano")["Precipitacao"]

    grafico_precipitacao_path = gerar_grafico_precipitacao(
        precip_series,              # Series com o índice sendo o ano
        _ano_inicial,
        _ano_final,
        _NomeLocal,
        _graficos
    )

    # Calcula os índices de aridez e gera gráficos
    _balanco["Indice de Aridez UNEP"] = _precipitacao_df["Precipitacao"] / _balanco["PET"]
    _balanco["Aridez"] = _precipitacao_df["Precipitacao"] / _balanco["ET"]

    # Gráfico de precipitação e evaporação
    plt.figure(figsize=(10, 5))
    plt.plot(_balanco["Ano"], _precipitacao_df["Precipitacao"], label="Precipitation")
    plt.plot(_balanco["Ano"], _balanco["ET"], label="Evaporation")
    plt.xticks(np.arange(_ano_inicial, _ano_final + 1, 1), rotation=45)
    plt.xlabel('Year')
    plt.ylabel('Annual Total (mm)')
    plt.title('Average annual precipitation/evaporation')
    plt.legend()
    plt.savefig(os.path.join(_graficos, "precipitacao_e_evaporacao.png"), format="png")

    # Gráfico do índice de aridez UNEP
    z = np.polyfit(_balanco["Ano"], _balanco["Indice de Aridez UNEP"], 1)
    p = np.poly1d(z)  # Criando um objeto polinomial
    plt.figure(figsize=(10, 5))
    plt.plot(_balanco["Ano"], _balanco["Indice de Aridez UNEP"], label="Aridity index")
    plt.plot(_balanco["Ano"], p(_balanco["Ano"]), 'r-', label="Trend")
    plt.xticks(np.arange(_ano_inicial, _ano_final + 1, 1), rotation=45)
    plt.xlabel('Year')
    plt.ylabel('Aridity index')
    plt.title('Aridity index in the chosen region')
    plt.legend()
    plt.savefig(os.path.join(_graficos, "IA.png"), format="png")

    # Cálculo de médias e classificações
    indice_aridez_medio = _balanco["Indice de Aridez UNEP"].mean()
    indice_aridez_tendencia = p(_balanco["Ano"]).mean()
    indice_aridez_atual = _balanco.iloc[-1]["Indice de Aridez UNEP"]

    print(f"Essa região está classificada atualmente como sendo uma região {indice_aridez_atual:.2f}, "
          f"o que lhe classifica como uma região {categoria_climatica(indice_aridez_atual)}")
    print(f"Entre os anos de {_ano_inicial} e {_ano_final}, a região teve um índice médio de {indice_aridez_tendencia:.2f}, "
          f"o que lhe classifica como uma região {categoria_climatica(indice_aridez_tendencia)}")
    print(f"A chance de desertificação da região está classificada como {risco_desertificacao(indice_aridez_tendencia)}")

    # Comparação de índices de aridez
    _balanco["Aridez2"] = _balanco["ET"] / _balanco["PET"]
    indice_aridez2_medio = _balanco["Aridez2"].mean()
    print(f"Comparando os 2 índices para verificar equivalência {indice_aridez_medio:.2f} ~= {indice_aridez2_medio:.2f}")


    _dado = []
    for i in range(_ano_inicial, _ano_final + 1):  # Inclui todos os anos no intervalo
        try:
            print(f"Processando o ano {i}...")
            arid_data = mostraGraficoDoAno(i, _localdataName)
            _dado.append(arid_data)
        except FileNotFoundError as e:
            print(f"Erro ao processar o ano {i}: {e}")
    
    # Calcula a média dos dados de aridez ao longo dos anos processados
    if _dado:  # Verifica se há dados processados
        _final = np.mean(_dado, axis=0)
    
        # Gera o mapa usando os dados médios
        mapaIA_path = PlotGrafico(_final, f"{_ano_inicial}-{_ano_final}", _NomeLocal, _graficos)
        print(f"Mapa de IA salvo em: {mapaIA_path}")
    else:
        print("Nenhum dado foi processado. Verifique os arquivos de entrada.")
    
    # Cálculo do índice de anomalia de chuva (RAI)
    media_precipitacao = _precipitacao_df["Precipitacao"].mean()
    desvio_precipitacao = _precipitacao_df["Precipitacao"].std()

    _balanco["RAI"] = _precipitacao_df["Precipitacao"].apply(
        lambda precipitacao: (precipitacao - media_precipitacao) / desvio_precipitacao * 100
    )

    # Gráfico do índice de anomalia de chuva (RAI)
    _balanco.plot(kind='bar', x='Ano', y='RAI', title='Rain Anomaly Index (RAI)', xlabel='Anos', ylabel='RAI', color='blue')
    plt.savefig(os.path.join(_graficos, "RAI.png"), format="png")

    # Caminhos dos gráficos gerados
    grafico_precipitacao_path = os.path.join(f"cache_data/{latitude}_{longitude}_{_res}/resultados/grafico_precipitacao_Região_Nordeste_-_Brasil_2001_2010.png").replace("\\", "/")
    grafico_rai_path = os.path.join(f"cache_data/{latitude}_{longitude}_{_res}/resultados/RAI.png").replace("\\", "/")
    grafico_aridez_path = os.path.join(f"cache_data/{latitude}_{longitude}_{_res}/resultados/IA.png").replace("\\", "/")
    mapaIA_path = os.path.join(f"cache_data/{latitude}_{longitude}_{_res}/resultados/mapaIA2001-2010.png").replace("\\", "/")

    print(f"Gráfico de precipitação salvo em: {grafico_precipitacao_path}")
    print(f"Gráfico de RAI salvo em: {grafico_rai_path}")
    print(f"Gráfico de aridez salvo em: {grafico_aridez_path}")
    print(f"Mapa de IA salvo em: {mapaIA_path}")

    return {
        "nome_local": _NomeLocal,
        "ano_inicial": _ano_inicial,
        "ano_final": _ano_final,
        "area": _res,
        "latitude": latitude,
        "longitude": longitude,
        "grafico_precipitacao": grafico_precipitacao_path,
        "grafico_rai": grafico_rai_path,
        "grafico_aridez": grafico_aridez_path,
        "mapa_IA": mapaIA_path,
    }