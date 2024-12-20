from flask_wtf import FlaskForm
import sqlalchemy as sqla
from wtforms import SelectField, StringField, SubmitField,PasswordField,BooleanField,validators
from wtforms.validators import  ValidationError, DataRequired, EqualTo, Email,Length
from app.main.models import User
from app import db



class RegistrationForm(FlaskForm):
    first_name = StringField('First name', validators=[DataRequired()])
    last_name = StringField('Last name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()] )
    wpi_id = StringField('WPI ID', validators=[DataRequired(), Length(min=9, max=9)])
    phonenum = StringField('Phone Number', validators=[DataRequired()])
    password = PasswordField('Password',validators= [DataRequired()])
    password2 = PasswordField('Password',validators= [DataRequired(),EqualTo('password')])
    submit = SubmitField('Post')
    def validate_email(self,email):
        query = sqla.select(User).where(User.email == email.data)
        user = db.session.scalars(query).first()
        if user is not None:
            raise validators.ValidationError('Email is already existed, Please use a different email.')
        if not email.data.endswith('@wpi.edu'):
            raise ValidationError("Email must be a WPI email ending with 'wpi.edu'")
    def validate_wpi_id(self, wpi_id):
        query = sqla.select(User).where(User.wpi_id == wpi_id.data)
        user = db.session.scalars(query).first()
        if user is not None:
            raise ValidationError('The ID is associated with another account! Please log in to your account.')
class LoginForm(FlaskForm):
    email = StringField('email',validators= [DataRequired()])
    password = PasswordField('Password',validators= [DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Login')