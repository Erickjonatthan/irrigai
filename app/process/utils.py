import json
import os
import requests

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
    
def gerenciar_cache_parametros(inDir, parametros_atual, api, head, log=print):
    """
    Gerencia o cache de parâmetros, verificando se há alterações e limpando o cache se necessário.
    Também apaga as tasks realizadas no AppEEARS se os parâmetros forem diferentes.
    """
    # Caminho para o arquivo de cache de parâmetros
    parametros_cache_path = os.path.join(inDir, "parametros_cache.json")

    # Verifica se o cache existe
    if os.path.exists(parametros_cache_path):
        with open(parametros_cache_path, "r") as f:
            parametros_salvos = json.load(f)

        # Comparar os parâmetros atuais com os salvos
        if parametros_atual != parametros_salvos:
            log("Parâmetros diferentes detectados. Limpando o cache e excluindo tasks no AppEEARS...")

            # Apagar todo o conteúdo da pasta inDir
            for root, dirs, files in os.walk(inDir, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))

            # Excluir tasks no AppEEARS
            excluir_tasks_appeears(api, head, log)
    else:
        log("Nenhum cache encontrado. Continuando com a execução...")

    # Salvar os parâmetros atuais no cache
    with open(parametros_cache_path, "w") as f:
        json.dump(parametros_atual, f)


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
