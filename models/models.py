from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    bookings = db.relationship('Booking', backref='user', lazy=True)
    matches_as_player1 = db.relationship('Match', backref='player1', lazy=True, foreign_keys='Match.player1_id')
    matches_as_player2 = db.relationship('Match', backref='player2', lazy=True, foreign_keys='Match.player2_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class TennisCourt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    available_hours = db.Column(db.String(200))  # Store as JSON string: {"monday": "9:00-21:00", ...}
    price_per_hour = db.Column(db.Float, nullable=False)
    
    # Relationships
    bookings = db.relationship('Booking', backref='court', lazy=True)
    matches = db.relationship('Match', backref='court', lazy=True)

    def __repr__(self):
        return f'<TennisCourt {self.name}>'

class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tennis_court_id = db.Column(db.Integer, db.ForeignKey('tennis_court.id'), nullable=False)
    booking_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # Duration in minutes
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Booking {self.id} - Court {self.tennis_court_id}>'

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    court_id = db.Column(db.Integer, db.ForeignKey('tennis_court.id'), nullable=False)
    player1_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    player2_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    match_time = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.Integer, default=60)  # Duration in minutes
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Match {self.id} - {self.player1_id} vs {self.player2_id}>'
