from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import RegularUser, OrganizationUser, User

class LoginForm(FlaskForm):
    username = StringField('Username', render_kw={"placeholder": "Username..."}, validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('Password',render_kw={"placeholder": "Password..."},  validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Sign in to Occasional')


# check if email already taken
def validate_username(form,field):
    try:
        User.get_user_by_username(field.data)

        # if we get to here, means that email is not unique
        raise ValidationError(f'Username already taken.')
    except:
        pass


class RegistrationRegularForm(FlaskForm):
    first_name = StringField('First Name', render_kw={"placeholder": "First Name..."}, validators=[DataRequired(Regexp("^[a-zA-Z \-]+$", message="Not a valid name."))])
    last_name = StringField('Last Name', render_kw={"placeholder": "Last Name..."}, validators=[DataRequired(), Regexp("^[a-zA-Z \-]+$", message="Not a valid name.")])
    email = StringField('UofT Email', render_kw={"placeholder": "UofT Email (e.g., John.Doe@mail.utoronto.ca)"}, validators=[DataRequired(), Length(1, 64),
        Email()])
    username = StringField('Username', render_kw={"placeholder": "Username..."}, validators=[DataRequired(), Length(1,64), validate_username])
    password = PasswordField('Password', render_kw={"placeholder": "Password..."}, validators=[Regexp("^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", message="Invalid Password"),
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    
    password2 = PasswordField('Confirm password', render_kw={"placeholder": "Confirm Password..."}, validators=[DataRequired()])
    
    submit = SubmitField('Register')



class RegistrationOrganizationForm(FlaskForm):
    name = StringField('Organization Name', render_kw={"placeholder": "Organization Name..."}, validators=[DataRequired(Regexp("^[a-zA-Z \-]+$", message="Not a valid name."))])
    email = StringField('Email', render_kw={"placeholder": "UofT Email (e.g., John.Doe@mail.utoronto.ca)"}, validators=[DataRequired(), Length(1, 64),
        Email()])
    username = StringField('Username', render_kw={"placeholder": "Username..."}, validators=[DataRequired(), Length(1,64), validate_username])
    password = PasswordField('Password', render_kw={"placeholder": "Password..."}, validators=[Regexp("^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$", message="Invalid Password"),
        DataRequired(), EqualTo('password2', message='Passwords must match.')])
    
    password2 = PasswordField('Confirm password', render_kw={"placeholder": "Confirm Password..."}, validators=[DataRequired()])
    
    submit = SubmitField('Register')

   
        
   