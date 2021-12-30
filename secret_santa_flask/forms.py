from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from secret_santa_flask.models import User



class RegistrationForm(FlaskForm):
    username = StringField(label='Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    social = StringField(label='Social Security (Must be entered correctly)', validators=[DataRequired(), Length(min=9, max=9)])
    password = PasswordField(label = 'Password', validators=[DataRequired()])
    confirm_password = PasswordField(label = 'Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(label='Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField(label='Email', validators=[DataRequired(), Email()])
    password = PasswordField(label = 'Password', validators=[DataRequired()])
    remember = BooleanField(label='Remember Me')
    submit = SubmitField(label='Login')

class UpdateAccountForm(FlaskForm):
    likes = StringField(label='What kind of gifts do you want?', validators=[DataRequired(), Length(min=0, max=120)])
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
    submit = SubmitField(label='Update')
