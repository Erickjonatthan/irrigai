import os

def criar_diretorios(inDir, user_id, latitude, longitude, area):
    """
    Cria os diretórios necessários para armazenar os dados do usuário.
    """
    base_dir = os.path.join(inDir, user_id)
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    local_data_name = os.path.join(base_dir, f"{latitude}_{longitude}_{area}")
    if not os.path.exists(local_data_name):
        os.makedirs(local_data_name)

    graficos_dir = os.path.join(local_data_name, "resultados")
    if not os.path.exists(graficos_dir):
        os.makedirs(graficos_dir)

    return local_data_name, graficos_dir

def obter_caminhos_graficos(latitude, longitude, resolucao, nome_local, ano_inicial, ano_final, user_id):
    """
    Gera os caminhos para os gráficos e mapas gerados, organizados por usuário.
    """
    # Define o diretório base para os resultados
    base_path = os.path.join("app", "static", "cache_data", user_id, f"{latitude}_{longitude}_{resolucao}", "resultados")
    os.makedirs(base_path, exist_ok=True)  # Cria o diretório, se não existir

    # Define os nomes dos arquivos de saída
    arquivos = {
        "grafico_precipitacao": f"grafico_precipitacao_{nome_local.replace(' ', '_')}_{ano_inicial}_{ano_final}.png",
        "grafico_rai": "RAI.png",
        "grafico_aridez": "IA.png",
        "mapa_IA": f"mapaIA{ano_inicial}-{ano_final}.png",
    }

    # Gera os caminhos completos para os arquivos e normaliza para o formato de URL
    caminhos = {key: os.path.join("cache_data", user_id, f"{latitude}_{longitude}_{resolucao}", "resultados", nome).replace("\\", "/")
                for key, nome in arquivos.items()}

    # Logs para depuração
    for descricao, caminho in caminhos.items():
        print(f"{descricao.replace('_', ' ').capitalize()} salvo em: {caminho}")

    return caminhos["grafico_precipitacao"], caminhos["grafico_rai"], caminhos["grafico_aridez"], caminhos["mapa_IA"]