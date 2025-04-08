import os
import matplotlib.pyplot as plt
import numpy as np

def PlotGrafico(data, name='', _NomeLocal='', _graficos=''):
    plt.title(f'{_NomeLocal}' + name)
    plt.imshow(data, cmap='jet_r', vmin=0, vmax=1)
    plt.colorbar(label='Aridez')
    mascara = np.where(data < 0.2, 0, np.nan)
    plt.imshow(mascara, cmap='gray', vmin=0, vmax=1, alpha=1)
    branco = np.where(data == 1, 0, np.nan)
    plt.imshow(branco, cmap='gray_r', vmin=0, vmax=1, alpha=1)
    plt.axis('off')
    output_path = os.path.join(_graficos, f"mapaIA{name}.png")
    plt.savefig(output_path, format="png")
    return output_path