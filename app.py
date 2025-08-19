from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import time, datetime
from config import Config, WEEKDAYS, TIME_CHOICES
import os

app = Flask(__name__)
app.config.from_object(Config)

# Garantir que o diretório instance existe
instance_path = os.path.join(os.path.dirname(__file__), 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Importar modelos após db ser inicializado
from models import User, Availability

# Funções auxiliares
def time_from_string(time_str):
    """Converte string HH:MM para objeto time"""
    try:
        return datetime.strptime(time_str, '%H:%M').time()
    except ValueError:
        return None

def calculate_common_availability():
    """Calcula a disponibilidade comum entre todos os usuários"""
    users = User.query.all()
    if not users:
        return []

    # Inicializa com a disponibilidade do primeiro usuário
    common_availability = {}

    for user in users:
        user_availability = {}
        for avail in user.availabilities:
            if avail.day_of_week not in user_availability:
                user_availability[avail.day_of_week] = []
            user_availability[avail.day_of_week].append((avail.start_time, avail.end_time))

        if not common_availability:
            # Primeiro usuário
            common_availability = user_availability
        else:
            # Intersecção com usuários anteriores
            new_common = {}
            for day, intervals in user_availability.items():
                if day in common_availability:
                    day_common = []
                    for common_start, common_end in common_availability[day]:
                        for user_start, user_end in intervals:
                            start = max(common_start, user_start)
                            end = min(common_end, user_end)
                            if start < end:
                                day_common.append((start, end))
                    if day_common:
                        new_common[day] = day_common
            common_availability = new_common

    return common_availability

# Rotas
@app.route('/')
def index():
    return render_template('index.html', weekdays=WEEKDAYS, time_choices=TIME_CHOICES)

@app.route('/submit', methods=['POST'])
def submit_availability():
    name = request.form.get('name')
    if not name:
        flash('Nome é obrigatório', 'error')
        return redirect(url_for('index'))

    # Verifica se usuário já existe
    user = User.query.filter_by(name=name).first()
    if user:
        # Remove disponibilidades existentes
        Availability.query.filter_by(user_id=user.id).delete()
    else:
        user = User(name=name)
        db.session.add(user)

    db.session.flush()  # Para obter o ID do usuário

    # Processa disponibilidades
    for day, day_name in WEEKDAYS:
        day_availabilities = []

        # Coleta todos os intervalos para este dia
        for i in range(3):  # Até 3 intervalos por dia
            start_key = f'{day}_start_{i}'
            end_key = f'{day}_end_{i}'

            start_str = request.form.get(start_key)
            end_str = request.form.get(end_key)

            if start_str and end_str:
                start_time = time_from_string(start_str)
                end_time = time_from_string(end_str)

                if not start_time or not end_time:
                    flash(f'Horário inválido para {day_name}', 'error')
                    continue

                if not Availability.validate_times(start_time, end_time):
                    flash(f'Horário final deve ser após horário inicial em {day_name}', 'error')
                    continue

                day_availabilities.append((start_time, end_time))

        # Verifica sobreposição para este dia
        for i, (start, end) in enumerate(day_availabilities):
            for j, (other_start, other_end) in enumerate(day_availabilities):
                if i != j and not (end <= other_start or start >= other_end):
                    flash(f'Intervalos sobrepostos detectados em {day_name}', 'error')
                    db.session.rollback()
                    return redirect(url_for('index'))

        # Salva disponibilidades válidas
        for start, end in day_availabilities:
            availability = Availability(
                user_id=user.id,
                day_of_week=day,
                start_time=start,
                end_time=end
            )
            db.session.add(availability)

    try:
        db.session.commit()
        flash('Disponibilidade salva com sucesso!', 'success')
        return redirect(url_for('success'))
    except Exception as e:
        db.session.rollback()
        flash('Erro ao salvar disponibilidade', 'error')
        return redirect(url_for('index'))

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/common')
def common_availability():
    common = calculate_common_availability()
    weekday_names = {day: name for day, name in WEEKDAYS}
    return render_template('common.html', common_availability=common, weekday_names=weekday_names)

@app.route('/reset')
def reset_database():
    """Rota para resetar o banco de dados (apenas para desenvolvimento)"""
    if app.config['DEBUG']:
        db.drop_all()
        db.create_all()
        flash('Banco de dados resetado', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False').lower() == 'true')

