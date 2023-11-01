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
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('First Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
    Email()])
    password = PasswordField('Password', validators=[Regexp("^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$"),
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    
    submit = SubmitField('Register')

    def validate_email(self, field):
        try:
            if RegularUser.objects(email=field.data).get():
                return False
        except:
            return True
        
   