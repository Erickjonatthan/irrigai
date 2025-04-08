import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio

def gerar_grafico_precipitacao(_dados, _ano_inicial, _ano_final, _NomeLocal, _graficos):
    """
    Gera e salva o gráfico de precipitação anual.
    """
    plt.figure(figsize=(10, 5))
    plt.plot(_dados["Ano"], _dados["Precipitacao"])
    plt.xticks(np.arange(_ano_inicial, _ano_final + 1, 1), [str(i) for i in range(_ano_inicial, _ano_final + 1)], rotation=45)
    plt.xlabel('Anos')
    plt.ylabel('Precipitação (mm)')
    plt.title(f'Média anual de precipitação em {_NomeLocal}')
    
    # Salvar o gráfico
    grafico_path = os.path.join(_graficos, "precipitacao.png")
    plt.savefig(grafico_path, format="png")
    plt.close()  # Fecha a figura para liberar memória

    return grafico_path

def mostraGraficoDoAno(ano, _appEEARsDir, _arquivos):
    for f in _arquivos:
        nome = f#_arquivos[f]
        if "_ET_5" in nome and f"doy{ano}" in nome:
            et_tif = nome
        if "_PET_5" in nome and f"doy{ano}" in nome:
            pet_tif = nome
    et_tif = _appEEARsDir+"/"+et_tif
    pet_tif = _appEEARsDir+"/"+pet_tif
    with rasterio.open(et_tif) as et:
      et_data = et.read(1) 
    with rasterio.open(pet_tif) as pet:
      pet_data = pet.read(1) 
    arid_data = et_data / pet_data
    return arid_data
