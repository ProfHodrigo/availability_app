from app import db
from datetime import datetime, time

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    availabilities = db.relationship('Availability', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.name}>'

class Availability(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day_of_week = db.Column(db.String(20), nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    def __repr__(self):
        return f'<Availability {self.day_of_week} {self.start_time}-{self.end_time}>'

    @staticmethod
    def validate_times(start_time, end_time):
        """Valida se start_time < end_time"""
        return start_time < end_time

    @staticmethod
    def check_overlap(existing_availabilities, new_start, new_end):
        """Verifica se há sobreposição com disponibilidades existentes"""
        for avail in existing_availabilities:
            if not (new_end <= avail.start_time or new_start >= avail.end_time):
                return True
        return False