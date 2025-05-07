from flask import render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import current_user, login_required
from functools import wraps
from datetime import datetime, timedelta
from app import db
from app.models import User, GameSession, Feedback, Word, Setting
from app.admin import bp
from app.admin.forms import (
    AdminEditUserForm, 
    LevelSettingsForm,
    InstructionsForm,
    SystemSettingsForm,
    EditWordForm
)

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
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    form = AdminEditUserForm(
        original_username=user.username,
        original_email=user.email,
        obj=user
    )

    if form.validate_on_submit():
        form.populate_obj(user)
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
    # Get or create settings for each level
    easy = Setting.get_settings('easy')
    medium = Setting.get_settings('medium')
    hard = Setting.get_settings('hard')
    
    # Set defaults if they don't exist
    if not easy.range_low:
        easy.range_low = 1
        easy.range_high = 50
        easy.max_attempts = 10
        db.session.commit()
    
    if not medium.range_low:
        medium.range_low = 1
        medium.range_high = 100
        medium.max_attempts = 7
        db.session.commit()
        
    if not hard.range_low:
        hard.range_low = 1
        hard.range_high = 200
        hard.max_attempts = 5
        db.session.commit()
    
    return render_template('admin/manage_content.html',
        easy_settings=easy,
        medium_settings=medium,
        hard_settings=hard
    )

@bp.route('/content/levels/<level>', methods=['GET', 'POST'])
def edit_level(level):
    """Edit game level settings"""
    level_setting = Setting.get_level_settings(level)
    if not level_setting:
        abort(404)
    
    form = LevelSettingsForm(obj=level_setting)
    
    if form.validate_on_submit():
        try:
            form.populate_obj(level_setting)
            db.session.commit()
            flash(f'{level.capitalize()} level settings updated', 'success')
            return redirect(url_for('admin.manage_content'))
        except Exception as e:
            current_app.logger.error(f'Error updating level settings: {str(e)}')
            flash('Error updating level settings', 'danger')
    
    return render_template('admin/edit_level.html', level=level, form=form)

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
@bp.route('/settings')
def system_settings():
    # Get settings for all levels
    levels = {
        'easy': Setting.get_settings('easy'),
        'medium': Setting.get_settings('medium'),
        'hard': Setting.get_settings('hard')
    }
    
    return render_template('admin/settings.html',
        settings=levels  # Pass as 'settings' to template
    )

@bp.route('/update-ranges', methods=['POST'])
def update_ranges():
    if request.method == 'POST':
        try:
            levels = ['easy', 'medium', 'hard']
            for level in levels:
                setting = Setting.get_settings(level)
                setting.update_ranges(
                    request.form.get(f'{level}_min'),
                    request.form.get(f'{level}_max'),
                    request.form.get(f'{level}_attempts')
                )
            
            db.session.commit()
            flash('Number ranges updated successfully!', 'success')
            
        except ValueError as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
        except Exception as e:
            db.session.rollback()
            flash('Failed to update ranges', 'danger')
            current_app.logger.error(f"Update error: {str(e)}")
    
    return redirect(url_for('admin.system_settings'))

@bp.route('/settings/update', methods=['POST'])
def update_settings():
    try:
        for level in ['easy', 'medium', 'hard']:
            setting = Setting.get_settings(level)
            setting.range_low = int(request.form.get(f'{level}_min'))
            setting.range_high = int(request.form.get(f'{level}_max'))
            setting.max_attempts = int(request.form.get(f'{level}_attempts'))
        
        db.session.commit()
        flash('Settings updated successfully!', 'success')
    except ValueError:
        flash('Please enter valid numbers', 'danger')
    except Exception as e:
        flash('Error updating settings', 'danger')
        current_app.logger.error(f"Settings update error: {str(e)}")
    
    return redirect(url_for('admin.system_settings'))