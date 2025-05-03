from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user
from app.main import bp
from app.models import Feedback
from app.main.forms import FeedbackForm
from app import db

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

@bp.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Handle feedback form submission and display"""
    form = FeedbackForm()
    if form.validate_on_submit():
        feedback = Feedback(
            name=form.name.data,
            email=form.email.data,
            message=form.message.data,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        db.session.add(feedback)
        db.session.commit()
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('main.index'))
    return render_template('main/feedback.html', form=form)