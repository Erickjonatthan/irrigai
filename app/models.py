import os
from app.process.climate_analysis import calcular_e_classificar_indices_aridez, recomendar_irrigacao
from app.process.data_processing import processar_balanco_hidrico, processar_dados_aridez, processar_precipitacao
from app.process.file_operations import criar_diretorios, obter_caminhos_graficos
from app.process.graphics import calcular_e_gerar_grafico_rai, calcular_indices_e_gerar_graficos, gerar_grafico_indice_aridez_unep
from app.process.map_operations import criar_mapa
from app.process.utils import gerenciar_cache_parametros, get_location_name, obter_token_autenticacao
import climateservaccess as ca

_user = os.getenv('USER_ENV_VAR', '')
_password = os.getenv('PASSWORD_ENV_VAR', '')

def processar_dados(latitude, longitude, cultura, estagio, _ano_inicial=2022, _ano_final=2023, log=print):
    _res = 10
    inDir = 'app/static/cache_data'
    api = 'https://appeears.earthdatacloud.nasa.gov/api/'

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

    head = obter_token_autenticacao(api, _user, _password, log=log)

    gerenciar_cache_parametros(inDir, parametros_atual, api, head, log=log)
    

    _localdataName, _graficos = criar_diretorios(inDir, latitude, longitude, _res)

    _NomeLocal = get_location_name(latitude, longitude, log=log)
    _quadrado = ca.getBox(latitude, longitude, _res)

    mapa_path, data_Json, geo_json_data = criar_mapa(latitude, longitude, _quadrado, _graficos)


    log("Processando dados de balanço hídrico...")
    _balanco, grafico_balanco_hidrico_path = processar_balanco_hidrico(
        _ano_inicial, _ano_final, data_Json, _localdataName, api, head, _graficos, _NomeLocal, log=log
    )

    log("Gerando dados de precipitação...")
    _precipitacao_df, grafico_precipitacao_path = processar_precipitacao(
        _ano_inicial, _ano_final, data_Json, _localdataName, _graficos, _NomeLocal, log=log
    )

    log("Calculando índices de aridez...")
    calcular_indices_e_gerar_graficos(_balanco, _precipitacao_df, _ano_inicial, _ano_final, _graficos)

    log("Gerando gráfico de índice de aridez (UNEP)...")
    gerar_grafico_indice_aridez_unep(_balanco, _ano_inicial, _ano_final, _graficos)

    log("Classificando índices de aridez...")
    calcular_e_classificar_indices_aridez(_balanco, _ano_inicial, _ano_final)

    log("Processando dados para mapa de aridez com IA...")
    mapaIA_path = processar_dados_aridez(_ano_inicial, _ano_final, _localdataName, _graficos, _NomeLocal)

    log("Calculando RAI e gerando gráfico...")
    calcular_e_gerar_grafico_rai(_balanco, _precipitacao_df, _graficos)

    log("Obtendo caminhos dos gráficos finais...")
    grafico_precipitacao_path, grafico_rai_path, grafico_aridez_path, mapaIA_path = obter_caminhos_graficos(
        latitude, longitude, _res, _NomeLocal, _ano_inicial, _ano_final
    )

    dados_ET = _balanco["ET"]
    dados_PET = _balanco["PET"]
    dados_precipitacao = _precipitacao_df["Precipitacao"]
    anos = _balanco["Ano"]

    log("Gerando recomendações de irrigação...")
    recomendacoes = recomendar_irrigacao(cultura, estagio, dados_ET, dados_PET, dados_precipitacao, anos)

    log("Processamento completo! 🎉")

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
        "recomendacoes": recomendacoes,
    }
