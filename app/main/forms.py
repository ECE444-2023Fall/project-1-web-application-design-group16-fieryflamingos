from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectMultipleField, SelectField, HiddenField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, Optional
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

   

""" Event Search Fields Form """

""" Events creation form """
class EventSearchForm(FlaskForm):
    search = StringField("Search", render_kw={"placeholder": "Event title, location, or organizer..."})


    targeted_preferences = SelectMultipleField("Preferences", choices=Preference.get_preferences_as_tuple())
    from_date = DateTimeLocalField("Start Date", format="%Y-%m-%dT%H:%M", validators=[Optional()])
    to_date = DateTimeLocalField("End Date", format="%Y-%m-%dT%H:%M", validators=[Optional()])

    items_per_page = SelectField("Events Per Page", choices=[(10,10), (25,25), (50,50)])

    submit = SubmitField("Search")

    next_page = SubmitField("Next")
    prev_page = SubmitField("Back")



""" Update profile form """
class UpdateRegularUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(Regexp("^[a-zA-Z \-]+$", message="Not a valid name."))])
    last_name = StringField('Last Name', validators=[DataRequired(Regexp("^[a-zA-Z \-]+$", message="Not a valid name."))])
    
    preferences = SelectMultipleField("Preferences", choices=Preference.get_preferences_as_tuple())

    submit = SubmitField("Update")


""" Update profile form """
class UpdateOrganizationUserForm(FlaskForm):
    name = StringField('Last Name', validators=[DataRequired(Regexp("^[a-zA-Z \-]+$", message="Not a valid name."))])
    
    submit = SubmitField("Update")

    

