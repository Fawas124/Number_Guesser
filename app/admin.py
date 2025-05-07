# app/admin.py or wherever you initialize Flask-Admin
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from app.models import Setting, GameSession, db  # Make sure to import db
from app import app

# Initialize Flask-Admin
admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')

class NumberRangeView(ModelView):
    form_columns = ['range_low', 'range_high', 'difficulty', 'is_active']
    column_labels = {
        'range_low': 'Minimum Number',
        'range_high': 'Maximum Number'
    }

# Add views to admin interface
admin.add_view(NumberRangeView(Setting, db.session))
admin.add_view(ModelView(GameSession, db.session))