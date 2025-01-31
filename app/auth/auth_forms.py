from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from app.main.models import User
from app import db

class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=30)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=15)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    wpi_id = StringField('WPI ID', validators=[DataRequired(), Length(min=9, max=9)])
    phonenum = StringField('Phone Number', validators=[Length(max=10)])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('This email is already registered.')
        if not email.data.endswith('@wpi.edu'):
            raise ValidationError('Email must be a WPI email ending with @wpi.edu.')

    def validate_wpi_id(self, wpi_id):
        user = User.query.filter_by(wpi_id=wpi_id.data).first()
        if user:
            raise ValidationError('This WPI ID is already registered.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')
