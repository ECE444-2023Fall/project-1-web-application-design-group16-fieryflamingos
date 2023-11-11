from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import RegularUser, OrganizationUser, User
from ..util import validate_email as util_email_validate

class LoginForm(FlaskForm):
    username = StringField('Username', render_kw={"placeholder": "Username"}, validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password',render_kw={"placeholder": "Password"},  validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Sign in')


# check if username already taken
def validate_username(form,field):
    users = User.objects(username=field.data.strip())
    if len(users) > 0:
        raise ValidationError(f'Username already taken.')

# check if email is valid
def validate_email(form, field):
    util_email_validate(field.data.strip())


class RegistrationRegularForm(FlaskForm):
    first_name = StringField('First Name', render_kw={"placeholder": "First Name"}, validators=[DataRequired(Regexp("^[a-zA-Z \-]+$", message="Not a valid name."))])
    last_name = StringField('Last Name', render_kw={"placeholder": "Last Name"}, validators=[DataRequired(), Regexp("^[a-zA-Z \-]+$", message="Not a valid name.")])
    email = StringField('UofT Email', render_kw={"placeholder": "U of T Email (e.g., John.Doe@mail.utoronto.ca)"}, validators=[DataRequired(), Length(1, 64),
        Email(), validate_email])
    username = StringField('Username', render_kw={"placeholder": "Username"}, validators=[DataRequired(), Length(1,64), validate_username])
    password = PasswordField('Password', render_kw={"placeholder": "Password"}, validators=[Regexp("^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", message="Invalid Password"),
        DataRequired()])
    
    password2 = PasswordField('Confirm password', render_kw={"placeholder": "Confirm Password"}, validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    
    submit = SubmitField('Register')



class RegistrationOrganizationForm(FlaskForm):

    name = StringField('Organization Name', render_kw={"placeholder": "Organization Name"}, validators=[DataRequired(Regexp("^[a-zA-Z \-]+$", message="Not a valid name."))])
    email = StringField('Email', render_kw={"placeholder": "Organization Email (e.g., skule.org@mail.utoronto.ca)"}, validators=[DataRequired(), Length(1, 64),
        Email(), validate_email])
    username = StringField('Username', render_kw={"placeholder": "Username"}, validators=[DataRequired(), Length(1,64), validate_username])
    password = PasswordField('Password', render_kw={"placeholder": "Password"}, validators=[Regexp("^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", message="Invalid Password"),
        DataRequired()])
    
    password2 = PasswordField('Confirm password', render_kw={"placeholder": "Confirm Password..."}, validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    
    submit = SubmitField('Register')

   
        
   