from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .models import db  # Certifique-se de importar `db`
from .routes import main

def create_app():
    app = Flask(__name__)

    # Configurações
    app.config.from_object('app.config.Config')  # Use from_object to load Config class

    # Inicialização do banco de dados e migrações
    db.init_app(app)  # Initialize the db with the app
    migrate = Migrate(app, db)

    # Registrar blueprints
    app.register_blueprint(main)

    return app
