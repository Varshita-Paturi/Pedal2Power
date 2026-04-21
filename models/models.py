from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sessions = db.relationship('PedalSession', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class PedalSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Integer, default=0)
    avg_rpm = db.Column(db.Float, default=0.0)
    avg_voltage = db.Column(db.Float, default=0.0)
    avg_current = db.Column(db.Float, default=0.0)
    energy_wh = db.Column(db.Float, default=0.0)
    calories_burned = db.Column(db.Float, default=0.0)
    co2_saved_g = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Latest raw values
    raw_rpm = db.Column(db.Float, default=0.0)
    raw_voltage = db.Column(db.Float, default=0.0)
    raw_current = db.Column(db.Float, default=0.0)
    power_w = db.Column(db.Float, default=0.0) # voltage * current
    
    # Internal tracking for averaging
    _rpm_sum = db.Column(db.Float, default=0.0)
    _voltage_sum = db.Column(db.Float, default=0.0)
    _current_sum = db.Column(db.Float, default=0.0)
    _data_points = db.Column(db.Integer, default=0)

    # Relationship to detailed data points
    data_points = db.relationship('SessionData', backref='session', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'avg_rpm': self.avg_rpm,
            'avg_voltage': self.avg_voltage,
            'avg_current': self.avg_current,
            'raw_rpm': self.raw_rpm,
            'raw_voltage': self.raw_voltage,
            'raw_current': self.raw_current,
            'power_w': self.power_w,
            'energy_wh': self.energy_wh,
            'calories_burned': self.calories_burned,
            'co2_saved_g': self.co2_saved_g
        }

class SessionData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('pedal_session.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Raw values
    raw_rpm = db.Column(db.Float)
    raw_voltage = db.Column(db.Float)
    raw_current = db.Column(db.Float)
    
    # Smoothed values (Moving Average)
    smoothed_rpm = db.Column(db.Float)
    smoothed_voltage = db.Column(db.Float)
    smoothed_current = db.Column(db.Float)
    
    power_w = db.Column(db.Float) # voltage * current (smoothed)
