import os
import matplotlib.pyplot as plt
import pandas as pd
import rasterio

def gerar_grafico_balanco_hidrico(df, ano_inicial, ano_final, nome_local, pasta_saida):
    """
    Gera gráfico de balanço hídrico com ET, PET e Déficit ao longo dos anos.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Grupos de barras
    largura = 0.25
    anos = df["Ano"].astype(int)
    x = range(len(anos))

    ax.bar([i - largura for i in x], df["ET"], width=largura, label="ET (Evapotranspiração)")
    ax.bar(x, df["PET"], width=largura, label="PET (Evapotranspiração Potencial)")
    ax.bar([i + largura for i in x], df["Deficit"], width=largura, label="Déficit Hídrico", color='red')

    # Estética
    ax.set_title(f"Balanço Hídrico Anual - {nome_local}", fontsize=14)
    ax.set_xlabel("Ano", fontsize=12)
    ax.set_ylabel("Milímetros (mm)", fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(anos)
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.5)

    # Salvar
    os.makedirs(pasta_saida, exist_ok=True)
    nome_arquivo = f"balanco_hidrico_{ano_inicial}_{ano_final}_{nome_local}.png".replace(" ", "_")
    caminho = os.path.join(pasta_saida, nome_arquivo)
    plt.tight_layout()
    plt.savefig(caminho)
    plt.close()

    print(f"Gráfico de balanço hídrico salvo em: {caminho}")
    return caminho

import matplotlib.pyplot as plt
import os

def gerar_grafico_precipitacao(series_precipitacao, ano_inicial, ano_final, nome_local, pasta_saida):
    """
    Gera e salva um gráfico de barras com a precipitação média anual de uma área.

    Parâmetros:
      - series_precipitacao: pandas.Series contendo a precipitação média por ano
                             (índice: ano, valor: mm)
      - ano_inicial: ano inicial do intervalo (int)
      - ano_final: ano final do intervalo (int)
      - nome_local: nome da localidade (str)
      - pasta_saida: caminho da pasta onde o gráfico será salvo (str)

    Retorna:
      - Caminho do arquivo gerado (str)
    """
    # Garante que a pasta de saída existe
    os.makedirs(pasta_saida, exist_ok=True)

    # Caminho do arquivo de saída
    nome_arquivo = f"grafico_precipitacao_{nome_local.replace(' ', '_')}_{ano_inicial}_{ano_final}.png"
    caminho_saida = os.path.join(pasta_saida, nome_arquivo)

    # Criar o gráfico
    plt.figure(figsize=(12, 6))
    series_precipitacao.plot(kind='bar', color='royalblue', edgecolor='black')

    plt.title(f"Precipitação Média Anual - {nome_local}\n({ano_inicial} a {ano_final})", fontsize=14)
    plt.xlabel("Ano", fontsize=12)
    plt.ylabel("Precipitação Média (mm)", fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    # Salvar o gráfico
    plt.savefig(caminho_saida)
    plt.close()

    print(f"Gráfico de precipitação salvo em: {caminho_saida}")
    return caminho_saida

def mostraGraficoDoAno(ano, _inDir):
    import os
    import rasterio

    # Caminho da subpasta do ano
    subpasta_ano = os.path.normpath(os.path.join(_inDir, f"BALANCO_HIDRICO_{ano}"))
    print(f"Verificando subpasta: {subpasta_ano}")
    
    if not os.path.exists(subpasta_ano):
        print(f"Subpasta não encontrada: {subpasta_ano}")
        return None  # Retorna None para indicar que o ano não foi processado

    # Inicializa as variáveis para os arquivos
    et_tif = None
    pet_tif = None

    # Procura os arquivos ET e PET na subpasta
    for f in os.listdir(subpasta_ano):
        if "_ET_500m" in f:
            et_tif = os.path.join(subpasta_ano, f)
        if "_PET_500m" in f:
            pet_tif = os.path.join(subpasta_ano, f)

    # Verifica se os arquivos foram encontrados
    if not et_tif or not pet_tif:
        print(f"Arquivos ET ou PET não encontrados na subpasta: {subpasta_ano}")
        return None

    # Abre os arquivos e calcula os dados de aridez
    with rasterio.open(et_tif) as et:
        et_data = et.read(1)
    with rasterio.open(pet_tif) as pet:
        pet_data = pet.read(1)

    # Calcula o índice de aridez
    arid_data = et_data / pet_data
    return arid_data