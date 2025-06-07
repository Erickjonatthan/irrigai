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

def obter_caminhos_graficos(latitude, longitude, resolucao, ano_inicial, ano_final, user_id):
    """
    Gera o caminho para o mapa IA gerado, organizado por usuário.
    """
    # Define o diretório base para os resultados
    base_path = os.path.join("app", "static", "data", user_id, f"{latitude}_{longitude}_{resolucao}", "resultados")
    os.makedirs(base_path, exist_ok=True)  # Cria o diretório, se não existir

    # Define apenas o arquivo do mapa IA (única imagem disponível)
    mapa_IA_nome = f"mapaIA{ano_inicial}-{ano_final}.png"
    
    # Gera o caminho completo para o arquivo e normaliza para o formato de URL
    mapa_IA_path = os.path.join("data", user_id, f"{latitude}_{longitude}_{resolucao}", "resultados", mapa_IA_nome).replace("\\", "/")

    # Log para depuração
    print(f"Mapa IA salvo em: {mapa_IA_path}")

    return mapa_IA_path