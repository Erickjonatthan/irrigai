import threading

# Variável global para controlar a execução
stop_event = threading.Event()
api_url = "https://appeears.earthdatacloud.nasa.gov/api/"