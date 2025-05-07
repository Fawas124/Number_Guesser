from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager

class Setting(db.Model):
    """Application settings model for game levels"""
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.String(20), unique=True)  # 'easy', 'medium', 'hard'
    range_low = db.Column(db.Integer, default=1)
    range_high = db.Column(db.Integer, default=100)
    max_attempts = db.Column(db.Integer, default=10)
    score_multiplier = db.Column(db.Float, default=1.0)
    is_active = db.Column(db.Boolean, default=True)
    
    @classmethod
    def get_settings(cls, level):
        """Get or create settings for a specific level"""
        setting = cls.query.filter_by(level=level).first()
        if not setting:
            # Create with default values
            defaults = {
                'easy': {'range_high': 100, 'max_attempts': 10, 'score_multiplier': 1.0},
                'medium': {'range_high': 200, 'max_attempts': 7, 'score_multiplier': 1.5},
                'hard': {'range_high': 300, 'max_attempts': 5, 'score_multiplier': 2.0}
            }
            
            setting = cls(
                level=level,
                range_low=1,
                range_high=defaults.get(level, {}).get('range_high', 100),
                max_attempts=defaults.get(level, {}).get('max_attempts', 10),
                score_multiplier=defaults.get(level, {}).get('score_multiplier', 1.0)
            )
            db.session.add(setting)
            db.session.commit()
        return setting

    def update_ranges(self, min_val, max_val, attempts):
        """Validate and update number ranges"""
        try:
            min_val = int(min_val)
            max_val = int(max_val)
            attempts = int(attempts)
            
            if min_val >= max_val:
                raise ValueError("Minimum must be less than maximum")
            if attempts <= 0:
                raise ValueError("Attempts must be positive")
            
            self.range_low = min_val
            self.range_high = max_val
            self.max_attempts = attempts
            return True
            
        except ValueError as e:
            raise ValueError(f"Invalid input: {str(e)}")

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
    legacy_games = db.relationship('Game', back_populates='player', lazy='dynamic')
    
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
        db.session.commit()

class GameSession(db.Model):
    """Game session model"""
    __tablename__ = 'game_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    level = db.Column(db.String(20), nullable=False)
    secret_number = db.Column(db.Integer)
    attempts_left = db.Column(db.Integer, nullable=False)
    
    current_range_low = db.Column(db.Integer)
    current_range_high = db.Column(db.Integer)
    
    completed = db.Column(db.Boolean, default=False)
    won = db.Column(db.Boolean, default=False)
    score = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', back_populates='game_sessions')
    guesses = db.relationship(
        'Guess',
        backref='game',
        lazy='dynamic',
        order_by='Guess.created_at.desc()'
    )
    
    def calculate_score(self):
        """Calculate score based on level and attempts left"""
        settings = Setting.get_settings(self.level)
        if not settings:
            return 0
            
        base_score = self.attempts_left * 10
        return int(base_score * settings.score_multiplier)

class Guess(db.Model):
    """Game guess model"""
    __tablename__ = 'guesses'
    
    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('game_sessions.id'), nullable=False)
    guess_value = db.Column(db.String(100), nullable=False)
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
    """Word model for word guessing game"""
    __tablename__ = 'words'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100), nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)  # 1-3 for easy-medium-hard
    max_attempts = db.Column(db.Integer, default=10)
    is_active = db.Column(db.Boolean, default=True)
    
    @property
    def difficulty_name(self):
        """Get difficulty as human-readable name"""
        return {1: 'easy', 2: 'medium', 3: 'hard'}.get(self.difficulty, 'unknown')

class Game(db.Model):
    """Legacy game model (for backward compatibility)"""
    __tablename__ = 'games'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    level = db.Column(db.String(50))
    won = db.Column(db.Boolean)
    score = db.Column(db.Integer)
    played_at = db.Column(db.DateTime, default=datetime.utcnow)
    attempts = db.Column(db.Integer)
    
    # Relationship
    player = db.relationship('User', back_populates='legacy_games')

@login_manager.user_loader
def load_user(user_id):
    """Flask-Login user loader callback"""
    return User.query.get(int(user_id))