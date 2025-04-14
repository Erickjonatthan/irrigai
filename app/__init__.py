from flask import Flask
def create_app():
    app = Flask(__name__)

    app.secret_key = 'sua_chave_secreta'

    # Importar e registrar as rotas
    from app.routes import main
    app.register_blueprint(main)

    return app