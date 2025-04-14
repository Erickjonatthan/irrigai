import numpy as np

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
    Fornece recomendações de irrigação em linguagem acessível com base nos dados médios mensais.
    """
    import pandas as pd

    # Prints para depuração
    print("=== Depuração: Dados de Entrada ===")
    print(f"Dados ET recebidos:\n{dados_ET}")
    print(f"Dados PET recebidos:\n{dados_PET}")
    print(f"Dados de precipitação recebidos:\n{dados_precipitacao}")
    print(f"Anos recebidos:\n{anos}")

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
    print(f"Kc selecionado para {cultura} no estágio {estagio}: {kc}")

    # Criar DataFrame com os dados
    df = pd.DataFrame({
        "Ano": anos,
        "ET": dados_ET,
        "PET": dados_PET,
        "Precipitacao": dados_precipitacao
    })

    # Adicionar coluna de mês
    df['Mes'] = (df.index % 12) + 1

    print("=== DataFrame Inicial ===")
    print(df)

    # Calcular a média mensal ao longo de todos os anos
    resumo = df.groupby('Mes').mean()
    print("=== Resumo Mensal (Média) ===")
    print(resumo)

    mensagens = []
    nomes_meses = {
        1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho",
        7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
    }

    for mes, linha in resumo.iterrows():
        pet = linha["PET"]
        et = linha["ET"]
        prec = linha["Precipitacao"]
        etc = pet * kc
        deficit = etc - prec

        # Print dos cálculos intermediários
        print(f"Mês: {nomes_meses[mes]}, PET: {pet}, ET: {et}, Precipitação: {prec}, ETC: {etc}, Déficit: {deficit}")

        if deficit > 0:
            msg = (
                f"📅 {nomes_meses[mes]} (média de {anos.min()} a {anos.max()}): Sua PET média foi de {pet:.1f} mm. "
                f"Como sua cultura é {cultura} no estágio {estagio} (Kc = {kc}), "
                f"a planta precisa de aproximadamente {etc:.1f} mm. "
                f"A precipitação foi de {prec:.1f} mm, resultando em um déficit de {deficit:.1f} mm. "
                f"💧 Recomendado realizar irrigação nesse mês."
            )
        else:
            msg = (
                f"📅 {nomes_meses[mes]} (média de {anos.min()} a {anos.max()}): PET média de {pet:.1f} mm e precipitação de {prec:.1f} mm. "
                f"Não há déficit hídrico significativo — irrigação provavelmente não necessária."
            )
        mensagens.append(msg)

    return mensagens

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