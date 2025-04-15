# filepath: app/routes.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
import threading
import shutil
import os
from app.models import processar_dados
from app.globals import stop_event  # Atualize a importação

main = Blueprint("main", __name__)

# Variável global para armazenar os resultados
resultados_globais = {}

def baixar_dados_thread(latitude, longitude, cultura, estagio, thread_id):
    try:
        stop_event.clear()
        resultados_globais[thread_id] = {"logs": [], "resultados": None}

        def log(msg):
            print(msg)
            resultados_globais[thread_id]["logs"].append(msg)

        log("Iniciando processamento...")
        resultados = processar_dados(latitude, longitude, cultura, estagio, log=log)

        # Verifica se o processo foi interrompido
        if stop_event.is_set():
            log("Processo interrompido pelo usuário. Nenhum dado será retornado.")
            return

        # Armazena os resultados apenas se o processo não foi interrompido
        resultados_globais[thread_id]["resultados"] = resultados
    except Exception as e:
        # Verifica se o erro não foi causado pela interrupção do usuário
        if not stop_event.is_set():
            resultados_globais[thread_id]["logs"].append(f"Erro: {str(e)}")
            print(f"Erro ao baixar dados: {e}")

@main.route("/status", methods=["GET"])
def status():
    thread_id = request.args.get("thread_id")
    logs = resultados_globais.get(thread_id, {}).get("logs", [])
    return jsonify({"logs": logs})


@main.route("/", methods=["GET"])
def index():
    return render_template("form.html")

@main.route("/iniciar-carregamento", methods=["POST"])
def iniciar_carregamento():
    latitude = float(request.form.get("latitude"))
    longitude = float(request.form.get("longitude"))
    cultura = request.form.get("cultura")
    estagio = request.form.get("estagio")

    thread_id = f"{latitude}_{longitude}_{cultura}_{estagio}"

    thread = threading.Thread(target=baixar_dados_thread, args=(latitude, longitude, cultura, estagio, thread_id))
    thread.start()

    # Retorna JSON com o ID da thread, sem esperar o processamento
    return jsonify({"thread_id": thread_id})

@main.route("/resultados", methods=["GET"])
def resultados():
    thread_id = request.args.get("thread_id")
    resultados = resultados_globais.get(thread_id, {})
    
    if not resultados:
        return "Nenhum resultado encontrado. Certifique-se de que o processamento foi concluído.", 400
    
    # Passe apenas o conteúdo de 'resultados' para o template
    return render_template("resultado.html", **resultados.get("resultados", {}))

@main.route("/parar-carregamento", methods=["POST"])
def parar_carregamento():
    stop_event.set()  # Sinaliza para parar o processo

    # Caminho para a pasta de cache
    cache_dir = "app/static/cache_data"
    parametros_cache_path = os.path.join(cache_dir, "parametros_cache.json")

    if os.path.exists(cache_dir):
        # Itera sobre os arquivos e pastas dentro de cache_data
        for item in os.listdir(cache_dir):
            item_path = os.path.join(cache_dir, item)
            # Remove tudo, exceto o arquivo parametros_cache.json
            if item_path != parametros_cache_path:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)

    return jsonify({"status": "Carregamento interrompido e cache limpo, exceto o arquivo de parâmetros."})