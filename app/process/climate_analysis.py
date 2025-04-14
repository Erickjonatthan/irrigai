import numpy as np
import pandas as pd

kc_values = {
    "milho": {"inicial": 0.4, "medio": 1.25, "final": 0.5},
    "feijao": {"inicial": 0.55, "medio": 1.125, "final": 0.55},
    "tomate": {"inicial": 0.65, "medio": 1.175, "final": 0.75},
    "cana-de-acucar": {"inicial": 0.45, "medio": 1.275, "final": 0.925}
}

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

def recomendar_irrigacao(cultura, estagio, dados_ET, dados_PET):
    cultura = cultura.lower()
    estagio = estagio.lower()
    if cultura not in kc_values:
        raise ValueError(f"Cultura '{cultura}' não reconhecida. Escolha entre: {list(kc_values.keys())}")
    if estagio not in kc_values[cultura]:
        raise ValueError(f"Estágio '{estagio}' não reconhecido para a cultura '{cultura}'. Escolha entre: {list(kc_values[cultura].keys())}")
    kc = kc_values[cultura][estagio]
    etc = dados_PET * kc
    deficit = etc - dados_ET
    necessidade_irrigacao = deficit > 0
    recomendacoes = pd.DataFrame({
        "ET": dados_ET,
        "PET": dados_PET,
        "ETc": etc,
        "Déficit (mm)": deficit,
        "Necessita Irrigação": necessidade_irrigacao
    })
    return recomendacoes

def calcular_e_classificar_indices_aridez(_balanco, _ano_inicial, _ano_final):
    """
    Calcula os índices de aridez, realiza classificações e imprime os resultados.
    """
    # Cálculo de médias e classificações
    indice_aridez_medio = _balanco["Indice de Aridez UNEP"].mean()
    z = np.polyfit(_balanco["Ano"], _balanco["Indice de Aridez UNEP"], 1)
    p = np.poly1d(z)
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