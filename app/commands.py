import click
from flask import current_app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def register_commands(app):
    @app.cli.command()
    def create_admin():
        """Create the admin user"""
        from .models import User  # Import inside function to avoid circular imports
        
        with app.app_context():
            if not User.query.filter_by(username='admin').first():
                admin = User(
                    username='admin',
                    email='fawassurajudeen16@gmail.com',
                    is_admin=True
                )
                admin.set_password('Olamilekan123')
                db.session.add(admin)
                db.session.commit()
                click.echo('Admin user created successfully!')
            else:
                click.echo('Admin user already exists')