import os
from dotenv import load_dotenv

# Load environment variables from .env file
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '..', '.env'))

class Config:
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # Database configuration - supports both SQLite (development) and PostgreSQL (production)
    SQLALCHEMY_DATABASE_URI = "postgresql://flaskuser:Olamilekan@localhost:5432/number_guesser_db"
    
    # Database engine options - different settings for SQLite vs PostgreSQL
    if SQLALCHEMY_DATABASE_URI.startswith('sqlite'):
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_pre_ping": True,
            "pool_recycle": 3600,
            "connect_args": {
                "timeout": 30,  # Wait longer for SQLite locks
            }
        }
    else:
        # PostgreSQL connection pool settings
        SQLALCHEMY_ENGINE_OPTIONS = {
            'pool_size': 5,
            'max_overflow': 10,
            'pool_timeout': 30,
            'pool_recycle': 1800   # Recycle connections every 30 minutes for PostgreSQL
        }
    
    # Disable modification tracking
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Other common configurations
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    TESTING = False