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
from app.process.utils import gerenciar_cache_parametros, get_location_name
from app.process.climate_analysis import calcular_e_classificar_indices_aridez, categoria_climatica, risco_desertificacao, recomendar_irrigacao
from app.process.file_operations import criar_diretorios, obter_caminhos_graficos
from app.process.visualization import PlotGrafico, calcular_e_gerar_grafico_rai, processar_balanco_hidrico, processar_dados_aridez
from app.process.data_processing import precipitacao_ano_chirps, processar_precipitacao, status, balanco_hidrico_ano
from app.process.map_operations import criar_mapa
from app.process.graphics import calcular_indices_e_gerar_graficos, gerar_grafico_balanco_hidrico, gerar_grafico_indice_aridez_unep, gerar_grafico_precipitacao, mostraGraficoDoAno


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

    parametros_atual = {
        "latitude": latitude,
        "longitude": longitude,
        "cultura": cultura,
        "estagio": estagio,
        "ano_inicial": _ano_inicial,
        "ano_final": _ano_final,
        "res": _res
    }
    
    gerenciar_cache_parametros(inDir, parametros_atual)
    
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

    _balanco, grafico_balanco_hidrico_path = processar_balanco_hidrico(
        _ano_inicial, _ano_final, data_Json, _localdataName, api, head, _graficos, _NomeLocal
    )

    _precipitacao_df, grafico_precipitacao_path = processar_precipitacao(
        _ano_inicial, _ano_final, data_Json, _localdataName, _graficos, _NomeLocal
    )

    # Calcula os índices de aridez e gera gráficos
    calcular_indices_e_gerar_graficos(_balanco, _precipitacao_df, _ano_inicial, _ano_final, _graficos)
    
    # Gráfico do índice de aridez UNEP
    gerar_grafico_indice_aridez_unep(_balanco, _ano_inicial, _ano_final, _graficos)
    
    # Cálculo de médias e classificações
    calcular_e_classificar_indices_aridez(_balanco, _ano_inicial, _ano_final)

    mapaIA_path = processar_dados_aridez(_ano_inicial, _ano_final, _localdataName, _graficos, _NomeLocal)
    
    calcular_e_gerar_grafico_rai(_balanco, _precipitacao_df, _graficos)

    grafico_precipitacao_path, grafico_rai_path, grafico_aridez_path, mapaIA_path = obter_caminhos_graficos(
        latitude, longitude, _res, _ano_inicial, _ano_final
    )

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