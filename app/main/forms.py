from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError

from models import Preference


""" Events creation form """
class EventForm(FlaskForm):
    location_place = StringField("Place")
    location_address = StringField("Location")
    location_room = StringField("Room")

    title = StringField("Title", Validators=[DataRequired()])

    targeted_preferences = SelectField("Preferences", choices=Preference.get_preferences_as_tuple())
    description = StringField("Description", Validators=[DataRequired(), Length(0, 1000, message="Length must be less than 1000 characters.")])

    from_date = DateTimeField("Start Date", format="'%Y-%m-%d %H:%M", validators=[DataRequired()])
    to_date = DateTimeField("End Date", format="'%Y-%m-%d %H:%M", validators=[DataRequired()])

    submit = SubmitField("Create Event")

""" RSVPForm
allows user to RSVP for event """
class RSVPForm(FlaskForm):
    submit = SubmitField("RSVP")

""" CancelRSVPForm
allows user to cancel their RSVP for an event """
class CancelRSVPForm(FlaskForm):
    submit = SubmitField("Cancel RSVP")

   




""" Update profile form """


