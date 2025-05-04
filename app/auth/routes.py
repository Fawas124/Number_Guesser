from flask import render_template, redirect, url_for, flash, request, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import OperationalError, IntegrityError
from app import db
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User
from app.auth import bp
import random
import time

@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('game.select_level'))
        flash('Invalid email or password', 'danger')
    return render_template('auth/login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Handle new user registration with retry logic for database locks"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check for existing user first (without db lock)
        existing_user = User.query.filter_by(username=form.username.data).first()
        existing_email = User.query.filter_by(email=form.email.data).first()
        
        if existing_user:
            flash('Username already taken', 'danger')
            return render_template('auth/register.html', form=form)
        if existing_email:
            flash('Email already registered', 'danger')
            return render_template('auth/register.html', form=form)

        # Configure retry parameters
        max_attempts = 5
        base_delay = 0.1  # seconds
        
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
                current_app.logger.warning(f'Database operation failed (attempt {attempt + 1}): {str(e)}')
                
                # Exponential backoff with jitter
                delay = min((base_delay * (2 ** attempt)) + random.uniform(0, 0.1), 2)
                time.sleep(delay)
                
            except IntegrityError:
                db.session.rollback()
                flash('Username or email already exists', 'danger')
                return render_template('auth/register.html', form=form)
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f'Registration error: {str(e)}')
                flash('Error creating account. Please try again.', 'danger')
                return render_template('auth/register.html', form=form)
        
        flash('Database is busy. Please try again later.', 'warning')
    
    return render_template('auth/register.html', title='Register', form=form)

@bp.route('/logout')
@login_required
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))