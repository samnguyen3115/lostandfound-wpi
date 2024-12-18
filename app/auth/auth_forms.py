from flask_wtf import FlaskForm
import sqlalchemy as sqla
from wtforms import StringField, SubmitField,PasswordField,BooleanField,validators
from wtforms.validators import  ValidationError, DataRequired, EqualTo, Email
from app.main.models import User
from app import db


class RegistrationForm(FlaskForm):
    username = StringField('Username',validators= [DataRequired()])
    email = StringField('Email',validators= [DataRequired(),Email()])
    phonenum = StringField('Phone Number',validators= [DataRequired()])
    password = PasswordField('Password',validators= [DataRequired()])
    password2 = PasswordField('Password',validators= [DataRequired(),EqualTo('password')])
    submit = SubmitField('Post')
    def validate_username(self,username):
        query = sqla.select(User).where(User.username == username.data)
        user = db.session.scalars(query).first()
        if user is not None:
            raise validators.ValidationError('Username is already existed, Please use a different username.')
    def validate_email(self,email):
        query = sqla.select(User).where(User.email == email.data)
        user = db.session.scalars(query).first()
        if user is not None:
            raise validators.ValidationError('Email is already existed, Please use a different email.')
        if not email.data.endswith('@wpi.edu'):
            raise ValidationError("Email must be a WPI email ending with 'wpi.edu'")
        
class LoginForm(FlaskForm):
    username = StringField('username',validators= [DataRequired()])
    password = PasswordField('Password',validators= [DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')