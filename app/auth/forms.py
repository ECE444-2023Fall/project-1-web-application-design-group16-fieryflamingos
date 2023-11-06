from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import RegularUser, OrganizationUser, User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')


# check if email already taken
def validate_username(form,field):
    try:
        User.get_user_by_username(field.data)

        # if we get to here, means that email is not unique
        raise ValidationError(f'Username already taken.')
    except:
        pass


class RegistrationRegularForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(Regexp("^[a-zA-Z \-]+$", message="Not a valid name."))])
    last_name = StringField('Last Name', validators=[DataRequired(), Regexp("^[a-zA-Z \-]+$", message="Not a valid name.")])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
        Email()])
    username = StringField('User Name', validators=[DataRequired(), Length(1,64), validate_username])
    password = PasswordField('Password', validators=[Regexp("^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", message="Invalid Password"),
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    
    submit = SubmitField('Register')



class RegistrationOrganizationForm(FlaskForm):
    name = StringField('Organization Name', validators=[DataRequired(Regexp("^[a-zA-Z \-]+$", message="Not a valid name."))])
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
        Email()])
    username = StringField('User Name', validators=[DataRequired(), Length(1,64), validate_username])
    password = PasswordField('Password', validators=[Regexp("^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", message="Invalid Password"),
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    
    submit = SubmitField('Register')

   
        
   