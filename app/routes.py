# filepath: app/routes.py
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
import threading
import shutil
import os
import hashlib
from app.models import processar_dados
from app.globals import stop_event
from app.globals import api_url
from app.process.utils import obter_token_autenticacao, verificar_token_valido, carregar_usuarios, salvar_usuarios, excluir_dados_usuario
from app.dto.dtos import ResultadosDTO
from app.dto.dtos import ProcessarDadosDTO


main = Blueprint("main", __name__)

# Variável global para armazenar os resultados
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
    except Exception as e:
        # Verifica se o erro não foi causado pela interrupção do usuário
        if not stop_event.is_set():
            resultados_globais[thread_id]["logs"].append(f"Erro: {str(e)}")
            print(f"Erro ao baixar dados: {e}")

@main.route("/status", methods=["GET"])
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


# Rota para a página inicial
@main.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# Rota para a página de acesso
@main.route("/acesso", methods=["GET"])
def acesso():
    # Verifica se o usuário já está autenticado
    if "head" in session:
        # Redireciona para o formulário se já estiver logado
        return redirect(url_for("main.form"))
    return render_template("acesso.html")

# Rota para autenticação
@main.route("/autenticar", methods=["POST"])
def autenticar():
    data = request.get_json()  # Recebe o JSON do frontend
    usuario = data.get("usuario")
    senha = data.get("senha")

    if not usuario or not senha:
        return jsonify({"error": "Usuário e senha são obrigatórios"}), 400

    try:
        # Gera o token de autenticação
        head = obter_token_autenticacao(api_url, usuario, senha)

        # Carrega o banco de dados de usuários
        usuarios = carregar_usuarios()

        # Verifica se o usuário já possui um user_id
        if usuario in usuarios:
            user_id = usuarios[usuario]
        else:
            # Gera um ID único para o usuário usando um hash do nome de usuário
            user_id = hashlib.md5(usuario.encode()).hexdigest()
            usuarios[usuario] = user_id
            salvar_usuarios(usuarios)  # Salva o novo usuário no banco de dados

        # Armazena o cabeçalho e o user_id na sessão
        session["head"] = head
        session["usuario"] = usuario
        session["user_id"] = user_id

        return jsonify({"message": "Autenticação bem-sucedida", "redirect": url_for("main.form")})
    except Exception as e:
        return jsonify({"error": str(e)}), 401

@main.route("/form", methods=["GET"])
def form():
    if "head" not in session:
        return redirect(url_for("main.acesso"))  # Redireciona para a página de acesso se não estiver autenticado

    head = session["head"]
    usuario = session["usuario"]

    # Verifica se o token ainda é válido
    if not verificar_token_valido(api_url, head):
        session.pop("head", None)  # Remove o token inválido da sessão
        return redirect(url_for("main.acesso"))  # Redireciona para a página de acesso

    # Passa o nome do usuário para o template
    return render_template("form.html", usuario=usuario)

@main.route("/iniciar-carregamento", methods=["POST"])
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


@main.route("/painel", methods=["GET"])
def resultados():
    if "head" not in session:
        return redirect(url_for("main.acesso"))  # Redireciona para a página de acesso se não estiver autenticado

    head = session["head"]

    # Verifica se o token ainda é válido
    if not verificar_token_valido(api_url, head):
        session.pop("head", None)  # Remove o token inválido da sessão
        return redirect(url_for("main.acesso"))  # Redireciona para a página de acesso

    thread_id = request.args.get("thread_id")
    resultados = resultados_globais.get(thread_id, {}).get("resultados")

    if not resultados:
        return render_template(
            "error.html", 
            mensagem="Nenhum resultado encontrado. Certifique-se de que o processamento foi concluído."
        )

    # Verifica se os resultados são do tipo ResultadosDTO
    if isinstance(resultados, ResultadosDTO):
        # Passa o objeto resultados diretamente para o template
        return render_template("painel.html", resultados=resultados)
    else:
        return render_template(
            "error.html", 
            mensagem="Formato de resultados inválido."
        )


@main.route("/parar-carregamento", methods=["POST"])
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


@main.route("/apagar-conta", methods=["POST"])
def apagar_conta():
    if "usuario" not in session:
        return jsonify({"error": "Usuário não autenticado"}), 401

    usuario = session["usuario"]
    user_id = session.get("user_id")
    head = session.get("head")

    # Carrega o banco de dados de usuários
    usuarios = carregar_usuarios()

    # Remove o usuário do banco de dados
    if usuario in usuarios:
        del usuarios[usuario]
        salvar_usuarios(usuarios)

    # Exclui os dados do usuário (pasta de cache e tasks no AppEEARS)
    if user_id and head:
        excluir_dados_usuario(user_id, api_url, head)

    # Limpa a sessão
    session.pop("head", None)
    session.pop("usuario", None)
    session.pop("user_id", None)

    return jsonify({"message": "Conta apagada com sucesso."})