from flask import Flask
def create_app():
    app = Flask(__name__)

    app.secret_key = '481ad1d7-57b6-46ea-9582-802a493ce787'

    # Importar e registrar as rotas
    from app.routes import main
    app.register_blueprint(main)

    return app