from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import Config
from datetime import datetime

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
bootstrap = Bootstrap()

def create_app(config_class=Config):
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register template filters
    register_template_filters(app)
    
    return app

def register_blueprints(app):
    """Register all application blueprints"""
    from app.auth import bp as auth_bp
    from app.main import bp as main_bp
    from app.game import bp as game_bp
    from app.errors import bp as errors_bp
    from app.leaderboard import bp as leaderboard_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(errors_bp)
    app.register_blueprint(leaderboard_bp, url_prefix='/leaderboard')

def register_template_filters(app):
    """Register custom template filters"""
    @app.template_filter('datetimeformat')
    def datetimeformat(value, format='%Y-%m-%d %H:%M'):
        """Format datetime objects for templates"""
        if value is None:
            return ""
        return value.strftime(format)

# Import models after app creation to avoid circular imports
from app import models