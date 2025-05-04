from flask import Flask, render_template, redirect, url_for, flash, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_bootstrap import Bootstrap
from config import Config
from datetime import datetime
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import OperationalError
import time
import random

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
bootstrap = Bootstrap()

def create_app(config_class=Config):
    """Application factory function"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Configure SQLite specific settings if using SQLite
    if app.config['SQLALCHEMY_DATABASE_URI'].startswith('sqlite'):
        configure_sqlite()
    
    # Initialize extensions with app
    initialize_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register template filters and context processors
    register_template_utilities(app)
    
    # Setup database
    setup_database(app)
    
    return app

def configure_sqlite():
    """Configure SQLite-specific settings for better performance"""
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")  # Enable foreign key constraints
        cursor.execute("PRAGMA journal_mode=WAL")  # Better for concurrency
        cursor.execute("PRAGMA busy_timeout=5000")  # Wait up to 5 seconds if locked
        cursor.execute("PRAGMA synchronous=NORMAL")  # Good balance between safety and performance
        cursor.close()

def initialize_extensions(app):
    """Initialize Flask extensions with the application"""
    db.init_app(app)
    login_manager.init_app(app)
    bootstrap.init_app(app)

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

def register_template_utilities(app):
    """Register custom template filters and context processors"""
    @app.template_filter('datetimeformat')
    def datetimeformat(value, format='%Y-%m-%d %H:%M'):
        """Format datetime objects for templates"""
        if value is None:
            return ""
        return value.strftime(format)
    
    @app.teardown_request
    def shutdown_session(exception=None):
        """Ensure database session is removed after each request"""
        db.session.remove()

def setup_database(app):
    """Setup database and create tables if they don't exist"""
    with app.app_context():
        db.create_all()

# Import models after app creation to avoid circular imports
from app.models import User
from app.auth.forms import RegistrationForm

def register_routes(bp):
    """Register auth routes with the blueprint"""
    @bp.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))

        form = RegistrationForm()
        if form.validate_on_submit():
            # Check for existing user first (no transaction needed)
            if User.query.filter_by(username=form.username.data).first():
                flash('Username already taken', 'danger')
                return render_template('auth/register.html', form=form)
            if User.query.filter_by(email=form.email.data).first():
                flash('Email already registered', 'danger')
                return render_template('auth/register.html', form=form)

            # Configure retry parameters
            max_attempts = 5
            base_delay = 0.5  # seconds

            for attempt in range(max_attempts):
                try:
                    user = User(
                        username=form.username.data,
                        email=form.email.data
                    )
                    user.set_password(form.password.data)
                    db.session.add(user)
                    db.session.commit()
                    flash('Registration successful! Please login.', 'success')
                    return redirect(url_for('auth.login'))

                except OperationalError as e:
                    db.session.rollback()
                    current_app.logger.warning(f'Database locked (attempt {attempt + 1}): {str(e)}')
                    
                    # Exponential backoff with jitter
                    delay = min((base_delay * (2 ** attempt)) + random.uniform(0, 0.1), 5)
                    time.sleep(delay)

                except Exception as e:
                    db.session.rollback()
                    current_app.logger.error(f'Registration error: {str(e)}')
                    flash('Error creating account. Please try again.', 'danger')
                    return render_template('auth/register.html', form=form)

            flash('Database is busy. Please try again later.', 'warning')
        
        return render_template('auth/register.html', form=form)