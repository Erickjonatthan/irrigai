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
        location_name = data["address"]
        log(f"Localização obtida: {location_name.get('city', 'Desconhecido')} - {location_name.get('state', 'Desconhecido')} - {location_name.get('country', 'Desconhecido')}")
        return f"{location_name.get('region', 'Desconhecido')} - {location_name.get('country', 'Desconhecido')}"
    except requests.exceptions.RequestException as e:
        return f"Erro de conexão com a API Nominatim: {e}"
    except Exception as e:
        return f"Erro ao processar a resposta da API Nominatim: {e}"
    

def gerenciar_cache_parametros(inDir, parametros_atual, log=print):
    """
    Gerencia o cache de parâmetros, verificando se há alterações e limpando o cache se necessário.
    """
    # Caminho para o arquivo de cache de parâmetros
    parametros_cache_path = os.path.join(inDir, "parametros_cache.json")

    if os.path.exists(parametros_cache_path):
        with open(parametros_cache_path, "r") as f:
            parametros_salvos = json.load(f)

        # Comparar os parâmetros atuais com os salvos
        if parametros_atual != parametros_salvos:
            log("Parâmetros diferentes detectados. Limpando o cache...")
            # Apagar todo o conteúdo da pasta inDir
            for root, dirs, files in os.walk(inDir, topdown=False):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    os.rmdir(os.path.join(root, dir))
    else:
        log("Nenhum cache encontrado. Continuando com a execução...")

    # Salvar os parâmetros atuais no cache
    with open(parametros_cache_path, "w") as f:
        json.dump(parametros_atual, f)

def obter_token_autenticacao(api, _user, _password, log=print):
    """
    Obtém o token de autenticação da API usando as credenciais fornecidas.
    """
    try:
        token_response = requests.post(f'{api}login', auth=(_user, _password)).json()
        token = token_response['token']
        head = {'Authorization': f'Bearer {token}'}
        return head
    except Exception as e:
        log(f"Erro ao obter o token de autenticação: {e}")
        raise