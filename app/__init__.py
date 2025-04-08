# filepath: app/__init__.py
from flask import Flask
import logging
logging.getLogger("werkzeug").setLevel(logging.ERROR)  # Ocultar logs do Flask
def create_app():
    app = Flask(__name__)

    # Importar e registrar as rotas
    from app.routes import main
    app.register_blueprint(main)

    return app