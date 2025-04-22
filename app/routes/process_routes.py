import shutil
from flask import Blueprint, request, jsonify, session, url_for
import threading
from app.models import processar_dados
from app.globals import stop_event
from app.dto.dtos import ProcessarDadosDTO
import os
import json

from app.process.utils import verificar_token_valido
from app.globals import api_url

process_bp = Blueprint("process_routes", __name__)

resultados_globais = {}

def baixar_dados_thread(latitude, longitude, cultura, estagio, thread_id, head, user_id):
    try:
        stop_event.clear()
        resultados_globais[thread_id] = {"logs": [], "resultados": None}

        def log(msg):
            print(msg)
            resultados_globais[thread_id]["logs"].append(msg)

        log("Iniciando processamento...")

        # Cria o DTO
        dto = ProcessarDadosDTO(
            latitude=latitude,
            longitude=longitude,
            cultura=cultura,
            estagio=estagio,
            head=head,
            user_id=user_id,
        )

        # Passa o DTO para a função processar_dados
        resultados = processar_dados(dto, log=log)

        # Verifica se o processo foi interrompido
        if stop_event.is_set():
            log("Processo interrompido pelo usuário. Nenhum dado será retornado.")
            return

        # Armazena os resultados apenas se o processo não foi interrompido
        resultados_globais[thread_id]["resultados"] = resultados

        # Salva os resultados em disco
        user_folder = os.path.join("app/static/data", user_id)
        os.makedirs(user_folder, exist_ok=True)
        resultados_path = os.path.join(user_folder, f"{user_id}_resultados.json")
        with open(resultados_path, "w") as f:
            json.dump(resultados.__dict__, f, default=str)  # Converte o DTO para JSON
    except Exception as e:
        if not stop_event.is_set():
            resultados_globais[thread_id]["logs"].append(f"Erro: {str(e)}")
            print(f"Erro ao baixar dados: {e}")

@process_bp.route("/iniciar-carregamento", methods=["POST"])
def iniciar_carregamento():
    if "head" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401

    head = session["head"]
    user_id = session["user_id"]

    # Verifica se o token ainda é válido
    if not verificar_token_valido(api_url, head):
        session.pop("head", None)  # Remove o token inválido da sessão
        return jsonify({"error": "Token expirado. Faça login novamente.", "redirect": url_for("main.acesso")}), 401

    try:
        # Extrai os dados do formulário
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")
        cultura = request.form.get("cultura")
        estagio = request.form.get("estagio")

        # Validação dos campos
        if not all([latitude, longitude, cultura, estagio]):
            return jsonify({"error": "Todos os campos (latitude, longitude, cultura, estagio) são obrigatórios"}), 400

        # Gera o thread_id
        thread_id = f"{latitude}_{longitude}_{cultura}_{estagio}"

        # Inicia a thread com o DTO
        thread = threading.Thread(
            target=baixar_dados_thread,
            args=(latitude, longitude, cultura, estagio, thread_id, head, user_id),
        )
        thread.start()

        # Retorna JSON com o ID da thread
        return jsonify({"thread_id": thread_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@process_bp.route("/parar-carregamento", methods=["POST"])
def parar_carregamento():
    if "head" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401

    head = session["head"]

    # Verifica se o token ainda é válido
    if not verificar_token_valido(api_url, head):
        session.pop("head", None)  # Remove o token inválido da sessão
        return jsonify({"error": "Token expirado. Faça login novamente.", "redirect": url_for("main.acesso")}), 401

    stop_event.set()  # Sinaliza para parar o processo

    # Caminho para a pasta de cache
    cache_dir = "app/static/data"
    parametros_cache_path = os.path.join(cache_dir, "parametros_cache.json")

    if os.path.exists(cache_dir):
        # Itera sobre os arquivos e pastas dentro de data
        for item in os.listdir(cache_dir):
            item_path = os.path.join(cache_dir, item)
            # Remove tudo, exceto o arquivo parametros_cache.json
            if item_path != parametros_cache_path:
                if os.path.isfile(item_path):
                    os.remove(item_path)
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)

    return jsonify({"status": "Carregamento interrompido e cache limpo, exceto o arquivo de parâmetros."})


@process_bp.route("/status", methods=["GET"])
def status():
    if "head" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401

    head = session["head"]

    # Verifica se o token ainda é válido
    if not verificar_token_valido(api_url, head):
        session.pop("head", None)  # Remove o token inválido da sessão
        return jsonify({"error": "Token expirado. Faça login novamente.", "redirect": url_for("main.acesso")}), 401

    thread_id = request.args.get("thread_id")
    logs = resultados_globais.get(thread_id, {}).get("logs", [])
    return jsonify({"logs": logs})
