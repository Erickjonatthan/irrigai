import pandas as pd
from app.globals import stop_event  # Atualize a importação
from app.process.data_receiving import balanco_hidrico_ano, precipitacao_ano_chirps
from app.process.graphics import gerar_dados_balanco_hidrico, gerar_dados_precipitacao


def processar_balanco_hidrico(_ano_inicial, _ano_final, data_Json, _localdataName, api, head, _NomeLocal, log=print):
    """
    Processa o balanço hídrico para os anos fornecidos e gera o gráfico correspondente.
    """
    _balanco = pd.DataFrame(columns=["Ano", "ET", "PET", "Deficit"])
    tarefas_criadas = []

    for i in range(_ano_inicial, _ano_final + 1):
        if stop_event.is_set():
            print(f"Processo interrompido pelo usuário antes de processar o ano {i}.")
            break

        print(f"Processando ano: {i}")
        et_series, pet_series = balanco_hidrico_ano(i, data_Json, _localdataName, api, head, stop_event, tarefas_criadas, log=log)
        if stop_event.is_set():
            log(f"Processo interrompido pelo usuário durante o processamento do ano {i}.")
            break

        if not (isinstance(et_series, pd.Series) and isinstance(pet_series, pd.Series)):
            if not stop_event.is_set():
                log(f"Erro ao recuperar dados de ET/PET para o ano {i}")
            continue

        et_total = et_series.sum()
        pet_total = pet_series.sum()
        deficit = pet_total - et_total

        _balanco.loc[len(_balanco)] = [i, et_total, pet_total, deficit]

    if _balanco.empty:
        log("Nenhum dado de balanço hídrico foi processado.")
        return None, None

    _balanco["Ano"] = _balanco["Ano"].astype(int)
    

    log("Gerando gráfico de balanço hídrico...")
    grafico_balanco_hidrico_dados = gerar_dados_balanco_hidrico(
        _balanco,            # DataFrame com os dados
        _NomeLocal,          # Nome da localização (string)
    )

    return _balanco, grafico_balanco_hidrico_dados


def processar_precipitacao(_ano_inicial, _ano_final, data_Json, _localdataName, _graficos, _NomeLocal, log=print):
    """
    Processa os dados de precipitação para os anos fornecidos e gera o gráfico correspondente.
    """
    _precipitacao_df = pd.DataFrame(columns=["Ano", "Precipitacao"])

    for i in range(_ano_inicial, _ano_final + 1):
        if stop_event.is_set():
            log(f"Processo interrompido pelo usuário antes de processar a precipitação do ano {i}.")
            break

        print(f"Processando precipitação para o ano: {i}")
        precip_total = precipitacao_ano_chirps(i, data_Json, _localdataName, stop_event, log=log)
        if stop_event.is_set():
            log(f"Processo interrompido pelo usuário durante o processamento da precipitação do ano {i}.")
            break

        if precip_total != 0:
            _precipitacao_df.loc[len(_precipitacao_df)] = [i, precip_total]
        else:
            if not stop_event.is_set():
                log(f"Erro ao recuperar dados de precipitação para o ano {i}")

    if _precipitacao_df.empty:
        log("Nenhum dado de precipitação foi processado.")
        return None, None

    _precipitacao_df["Ano"] = _precipitacao_df["Ano"].astype(int)

    # Converter o DataFrame para Series com o ano como índice
    precip_series = _precipitacao_df.set_index("Ano")["Precipitacao"]

    #log de gerando gráfico de precipitação
    log("Gerando gráfico de precipitação...")
    grafico_precipitacao_path = gerar_dados_precipitacao(
        precip_series,              # Series com o índice sendo o ano
        _ano_inicial,
        _ano_final,
        _NomeLocal,
        _graficos
    )

    return _precipitacao_df, grafico_precipitacao_path
