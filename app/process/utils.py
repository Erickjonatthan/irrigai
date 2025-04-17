import json
import os
import requests

USER_DB_PATH = "app/static/user_db.json"

def get_location_name(latitude, longitude, log=print):
    """
    Obtém o nome da localização a partir das coordenadas geográficas usando a API Nominatim.
    
    Parâmetros:
        latitude (float): Latitude da localização.
        longitude (float): Longitude da localização.    
    
    Retorna:
        str: Nome da localização ou mensagem de erro.
    """
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?format=json&lat={latitude}&lon={longitude}"
        headers = {"User-Agent": "PaleBlueDot-DuneDivers/1.0 (seu-email@example.com)"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception(f"Erro na API: {response.status_code} - {response.text}")
        data = response.json()
        if "address" not in data:
            raise Exception("Resposta da API não contém o campo 'address'")
        
        # Obtém os campos relevantes da resposta
        address = data["address"]
        cidade = address.get("city") or address.get("town") or address.get("village") or "Localização desconhecida"
        estado = address.get("state", "")
        log(f"Localização obtida: {cidade} - {estado}")
        
        return f"{cidade} - {estado}"
    except requests.exceptions.RequestException as e:
        return f"Erro de conexão com a API Nominatim: {e}"
    except Exception as e:
        return f"Erro ao processar a resposta da API Nominatim: {e}"
    
def excluir_dados_usuario(user_id, api, head, base_dir="app/static/cache_data", log=print):
    """
    Exclui todos os dados associados a um determinado user_id, incluindo a pasta de cache e tasks no AppEEARS.

    Parâmetros:
        user_id (str): O ID do usuário cujos dados devem ser excluídos.
        api (str): URL base da API do AppEEARS.
        head (dict): Cabeçalho de autenticação para a API.
        base_dir (str): O diretório base onde os dados do usuário estão armazenados.
        log (function): Função para registrar logs (padrão: print).
    """
    # Excluir tasks no AppEEARS
    log(f"Excluindo tasks do usuário {user_id} no AppEEARS...")
    excluir_tasks_appeears(api, head, log)

    # Caminho para a pasta do usuário
    user_dir = os.path.join(base_dir, user_id)

    # Verifica se a pasta do usuário existe
    if os.path.exists(user_dir):
        log(f"Excluindo dados do usuário: {user_id}")
        # Remove todos os arquivos e subdiretórios dentro da pasta do usuário
        for root, dirs, files in os.walk(user_dir, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for dir in dirs:
                os.rmdir(os.path.join(root, dir))
        # Remove a pasta do usuário
        os.rmdir(user_dir)
        log(f"Dados do usuário {user_id} excluídos com sucesso.")
    else:
        log(f"Nenhum dado encontrado para o usuário: {user_id}")
def excluir_tasks_appeears(api, head, log=print):
    """
    Exclui apenas as tasks realizadas no AppEEARS cujo nome começa com 'BALANCO_HIDRICO_'.
    """
    try:
        # Obter a lista de tasks
        response = requests.get(f"{api}task", headers=head)
        response.raise_for_status()
        tasks = response.json()

        # Iterar sobre as tasks e excluir apenas as que começam com 'BALANCO_HIDRICO_'
        for task in tasks:
            task_id = task.get("task_id")
            task_name = task.get("task_name", "")  # Supondo que o nome da task esteja no campo 'task_name'
            if task_id and task_name.startswith("BALANCO_HIDRICO_"):
                delete_response = requests.delete(f"{api}task/{task_id}", headers=head)
                delete_response.raise_for_status()
                log(f"Task '{task_name}' excluída com sucesso.")
    except requests.RequestException as e:
        log(f"Erro ao excluir tasks no AppEEARS: {e}")


# Função para obter o token de autenticação
def obter_token_autenticacao(api, _user, _password):
    """
    Obtém o token de autenticação da API usando as credenciais fornecidas.
    """
    try:
        token_response = requests.post(f'{api}login', auth=(_user, _password)).json()
        token = token_response['token']
        head = {'Authorization': f'Bearer {token}'}
        return head
    except Exception as e:
        print(f"Erro ao obter o token de autenticação: {e}")
        raise

def verificar_token_valido(api,head):
    """
    Faz uma requisição de teste à API para verificar se o token é válido.
    """
    try:
        response = requests.get(api, headers=head)
        return response.status_code == 200  # Retorna True se o token for válido
    except Exception:
        return False

def carregar_usuarios():
    """Carrega o banco de dados de usuários do arquivo JSON."""
    if os.path.exists(USER_DB_PATH):
        with open(USER_DB_PATH, "r") as file:
            return json.load(file)
    return {}

def salvar_usuarios(usuarios):
    """Salva o banco de dados de usuários no arquivo JSON."""
    with open(USER_DB_PATH, "w") as file:
        json.dump(usuarios, file, indent=4)
