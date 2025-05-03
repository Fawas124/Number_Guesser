from flask import render_template
from flask_login import login_required
from app import db
from app.models import User, GameSession
from app.leaderboard import bp

def get_level_leaderboard(level):
    """Helper function to get top scores for a specific level"""
    return db.session.query(
        GameSession.score,
        User.username
    ).join(
        User
    ).filter(
        GameSession.level == level,
        GameSession.won == True
    ).order_by(
        GameSession.score.desc()
    ).limit(10).all()

@bp.route('/')
@bp.route('/leaderboard')  # Handle both root and /leaderboard paths
@login_required
def show_leaderboard():
    """Display the main leaderboard with top players and recent games"""
    # Get top 10 players by best score
    top_players = db.session.query(
        User.username,
        User.best_score
    ).order_by(
        User.best_score.desc()
    ).limit(10).all()

    # Get recent 10 winning games
    recent_games = db.session.query(
        GameSession,
        User.username
    ).join(
        User
    ).filter(
        GameSession.won == True
    ).order_by(
        GameSession.created_at.desc()
    ).limit(10).all()

    # Get level-specific leaderboards
    level_leaderboards = {
        'easy': get_level_leaderboard('easy'),
        'medium': get_level_leaderboard('medium'),
        'hard': get_level_leaderboard('hard')
    }

    return render_template(
        'leaderboard/leaderboard.html',
        top_players=top_players,
        recent_games=recent_games,
        level_leaderboards=level_leaderboards
    )