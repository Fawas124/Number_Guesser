from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class Setting(db.Model):
    """Application settings model"""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    app_name = db.Column(db.String(100), default='Number Guesser', nullable=False)
    maintenance_mode = db.Column(db.Boolean, default=False, nullable=False)
    max_attempts_easy = db.Column(db.Integer, default=10, nullable=False)
    max_attempts_medium = db.Column(db.Integer, default=7, nullable=False)
    max_attempts_hard = db.Column(db.Integer, default=5, nullable=False)
    score_multiplier_easy = db.Column(db.Float, default=1.0, nullable=False)
    score_multiplier_medium = db.Column(db.Float, default=1.5, nullable=False)
    score_multiplier_hard = db.Column(db.Float, default=2.0, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_settings(cls):
        """Get or create application settings"""
        settings = cls.query.first()
        if not settings:
            settings = cls()
            db.session.add(settings)
            db.session.commit()
        return settings

class User(UserMixin, db.Model):
    """User account model"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Game statistics
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
        """Create hashed password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_seen(self):
        """Update last seen timestamp"""
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        try:
            db.session.commit()
        except:
            db.session.rollback()
            raise

class GameSession(db.Model):
    """Game session model"""
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
        """Calculate score based on level and attempts left"""
        settings = Setting.get_settings()
        base_score = self.attempts_left * 10
        
        if self.level == 'easy':
            return int(base_score * settings.score_multiplier_easy)
        elif self.level == 'medium':
            return int(base_score * settings.score_multiplier_medium)
        elif self.level == 'hard':
            return int(base_score * settings.score_multiplier_hard)
        return base_score

class Guess(db.Model):
    """Game guess model"""
    __tablename__ = 'guesses'
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'), nullable=False)
    guess_value = db.Column(db.Integer, nullable=False)
    result = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Feedback(db.Model):
    """User feedback model"""
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_resolved = db.Column(db.Boolean, default=False)

class Word(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100))  # Stores range like "1-100"
    difficulty = db.Column(db.Integer) # 1-3 for easy-medium-hard
    max_attempts = db.Column(db.Integer)  # Add this line
    is_active = db.Column(db.Boolean, default=True)
    
    @property
    def difficulty_name(self):
        """Get difficulty as human-readable name"""
        return {1: 'easy', 2: 'medium', 3: 'hard'}.get(self.difficulty, 'unknown')

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader callback"""
    return User.query.get(int(user_id))