import random
from datetime import datetime

from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from sqlalchemy.orm import joinedload

from app import db
from app.game import bp
from app.game.constants import LEVEL_SETTINGS
from app.models import GameSession, Guess, User

@bp.route('/select-level')
@login_required
def select_level():
    """Render level selection page with game difficulty options."""
    return render_template('game/select_level.html', LEVEL_SETTINGS=LEVEL_SETTINGS)

@bp.route('/start-game', methods=['POST'])
@login_required
def start_game():
    """Initialize a new game session based on selected level."""
    level = request.form.get('level', 'easy')
    if level not in LEVEL_SETTINGS:
        flash('Invalid level selected', 'danger')
        return redirect(url_for('game.select_level'))

    min_num, max_num = LEVEL_SETTINGS[level]['range']
    secret = random.randint(min_num, max_num)

    game_session = GameSession(
        user_id=current_user.id,
        level=level,
        secret_number=secret,
        attempts_left=LEVEL_SETTINGS[level]['attempts'],
        current_range_low=min_num,
        current_range_high=max_num
    )
    db.session.add(game_session)
    db.session.commit()

    return redirect(url_for('game.play', game_id=game_session.id))

@bp.route('/play/<int:game_id>', methods=['GET', 'POST'])
@login_required
def play(game_id):
    """Handle gameplay: display form, process guesses, and track history."""
    game = GameSession.query.get_or_404(game_id)

    # Prevent access by other users
    if game.user_id != current_user.id:
        flash('You cannot access this game', 'danger')
        return redirect(url_for('main.index'))

    # Already finished?
    if game.completed:
        return redirect(url_for('game.results', game_id=game.id))

    # Get level settings with defaults
    level_settings = LEVEL_SETTINGS.get(game.level, {})
    multiplier = level_settings.get('multiplier', 1)
    points_per_attempt = level_settings.get('points_per_attempt', 10)

    hint = None
    if request.method == 'POST':
        # Parse guess
        try:
            guess_val = int(request.form.get('guess'))
        except (ValueError, TypeError):
            flash('Please enter a valid number', 'danger')
            return redirect(url_for('game.play', game_id=game.id))

        # Decrease attempt and record
        game.attempts_left -= 1

        # Correct?
        if guess_val == game.secret_number:
            game.score = game.attempts_left * points_per_attempt * multiplier
            game.completed = True
            game.won = True
            game.end_time = datetime.utcnow()

            # Update user stats
            current_user.games_played += 1
            current_user.games_won += 1
            if game.score > current_user.best_score:
                current_user.best_score = game.score

            db.session.add(Guess(
                game_id=game.id,
                guess_value=guess_val,
                result='correct'
            ))
            db.session.commit()
            return redirect(url_for('game.results', game_id=game.id))

        # Too high / too low
        hint = 'too high' if guess_val > game.secret_number else 'too low'
        if hint == 'too high':
            game.current_range_high = min(game.current_range_high, guess_val - 1)
        else:
            game.current_range_low = max(game.current_range_low, guess_val + 1)

        db.session.add(Guess(
            game_id=game.id,
            guess_value=guess_val,
            result=hint
        ))

        # Out of attempts?
        if game.attempts_left <= 0:
            game.completed = True
            game.end_time = datetime.utcnow()
            current_user.games_played += 1
            db.session.commit()
            return redirect(url_for('game.results', game_id=game.id))

        db.session.commit()

    # Render the play template
    return render_template(
        'game/play.html',
        game=game,
        hint=hint,
        range_low=game.current_range_low,
        range_high=game.current_range_high,
        LEVEL_SETTINGS=LEVEL_SETTINGS,
        multiplier=multiplier
    )

@bp.route('/results/<int:game_id>')
@login_required
def results(game_id):
    """Show finished game results."""
    game = GameSession.query.get_or_404(game_id)
    if game.user_id != current_user.id:
        flash('You cannot access this game', 'danger')
        return redirect(url_for('main.index'))
    
    # Calculate attempts used safely
    attempts_used = 0
    total_attempts = LEVEL_SETTINGS.get(game.level, {}).get('attempts', 0)
    if total_attempts > 0:
        attempts_used = total_attempts - game.attempts_left
    
    return render_template('game/results.html',
                         game=game,
                         attempts_used=attempts_used,
                         total_attempts=total_attempts,
                         LEVEL_SETTINGS=LEVEL_SETTINGS)

@bp.route('/leaderboard')
def leaderboard():
    """Display comprehensive leaderboards with top players and recent winners."""
    top_players = (
        User.query
            .filter(User.best_score > 0)
            .order_by(User.best_score.desc())
            .limit(10)
            .all()
    )
    
    recent_winners = (
        GameSession.query
            .options(joinedload(GameSession.user))
            .filter_by(won=True)
            .order_by(GameSession.end_time.desc())
            .limit(10)
            .all()
    )
    
    level_leaders = {
        lvl: {
            'games': (
                GameSession.query
                    .options(joinedload(GameSession.user))
                    .filter_by(level=lvl, won=True)
                    .order_by(GameSession.score.desc())
                    .limit(5)
                    .all()
            ),
            'settings': LEVEL_SETTINGS[lvl]
        }
        for lvl in LEVEL_SETTINGS
    }

    return render_template(
        'game/leaderboard.html',
        top_players=top_players,
        recent_winners=recent_winners,
        level_leaders=level_leaders,
        LEVEL_SETTINGS=LEVEL_SETTINGS
    )

@bp.route('/profile')
@login_required
def profile():
    """Display current user's stats and recent games."""
    stats = {
        'total_games': current_user.games_played,
        'games_won': current_user.games_won,
        'win_percentage': (
            current_user.games_won / current_user.games_played * 100
        ) if current_user.games_played else 0,
        'best_score': current_user.best_score
    }
    recent_games = (
        current_user.game_sessions
            .order_by(GameSession.created_at.desc())
            .limit(5)
            .all()
    )
    return render_template(
        'user/profile.html',
        user_stats=stats,
        recent_games=recent_games
    )