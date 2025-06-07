import os
import matplotlib
matplotlib.use('Agg')  # Define o backend não interativo
import matplotlib.pyplot as plt
import numpy as np
import rasterio

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


def gerar_dados_balanco_hidrico(df, nome_local):
    """
    Retorna dados do balanço hídrico para criação de gráfico no frontend.
    """
    if df.empty:
        return None

    anos = df["Ano"].astype(int).tolist()
    
    dados_grafico = {
        "titulo": f"Balanço Hídrico Anual - {nome_local}",
        "tipo": "bar",
        "dados": {
            "anos": anos,
            "series": [
                {
                    "nome": "ET (Evapotranspiração)",
                    "valores": df["ET"].tolist(),
                    "cor": "#2E86AB"
                },
                {
                    "nome": "PET (Evapotranspiração Potencial)", 
                    "valores": df["PET"].tolist(),
                    "cor": "#A23B72"
                },
                {
                    "nome": "Déficit Hídrico",
                    "valores": df["Deficit"].tolist(),
                    "cor": "#F18F01"
                }
            ]
        },
        "eixos": {
            "x": "Ano",
            "y": "Milímetros (mm)"
        }
    }
    
    print(f"Dados de balanço hídrico preparados para o frontend")
    return dados_grafico
def gerar_dados_precipitacao(series_precipitacao, ano_inicial, ano_final, nome_local):
    """
    Retorna dados de precipitação para criação de gráfico no frontend.
    """
    dados_grafico = {
        "titulo": f"Precipitação Média Anual - {nome_local} ({ano_inicial} a {ano_final})",
        "tipo": "bar",
        "dados": {
            "anos": series_precipitacao.index.tolist(),
            "series": [
                {
                    "nome": "Precipitação Média",
                    "valores": series_precipitacao.values.tolist(),
                    "cor": "#4682B4"
                }
            ]
        },
        "eixos": {
            "x": "Ano",
            "y": "Precipitação Média (mm)"
        }
    }

    print(f"Dados de precipitação preparados para o frontend")
    return dados_grafico

def mostraGraficoDoAno(ano, _inDir):
    """
    Mostra o gráfico de aridez para um ano específico.
    
    """

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

def calcular_indices_e_gerar_graficos(_balanco, _precipitacao_df, _ano_inicial, _ano_final, _graficos):
    # Calcula os índices de aridez
    _balanco["Indice de Aridez UNEP"] = _precipitacao_df["Precipitacao"] / _balanco["PET"]
    _balanco["Aridez"] = _precipitacao_df["Precipitacao"] / _balanco["ET"]

    # Retorna dados para gráfico de precipitação e evaporação
    dados_grafico = {
        "titulo": "Precipitação e Evaporação Anuais Médias",
        "tipo": "line", 
        "dados": {
            "anos": _balanco["Ano"].tolist(),
            "series": [
                {
                    "nome": "Precipitação",
                    "valores": _precipitacao_df["Precipitacao"].tolist(),
                    "cor": "#1f77b4"
                },
                {
                    "nome": "Evaporação",
                    "valores": _balanco["ET"].tolist(),
                    "cor": "#ff7f0e"
                }
            ]
        },
        "eixos": {
            "x": "Ano",
            "y": "Total Anual (mm)"
        }
    }

    return dados_grafico

def gerar_grafico_indice_aridez_unep(_balanco, _ano_inicial, _ano_final, _graficos):
    """
    Retorna dados do índice de aridez UNEP para criação de gráfico no frontend.
    """
    z = np.polyfit(_balanco["Ano"], _balanco["Indice de Aridez UNEP"], 1)
    p = np.poly1d(z)
    
    dados_grafico = {
        "titulo": "Índice de Aridez na Região Escolhida",
        "tipo": "line",
        "dados": {
            "anos": _balanco["Ano"].tolist(),
            "series": [
                {
                    "nome": "Índice de Aridez",
                    "valores": _balanco["Indice de Aridez UNEP"].tolist(),
                    "cor": "#2E8B57"
                },
                {
                    "nome": "Tendência",
                    "valores": p(_balanco["Ano"]).tolist(),
                    "cor": "#DC143C",
                    "tipo": "linha"
                }
            ]
        },
        "eixos": {
            "x": "Ano",
            "y": "Índice de Aridez"
        }
    }
    
    return dados_grafico

def calcular_e_gerar_grafico_rai(_balanco, _precipitacao_df, _graficos):
    """
    Calcula o índice de anomalia de chuva (RAI) e retorna dados para o frontend.
    """
    # Cálculo do índice de anomalia de chuva (RAI)
    media_precipitacao = _precipitacao_df["Precipitacao"].mean()
    desvio_precipitacao = _precipitacao_df["Precipitacao"].std()

    _balanco["RAI"] = _precipitacao_df["Precipitacao"].apply(
        lambda precipitacao: (precipitacao - media_precipitacao) / desvio_precipitacao * 100
    )

    dados_grafico = {
        "titulo": "Rain Anomaly Index (RAI)",
        "tipo": "bar",
        "dados": {
            "anos": _balanco["Ano"].tolist(),
            "series": [
                {
                    "nome": "RAI",
                    "valores": _balanco["RAI"].tolist(),
                    "cor": "#4169E1"
                }
            ]
        },
        "eixos": {
            "x": "Anos",
            "y": "RAI"
        }
    }
    
    print("Dados do gráfico RAI preparados para o frontend.")
    return dados_grafico
