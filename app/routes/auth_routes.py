from flask import Blueprint, request, jsonify, session, redirect, url_for
from app.process.utils import obter_token_autenticacao, carregar_usuarios, salvar_usuarios
import hashlib
from app.globals import api_url

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/autenticar", methods=["POST"])
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

@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.pop("head", None)  # Remove o token da sessão
    session.pop("usuario", None)  # Remove o usuário da sessão
    session.pop("user_id", None)  # Remove o user_id da sessão
    return jsonify({"message": "Logout realizado com sucesso.", "redirect": url_for("main.acesso")})