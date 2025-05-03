from flask import render_template
from app.main import bp

@bp.route('/')
def index():
    """Render the home page"""
    return render_template('main/index.html')

@bp.route('/contact')
def contact():
    """Render the contact page"""
    return render_template('main/contact.html')

@bp.route('/about')
def about():
    """Render the about page"""
    return render_template('main/about.html')

@bp.route('/feedback')
def feedback():
    """Render the feedback form page"""
    return render_template('main/feedback.html')