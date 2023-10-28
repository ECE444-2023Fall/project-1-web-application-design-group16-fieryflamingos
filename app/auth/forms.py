from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import RegularUser

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
    Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')



class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
    Email()])
    password = PasswordField('Password', validators=[
    DataRequired(), EqualTo('password2', message='Passwords must match.'),  Regexp('^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9])(?=.*[@#$%^&+=]).{8,25}$', 0,
    """Password Requirements:\n  
    \tlength: 8-25 characters\n 
    \tAt least 1 uppercase letter\n 
    \tAt least 1 lowercase letter\n 
    \tAt least 1 number\n 
    \tAt least 1 special character""")])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if RegularUser.objects(email=field.data).get():
            raise ValidationError('Email already registered.')
        
   