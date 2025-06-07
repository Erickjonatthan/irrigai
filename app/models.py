import os
from app.process.climate_analysis import calcular_e_classificar_indices_aridez, recomendar_irrigacao, processar_dados_aridez
from app.process.data_processing import processar_balanco_hidrico, processar_precipitacao
from app.process.file_operations import criar_diretorios, obter_caminhos_graficos
from app.process.graphics import calcular_e_gerar_grafico_rai, calcular_indices_e_gerar_graficos, gerar_grafico_indice_aridez_unep
from app.process.map_operations import criar_mapa
from app.process.utils import get_location_name
import climateservaccess as ca
from app.globals import api_url as api
from app.dto.dtos import ResultadosDTO
from app.dto.dtos import ProcessarDadosDTO


def processar_dados(dto: ProcessarDadosDTO, log=print):
    """
    Processa os dados necessários para o sistema, utilizando o cabeçalho de autenticação (head) fornecido.
    """
    _res = 10
    inDir = 'app/static/data'

    if not os.path.exists(inDir):
        os.makedirs(inDir)

    _localdataName, _graficos = criar_diretorios(inDir, dto.user_id, dto.latitude, dto.longitude, _res)

    _NomeLocal = get_location_name(dto.latitude, dto.longitude, log=log)
    _quadrado = ca.getBox(dto.latitude, dto.longitude, _res)

    data_Json = criar_mapa(dto.latitude, dto.longitude, _quadrado, _graficos)

    log("Processando dados de balanço hídrico...")
    _balanco, dados_grafico_balanco_hidrico = processar_balanco_hidrico(
        dto.ano_inicial, dto.ano_final, data_Json, _localdataName, api, dto.head, _NomeLocal, log=log
    )

    log("Gerando dados de precipitação...")
    _precipitacao_df, dados_grafico_precipitacao = processar_precipitacao(
        dto.ano_inicial, dto.ano_final, data_Json, _localdataName, _graficos, _NomeLocal, log=log
    )

    log("Calculando índices de aridez...")
    dados_grafico_precipitacao_vs_evaporacao = calcular_indices_e_gerar_graficos(_balanco, _precipitacao_df, dto.ano_inicial, dto.ano_final, _graficos)

    log("Gerando dados de índice de aridez (UNEP)...")
    dados_grafico_aridez = gerar_grafico_indice_aridez_unep(_balanco, dto.ano_inicial, dto.ano_final, _graficos)

    log("Classificando índices de aridez...")
    indices_e_classificacoes = calcular_e_classificar_indices_aridez(_balanco, dto.ano_inicial, dto.ano_final)

    log("Processando dados para mapa de aridez com o indice de aridez...")
    mapaIA_path = processar_dados_aridez(dto.ano_inicial, dto.ano_final, _localdataName, _graficos, _NomeLocal)

    log("Calculando RAI e gerando dados...")
    dados_grafico_rai = calcular_e_gerar_grafico_rai(_balanco, _precipitacao_df, _graficos)

    log("Obtendo caminho do mapa...")
    mapaIA_path = obter_caminhos_graficos(
        dto.latitude, dto.longitude, _res, dto.ano_inicial, dto.ano_final, dto.user_id
    )

    dados_ET = _balanco["ET"]
    dados_PET = _balanco["PET"]
    dados_precipitacao = _precipitacao_df["Precipitacao"]
    anos = _balanco["Ano"]

    log("Gerando recomendações de irrigação...")
    recomendacoes = recomendar_irrigacao(dto.cultura, dto.estagio, dados_ET, dados_PET, dados_precipitacao, anos)

    log("Processamento completo! 🎉")

    return ResultadosDTO(
        nome_local=_NomeLocal,
        ano_inicial=dto.ano_inicial,
        ano_final=dto.ano_final,
        area=_res,
        latitude=dto.latitude,
        longitude=dto.longitude,
        dados_grafico_precipitacao=dados_grafico_precipitacao,
        dados_grafico_precipitacao_vs_evaporacao=dados_grafico_precipitacao_vs_evaporacao,
        dados_grafico_balanco_hidrico=dados_grafico_balanco_hidrico,
        dados_grafico_rai=dados_grafico_rai,
        dados_grafico_aridez=dados_grafico_aridez,
        mapa_IA=mapaIA_path,
        indices_e_classificacoes=indices_e_classificacoes,
        recomendacoes=recomendacoes,
    )