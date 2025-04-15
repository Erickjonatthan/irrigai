import numpy as np
import pandas as pd
from app.globals import stop_event  # Atualize a importação
from app.process.data_receiving import balanco_hidrico_ano, precipitacao_ano_chirps
from app.process.graphics import PlotGrafico, gerar_grafico_balanco_hidrico, gerar_grafico_precipitacao, mostraGraficoDoAno

def processar_dados_aridez(_ano_inicial, _ano_final, _localdataName, _graficos, _NomeLocal):
    """
    Processa os dados de aridez para os anos fornecidos, calcula a média e gera o mapa de IA.
    """
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
        return mapaIA_path
    else:
        print("Nenhum dado foi processado. Verifique os arquivos de entrada.")
        return None

def processar_balanco_hidrico(_ano_inicial, _ano_final, data_Json, _localdataName, api, head, _graficos, _NomeLocal):
    """
    Processa o balanço hídrico para os anos fornecidos e gera o gráfico correspondente.
    """
    _balanco = pd.DataFrame(columns=["Ano", "ET", "PET", "Deficit"])

    for i in range(_ano_inicial, _ano_final + 1):
        print(f"Processando ano: {i}")
        et_series, pet_series = balanco_hidrico_ano(i, data_Json, _localdataName, api, head, stop_event)
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

    return _balanco, grafico_balanco_hidrico_path

def processar_precipitacao(_ano_inicial, _ano_final, data_Json, _localdataName, _graficos, _NomeLocal):
    """
    Processa os dados de precipitação para os anos fornecidos e gera o gráfico correspondente.
    """
    _precipitacao_df = pd.DataFrame(columns=["Ano", "Precipitacao"])

    for i in range(_ano_inicial, _ano_final + 1):
        print(f"Processando precipitação para o ano: {i}")
        precip_total = precipitacao_ano_chirps(i, data_Json, _localdataName, stop_event)
        if precip_total != 0:
            _precipitacao_df.loc[len(_precipitacao_df)] = [i, precip_total]
        else:
            print(f"Erro ao recuperar dados de precipitação para o ano {i}")

    _precipitacao_df["Ano"] = _precipitacao_df["Ano"].astype(int)

    # Converter o DataFrame para Series com o ano como índice
    precip_series = _precipitacao_df.set_index("Ano")["Precipitacao"]

    grafico_precipitacao_path = gerar_grafico_precipitacao(
        precip_series,              # Series com o índice sendo o ano
        _ano_inicial,
        _ano_final,
        _NomeLocal,
        _graficos
    )

    return _precipitacao_df, grafico_precipitacao_path
