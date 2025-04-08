# filepath: app/routes.py
import threading
import shutil
from flask import Blueprint, render_template, request, jsonify
import os
from app.models import processar_dados
from app.globals import stop_event  # Atualize a importação

main = Blueprint("main", __name__)

def baixar_dados_thread(latitude, longitude, cultura, estagio):
    try:
        stop_event.clear()  # Certifique-se de que o evento de parada está limpo
        resultados = processar_dados(latitude, longitude, cultura, estagio)  # Remova o stop_event daqui
        return resultados
    except Exception as e:
        print(f"Erro ao baixar dados: {e}")

@main.route("/", methods=["GET"])
def index():
    return render_template("form.html")

@main.route("/resultado", methods=["POST"])
def resultado():
    latitude = float(request.form.get("latitude"))
    longitude = float(request.form.get("longitude"))
    cultura = request.form.get("cultura")
    estagio = request.form.get("estagio")


    resultados = processar_dados(latitude, longitude, cultura, estagio)
    return render_template("resultado.html", **resultados)

@main.route("/iniciar-carregamento", methods=["POST"])
def iniciar_carregamento():
    latitude = float(request.form.get("latitude"))
    longitude = float(request.form.get("longitude"))
    cultura = request.form.get("cultura")
    estagio = request.form.get("estagio")

    # Inicia o processo em uma nova thread
    thread = threading.Thread(target=baixar_dados_thread, args=(latitude, longitude, cultura, estagio))
    thread.start()
    return jsonify({"status": "Carregamento iniciado"})

@main.route("/parar-carregamento", methods=["POST"])
def parar_carregamento():
    stop_event.set()  # Sinaliza para parar o processo
    # Apaga o conteúdo da pasta cache_data
    cache_dir = "app/static/cache_data"
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
        os.makedirs(cache_dir)
    return jsonify({"status": "Carregamento interrompido e cache limpo"})