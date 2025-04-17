from flask import Blueprint, jsonify, session
from app.process.utils import excluir_dados_usuario, carregar_usuarios, salvar_usuarios
import os
import shutil
from app.globals import api_url
user_bp = Blueprint("user_routes", __name__)

@user_bp.route("/apagar-conta", methods=["POST"])
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
