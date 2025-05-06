from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import current_user, login_required
from functools import wraps
from datetime import datetime, timedelta
from app import db
from app.models import User, GameSession, Feedback, Word
from app.admin import bp
from app.admin.forms import (AdminEditUserForm, LevelSettingsForm, 
                           InstructionsForm, SystemSettingsForm, EditWordForm)
from app.models import Setting

# Constants for game levels
LEVEL_SETTINGS = {
    'easy': {'min': 1, 'max': 50, 'attempts': 10, 'multiplier': 1.0},
    'medium': {'min': 1, 'max': 100, 'attempts': 7, 'multiplier': 1.5},
    'hard': {'min': 1, 'max': 200, 'attempts': 5, 'multiplier': 2.0}
}

def admin_required(f):
    """Decorator to ensure only admins can access the route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)  # Forbidden access
        return f(*args, **kwargs)
    return decorated_function

# Apply admin requirement to all admin routes
@bp.before_request
@login_required
@admin_required
def require_admin():
    pass  # Just forces the admin requirement check

@bp.route('/')
def dashboard():
    """Admin dashboard with statistics"""
    stats = {
        'total_users': User.query.count(),
        'total_games': GameSession.query.count(),
        'active_games': GameSession.query.filter_by(completed=False).count(),
        'total_feedback': Feedback.query.count(),
        'new_users': User.query.filter(
            User.created_at > datetime.utcnow() - timedelta(days=7)
        ).count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'game_levels': LEVEL_SETTINGS,
        'total_words': Word.query.count()
    }
    return render_template('admin/dashboard.html', stats=stats)

# User Management Routes
@bp.route('/users')
def manage_users():
    """Manage users with pagination"""
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.username).paginate(
        page=page, 
        per_page=10,
        error_out=False
    )
    return render_template('admin/users.html', users=users)

@bp.route('/user/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    
    # Pass original values to the form
    form = AdminEditUserForm(
        original_username=user.username,
        original_email=user.email,
        obj=user  # Pre-populates form with user data
    )

    if form.validate_on_submit():
        form.populate_obj(user)  # Update user with form data
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.manage_users'))

    return render_template('admin/edit_user.html', form=form, user=user)

@bp.route('/toggle_user/<int:user_id>', methods=['POST'])
def toggle_user(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    try:
        db.session.commit()
        status = 'activated' if user.is_active else 'deactivated'
        flash(f'User {status} successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error toggling user status: {str(e)}')
        flash('Error updating user status', 'danger')
    return redirect(url_for('admin.manage_users'))

@bp.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    """Delete user account"""
    if current_user.id == user_id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    user = User.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting user: {str(e)}')
        flash('Error deleting user', 'danger')
    return redirect(url_for('admin.manage_users'))

# Game Management Routes
@bp.route('/games')
def manage_games():
    """View all game sessions with pagination"""
    page = request.args.get('page', 1, type=int)
    games = GameSession.query.order_by(
        GameSession.created_at.desc()
    ).paginate(
        page=page, 
        per_page=10,
        error_out=False
    )
    return render_template('admin/games.html', games=games)

@bp.route('/game/<int:game_id>')
def view_game(game_id):
    """View detailed game session"""
    game = GameSession.query.get_or_404(game_id)
    return render_template('admin/view_game.html', game=game)

# Feedback Management Routes
@bp.route('/feedback')
def manage_feedback():
    """Manage user feedback"""
    page = request.args.get('page', 1, type=int)
    feedback = Feedback.query.order_by(
        Feedback.created_at.desc()
    ).paginate(
        page=page, 
        per_page=10,
        error_out=False
    )
    return render_template('admin/feedback.html', feedback=feedback)

@bp.route('/delete_feedback/<int:feedback_id>', methods=['POST'])
def delete_feedback(feedback_id):
    """Delete feedback entry"""
    feedback = Feedback.query.get_or_404(feedback_id)
    try:
        db.session.delete(feedback)
        db.session.commit()
        flash('Feedback deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting feedback: {str(e)}')
        flash('Error deleting feedback', 'danger')
    return redirect(url_for('admin.manage_feedback'))

# Content Management Routes
@bp.route('/manage-content')
def manage_content():
    search = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    
    query = Word.query
    if search:
        query = query.filter(Word.text.ilike(f'%{search}%'))
    
    words = query.paginate(page=page, per_page=10)
    
    return render_template('admin/manage_content.html',
                         words=words, search=search)

@bp.route('/content/levels/<level>', methods=['GET', 'POST'])
def edit_level(level):
    """Edit game level settings"""
    if level not in LEVEL_SETTINGS:
        abort(404)
    
    form = LevelSettingsForm()
    if form.validate_on_submit():
        try:
            LEVEL_SETTINGS[level] = {
                'min': form.min_value.data,
                'max': form.max_value.data,
                'attempts': form.attempts.data,
                'multiplier': form.multiplier.data
            }
            flash(f'{level.capitalize()} level settings updated', 'success')
            return redirect(url_for('admin.manage_content'))
        except Exception as e:
            current_app.logger.error(f'Error updating level settings: {str(e)}')
            flash('Error updating level settings', 'danger')
    
    # Pre-populate form with current values
    form.min_value.data = LEVEL_SETTINGS[level]['min']
    form.max_value.data = LEVEL_SETTINGS[level]['max']
    form.attempts.data = LEVEL_SETTINGS[level]['attempts']
    form.multiplier.data = LEVEL_SETTINGS[level]['multiplier']
    
    return render_template('admin/edit_level.html', level=level, form=form)

@bp.route('/content/update-instructions', methods=['POST'])
def update_instructions():
    """Update game instructions"""
    form = InstructionsForm()
    if form.validate_on_submit():
        try:
            # Save instructions to database or config file
            flash('Instructions updated successfully', 'success')
            return redirect(url_for('admin.manage_content'))
        except Exception as e:
            current_app.logger.error(f'Error updating instructions: {str(e)}')
            flash('Error updating instructions', 'danger')
    
    return render_template('admin/edit_instructions.html', form=form)

@bp.route('/content/add-word', methods=['POST'])
def add_word():
    """Add new word to database"""
    word = request.form.get('word', '').strip().lower()
    difficulty = request.form.get('difficulty', '').lower()
    
    if not word or not difficulty:
        flash('Both word and difficulty are required', 'danger')
        return redirect(url_for('admin.manage_content'))
    
    if difficulty not in ['easy', 'medium', 'hard']:
        flash('Invalid difficulty level', 'danger')
        return redirect(url_for('admin.manage_content'))
    
    try:
        new_word = Word(text=word, difficulty=difficulty)
        db.session.add(new_word)
        db.session.commit()
        flash('Word added successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error adding word: {str(e)}')
        flash('Error adding word', 'danger')
    
    return redirect(url_for('admin.manage_content'))

@bp.route('/edit-word/<int:word_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_word(word_id):
    word = Word.query.get_or_404(word_id)
    form = EditWordForm(obj=word)
    
    if form.validate_on_submit():
        form.populate_obj(word)
        db.session.commit()
        flash('Word updated successfully!', 'success')
        return redirect(url_for('admin.manage_content'))
    
    return render_template('admin/edit_word.html', form=form, word=word)

@bp.route('/content/delete-word/<int:word_id>', methods=['POST'])
def delete_word(word_id):
    """Delete word from database"""
    word = Word.query.get_or_404(word_id)
    try:
        db.session.delete(word)
        db.session.commit()
        flash('Word deleted successfully', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Error deleting word: {str(e)}')
        flash('Error deleting word', 'danger')
    return redirect(url_for('admin.manage_content'))

# System Settings Routes
@bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def system_settings():
    settings = Setting.get_settings()  # Use the class method
    
    if request.method == 'POST':
        settings.app_name = request.form.get('app_name')
        settings.maintenance_mode = 'maintenance_mode' in request.form
        db.session.commit()
        flash('Settings updated successfully!', 'success')
    
    return render_template('admin/settings.html', settings=settings)

@bp.route('/update-settings', methods=['POST'])
def update_settings():
    """Update system settings"""
    form = SystemSettingsForm()
    if form.validate_on_submit():
        try:
            # Save system settings to database or config file
            flash('System settings updated successfully', 'success')
        except Exception as e:
            current_app.logger.error(f'Error updating settings: {str(e)}')
            flash('Error updating settings', 'danger')
    
    return redirect(url_for('admin.system_settings'))