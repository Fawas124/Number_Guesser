from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, ValidationError, NumberRange
from app.models import User

class AdminEditUserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    is_admin = BooleanField('Admin Status')
    is_active = BooleanField('Active Status', default=True)  # Add this line
    submit = SubmitField('Update User')

    def __init__(self, original_username, original_email, *args, **kwargs):
        super(AdminEditUserForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already registered. Please use a different one.')
            

class LevelSettingsForm(FlaskForm):
    min_range = IntegerField('Minimum Number', validators=[DataRequired(), NumberRange(min=1)])
    max_range = IntegerField('Maximum Number', validators=[DataRequired(), NumberRange(min=2)])
    attempts = IntegerField('Attempts', validators=[DataRequired(), NumberRange(min=1)])
    multiplier = IntegerField('Score Multiplier', validators=[DataRequired(), NumberRange(min=1)])

class InstructionsForm(FlaskForm):
    instructions = TextAreaField('Game Instructions', validators=[DataRequired()])

class SystemSettingsForm(FlaskForm):
    app_name = StringField('Application Name', validators=[DataRequired()])
    items_per_page = IntegerField('Items Per Page', validators=[DataRequired(), NumberRange(min=1)])
    maintenance_mode = BooleanField('Maintenance Mode')

class EditWordForm(FlaskForm):
    text = StringField('Word', validators=[DataRequired()])
    difficulty = IntegerField('Difficulty', validators=[DataRequired()])
    is_active = BooleanField('Is Active')