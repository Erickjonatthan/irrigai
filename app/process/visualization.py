import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from app.globals import stop_event  # Atualize a importação
from app.process.data_processing import balanco_hidrico_ano
from app.process.graphics import gerar_grafico_balanco_hidrico, mostraGraficoDoAno

def PlotGrafico(data, name, _NomeLocal, _graficos):
    """
    Plota um gráfico de aridez com base nos dados fornecidos.
    """
    plt.title(f'{_NomeLocal}' + name)
    plt.imshow(data, cmap='jet_r', vmin=0, vmax=1)
    plt.colorbar(label='Aridez')
    mascara = np.where(data < 0.2, 0, np.nan)
    plt.imshow(mascara, cmap='gray', vmin=0, vmax=1, alpha=1)
    branco = np.where(data == 1, 0, np.nan)
    plt.imshow(branco, cmap='gray_r', vmin=0, vmax=1, alpha=1)
    plt.axis('off')
    
    plt.legend([], [], frameon=False)
    
    output_path = os.path.join(_graficos, f"mapaIA{name}.png")
    plt.savefig(output_path, format="png")
    return output_path

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
    
def calcular_e_gerar_grafico_rai(_balanco, _precipitacao_df, _graficos):
    """
    Calcula o índice de anomalia de chuva (RAI) e gera o gráfico correspondente.
    """
    # Cálculo do índice de anomalia de chuva (RAI)
    media_precipitacao = _precipitacao_df["Precipitacao"].mean()
    desvio_precipitacao = _precipitacao_df["Precipitacao"].std()

    _balanco["RAI"] = _precipitacao_df["Precipitacao"].apply(
        lambda precipitacao: (precipitacao - media_precipitacao) / desvio_precipitacao * 100
    )

    # Gráfico do índice de anomalia de chuva (RAI)
    _balanco.plot(kind='bar', x='Ano', y='RAI', title='Rain Anomaly Index (RAI)', xlabel='Anos', ylabel='RAI', color='blue')
    plt.savefig(os.path.join(_graficos, "RAI.png"), format="png")
    print("Gráfico do índice de anomalia de chuva (RAI) salvo com sucesso.")

def processar_balanco_hidrico(_ano_inicial, _ano_final, data_Json, _localdataName, api, head, _graficos, _NomeLocal):
    """
    Processa o balanço hídrico para os anos fornecidos e gera o gráfico correspondente.
    """
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

    return _balanco, grafico_balanco_hidrico_path