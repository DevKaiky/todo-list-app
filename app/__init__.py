from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .models import models  # Import models from models.py (assuming you have models defined there)
from .routes import main

def create_app():
    app = Flask(__name__)

    # Configurações
    app.config.from_pyfile('config.py')

    # Inicialização do banco de dados e migrações
    db = SQLAlchemy(app)  # Create an instance of SQLAlchemy
    migrate = Migrate(app, db)  # Use the created `db` instance for migrations

    # Registrar blueprints
    app.register_blueprint(main)

    return app
