from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectMultipleField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError

from ..models import Preference


""" Events creation form """
class EventForm(FlaskForm):
    location_place = StringField("Place")
    location_address = StringField("Location")
    location_room = StringField("Room")

    title = StringField("Title", validators=[DataRequired()])

    targeted_preferences = SelectMultipleField("Preferences", choices=Preference.get_preferences_as_tuple())
    description = StringField("Description", validators=[DataRequired(), Length(0, 1000, message="Length must be less than 1000 characters.")])

    from_date = DateTimeLocalField("Start Date", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    to_date = DateTimeLocalField("End Date", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])

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


