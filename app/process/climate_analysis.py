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