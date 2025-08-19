import os
from datetime import time
import re

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()

    # Configuração do banco de dados com fallback
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Fallback para SQLite local
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "app.db")}'

    SQLALCHEMY_TRACK_MODIFICATIONS = False


# Dias da semana disponíveis
WEEKDAYS = [
    ('monday', 'Segunda-feira'),
    ('tuesday', 'Terça-feira'),
    ('wednesday', 'Quarta-feira'),
    ('thursday', 'Quinta-feira'),
    ('friday', 'Sexta-feira'),
    ('saturday', 'Sábado'),
    ('sunday', 'Domingo')
]

# Horários padrão para o formulário
TIME_CHOICES = [
    (time(h, 0).strftime('%H:%M'), f"{h:02d}:00") for h in range(7, 23)
]