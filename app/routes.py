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

        # Exemplo: substitua prints por log()
        log("Iniciando processamento...")
        resultados = processar_dados(latitude, longitude, cultura, estagio, log=log)
        resultados_globais[thread_id]["resultados"] = resultados
    except Exception as e:
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
    return render_template("resultado.html", **resultados)

@main.route("/parar-carregamento", methods=["POST"])
def parar_carregamento():
    stop_event.set()  # Sinaliza para parar o processo
    # Apaga o conteúdo da pasta cache_data
    cache_dir = "app/static/cache_data"
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        os.makedirs(cache_dir)
    return jsonify({"status": "Carregamento interrompido e cache limpo"})