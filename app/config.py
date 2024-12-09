import os
from secrets import token_hex

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', token_hex(16))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 10  # Ajustar conforme necessário
    SQLALCHEMY_POOL_RECYCLE = 3600  # Ajustar conforme necessário