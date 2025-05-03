from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    
    games_played = db.Column(db.Integer, default=0)
    games_won = db.Column(db.Integer, default=0)
    best_score = db.Column(db.Integer, default=0)
    
    # Relationships
    game_sessions = db.relationship(
        'GameSession', 
        back_populates='user',
        foreign_keys='GameSession.user_id',
        lazy='dynamic'
    )
    feedback = db.relationship('Feedback', backref='author', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def update_last_seen(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

class GameSession(db.Model):
    __tablename__ = 'game_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    level = db.Column(db.String(20), nullable=False)
    secret_number = db.Column(db.Integer, nullable=False)
    attempts_left = db.Column(db.Integer, nullable=False)
    
    current_range_low = db.Column(db.Integer, nullable=False)
    current_range_high = db.Column(db.Integer, nullable=False)
    
    completed = db.Column(db.Boolean, default=False)
    won = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship(
        'User', 
        back_populates='game_sessions',
        foreign_keys=[user_id]
    )
    guesses = db.relationship(
        'Guess',
        backref='game',
        lazy='dynamic',
        order_by='Guess.created_at.desc()'
    )
    
    def calculate_score(self):
        base_score = self.attempts_left * 10
        if self.level == 'medium':
            return base_score * 2
        elif self.level == 'hard':
            return base_score * 3
        return base_score

class Guess(db.Model):
    __tablename__ = 'guesses'
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'), nullable=False)
    guess_value = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))