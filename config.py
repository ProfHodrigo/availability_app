import os
from datetime import time

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
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