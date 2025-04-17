from flask import Flask

def create_app():
    app = Flask(__name__)

    app.secret_key = '481ad1d7-57b6-46ea-9582-802a493ce787'

    # Importar e registrar os Blueprints das rotas
    from app.routes.main_routes import main_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.process_routes import process_bp
    from app.routes.user_routes import user_bp

    # Registrar os Blueprints
    app.register_blueprint(main_bp)  # Rota principal
    app.register_blueprint(auth_bp)  # Rota de autenticação
    app.register_blueprint(process_bp)  # Rota de processamento
    app.register_blueprint(user_bp)  # Rota de usuário

    return app