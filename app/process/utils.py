import requests

def get_location_name(latitude, longitude):
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
        return f"{location_name.get('region', 'Desconhecido')} - {location_name.get('country', 'Desconhecido')}"
    except requests.exceptions.RequestException as e:
        return f"Erro de conexão com a API Nominatim: {e}"
    except Exception as e:
        return f"Erro ao processar a resposta da API Nominatim: {e}"