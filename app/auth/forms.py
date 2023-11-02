from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import RegularUser, OrganizationUser

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
    Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


# check if email already taken
def validate_email(form,field):
    try:
        RegularUser.objects(email=field.data).get()

        # if we get to here, means that email is not unique
        raise ValidationError(f'Email already taken.')
    except:
        pass


class RegistrationForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(Regexp("^[a-zA-Z \-]+$", message="Not a valid name."))])
    last_name = StringField('First Name', validators=[DataRequired(), Regexp("^[a-zA-Z \-]+$", message="Not a valid name.")])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
        Email(), validate_email])
    password = PasswordField('Password', validators=[Regexp("^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", message="Invalid Password"),
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    
    submit = SubmitField('Register')


# check if email already taken
def validate_email(form,field):
    try:
        OrganizationUser.objects(email=field.data).get()
        
        # if we get to here, means that email is not unique
        raise ValidationError(f'Email already taken.')
    except:
        pass


class RegistrationOrganizationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(Regexp("^[a-zA-Z \-]+$", message="Not a valid name."))])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
        Email(), validate_email])
    password = PasswordField('Password', validators=[Regexp("^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", message="Invalid Password"),
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    
    submit = SubmitField('Register')

   
        
   