import numpy as np
import pandas as pd

from app.process.graphics import PlotGrafico, mostraGraficoDoAno

def categoria_climatica(index):
    if index >= 0.65:
        return 'Humid'
    elif index >= 0.5:
        return 'Subhumid'
    elif index >= 0.2:
        return 'Semiarid'
    elif index >= 0.05:
        return 'Arid'
    else:
        return 'Hyperarid'

def risco_desertificacao(ai):
    if ai < 0.05:
        return "Above Very High (AVH)"
    elif 0.05 <= ai <= 0.20:
        return "Very High (VH)"
    elif 0.21 <= ai <= 0.50:
        return "High (H)"
    elif 0.51 <= ai <= 0.65:
        return "Moderate (M)"
    else:
        return "Low (L)"

def recomendar_irrigacao(cultura, estagio, dados_ET, dados_PET, dados_precipitacao, anos):
    """
    Fornece uma recomendação geral de irrigação com base nos dados anuais.
    """

    cultura = cultura.lower()
    estagio = estagio.lower()
    
    kc_values = {
        "milho": {"inicial": 0.4, "medio": 1.2, "final": 0.5},
        "feijao": {"inicial": 0.3, "medio": 1.1, "final": 0.6},
        "tomate": {"inicial": 0.6, "medio": 1.15, "final": 0.8},
        "cana-de-acucar": {"inicial": 0.5, "medio": 1.25, "final": 0.9}
    }

    if cultura not in kc_values or estagio not in kc_values[cultura]:
        raise ValueError("Cultura ou estágio inválido")

    kc = kc_values[cultura][estagio]

    # Criar DataFrame com os dados anuais
    df = pd.DataFrame({
        "Ano": anos,
        "ET": dados_ET,
        "PET": dados_PET,
        "Precipitacao": dados_precipitacao
    })

    deficits = []
    for _, linha in df.iterrows():
        pet = linha["PET"]
        prec = linha["Precipitacao"]
        etc = pet * kc
        deficit = etc - prec
        deficits.append(deficit)

    deficit_medio = np.mean(deficits)
    anos_irrigacao = sum(1 for d in deficits if d > 0)
    total_anos = len(deficits)
    ano_inicial = df["Ano"].iloc[0]
    ano_final = df["Ano"].iloc[-1]

    if anos_irrigacao > total_anos / 2:
        recomendacao = (
            f"Entre os anos de {ano_inicial} e {ano_final}, a cultura {cultura} no estágio {estagio} (Kc = {kc}) apresentou, em média, "
            f"um déficit hídrico de {deficit_medio:.1f} mm/ano. "
            f"Em {anos_irrigacao} de {total_anos} anos analisados, foi recomendado realizar irrigação. "
            f"💧 Recomenda-se atenção à irrigação nesse período."
        )
    else:
        recomendacao = (
            f"Entre os anos de {ano_inicial} e {ano_final}, a cultura {cultura} no estágio {estagio} (Kc = {kc}) apresentou, em média, "
            f"um déficit hídrico de {deficit_medio:.1f} mm/ano. "
            f"Na maioria dos anos, a irrigação provavelmente não foi necessária."
        )

    return [recomendacao]


def calcular_e_classificar_indices_aridez(_balanco, _ano_inicial, _ano_final):
    """
    Calcula os índices de aridez, realiza classificações e retorna uma lista com os resultados.
    """
    resultados = []
    
    # Cálculo de médias e classificações
    indice_aridez_medio = _balanco["Indice de Aridez UNEP"].mean()
    z = np.polyfit(_balanco["Ano"], _balanco["Indice de Aridez UNEP"], 1)
    p = np.poly1d(z)
    indice_aridez_tendencia = p(_balanco["Ano"]).mean()
    indice_aridez_atual = _balanco.iloc[-1]["Indice de Aridez UNEP"]

    resultados.append(
        f"Essa região está classificada atualmente como sendo uma região {indice_aridez_atual:.2f}, "
        f"o que lhe classifica como uma região {categoria_climatica(indice_aridez_atual)}"
    )
    
    resultados.append(
        f"Entre os anos de {_ano_inicial} e {_ano_final}, a região teve um índice médio de {indice_aridez_tendencia:.2f}, "
        f"o que lhe classifica como uma região {categoria_climatica(indice_aridez_tendencia)}"
    )
    
    resultados.append(
        f"A chance de desertificação da região está classificada como {risco_desertificacao(indice_aridez_tendencia)}"
    )

    # Comparação de índices de aridez
    _balanco["Aridez2"] = _balanco["ET"] / _balanco["PET"]
    indice_aridez2_medio = _balanco["Aridez2"].mean()
    
    resultados.append(
        f"Comparando os 2 índices para verificar equivalência {indice_aridez_medio:.2f} ~= {indice_aridez2_medio:.2f}"
    )

    return resultados

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
