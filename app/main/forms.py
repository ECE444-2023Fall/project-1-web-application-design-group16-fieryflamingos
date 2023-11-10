from flask_wtf import FlaskForm
from wtforms import Field, StringField, PasswordField, BooleanField, SubmitField, SelectMultipleField, SelectField, HiddenField, DateField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo, Optional
from wtforms.widgets import html_params, TextArea
from wtforms import ValidationError
from markupsafe import Markup
from ..models import Preference


class TagWidget(object):
    """
    A widget that renders a list of tags as clickable buttons.
    Each tag has a display label and a value associated.
    The user can click on each tag to select it, and click on it again to unselect it.
    The selected tags are stored in a hidden field as a comma-separated list of values.
    """

    def __call__(self, field, **kwargs):
        # Get the list of tags from the field choices
        tags = field.choices
        # Get the list of selected values from the field data
        selected = field.data or []
        # Initialize an empty list to store the HTML output
        html = []
        # Loop through each tag
        for tag in tags:
            # Get the label and value of the tag
            label, value, num_events = tag
            # Check if the tag is selected
            is_selected = value in selected
            # Generate the HTML attributes for the tag button
            tag_attrs = html_params(
                type="button",
                name=field.name,
                value=value,
                class_="interest-tag" + (" selected" if is_selected else ""),
                onclick="toggleTag(this)"
            )
            # Generate the HTML code for the tag button
            tag_html = f'<button {tag_attrs}>{label}  <div class="tag-number">{num_events}</div></button>'
            # Append the tag button to the HTML output
            html.append(tag_html)
        # Generate the HTML attributes for the hidden field
        hidden_attrs = html_params(
            type="hidden",
            id=field.id,
            name=field.name,
            value=" ".join(selected)
        )
        # Generate the HTML code for the hidden field
        hidden_html = f'<input {hidden_attrs}>'
        # Append the hidden field to the HTML output
        html.append(hidden_html)
        # Generate the HTML code for the script that handles the tag selection logic
        script_html = """
        <script>
        function toggleTag(button) {
            button.classList.toggle("selected");
            let hiddenInput = document.getElementById(button.name);
            if (hiddenInput.value.includes(button.value)) {
                hiddenInput.value = hiddenInput.value.replace(button.value, "").trim();
            }
            else  {
                hiddenInput.value = `${hiddenInput.value} ${button.value}`.trim();
            }
        }
        </script>
        """
        # Append the script to the HTML output
        html.append(script_html)
        # Return the HTML output as a string
        return Markup("".join(html))

class TagField(Field):
    """
    A custom field that uses the TagWidget to render a list of tags.
    The data of this field is a list of values of the selected tags.
    """

    widget = TagWidget()

    def __init__(self, label=None, validators=None, choices=None, **kwargs):
        # Initialize the field with the given label, validators, and keyword arguments
        super(TagField, self).__init__(label, validators, **kwargs)
        # Set the choices attribute to the given choices or an empty list
        self.choices = choices or []


    def process_formdata(self, valuelist):
        # Process the form data by splitting the comma-separated string into a list
        if valuelist:
            self.data = valuelist[0].split(" ")
        else:
            self.data = []

    def pre_validate(self, form):
        # Validate the field data by checking if all the values are in the choices
        if self.data:
            for value in self.data:
                if not value:
                    self.data = []
                elif not any(value == choice[1] for choice in self.choices):
                    raise ValueError(self.gettext("Invalid tag value: {}".format(value)))


""" Events creation form """
class EventForm(FlaskForm):
    location_place = StringField("Place")
    location_address = StringField("Location*")
    location_room = StringField("Room")

    title = StringField("Title*", validators=[DataRequired()])

    targeted_preferences = TagField("Interests", choices=Preference.get_preferences_as_tuple())
    description = StringField("Description", widget=TextArea(), validators=[Length(0, 10000, message="Length must be less than 10000 characters.")])

    from_date = DateTimeLocalField("Start Date*", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    to_date = DateTimeLocalField("End Date*", format="%Y-%m-%dT%H:%M", validators=[DataRequired()])
    registration_open_until = DateTimeLocalField("Registration Open Until", format="%Y-%m-%dT%H:%M", validators=[Optional()])

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
    search = StringField("Keyword Search", render_kw={"placeholder": "Event title, location, or organizer..."})

    preferences = TagField("Interests", choices=Preference.get_preferences_as_tuple())

    start_date = DateField("Start Date", format="%Y-%m-%d", validators=[Optional()])
    end_date = DateField("End Date", format="%Y-%m-%d", validators=[Optional()])

    items_per_page = SelectField("Events Per Page", choices=[(10,10), (20,20), (30,30)])

    submit = SubmitField("Search")



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

    
""" Comment form """
class CommentForm(FlaskForm):
    content = StringField("Comment", widget=TextArea(), render_kw={"placeholder":"Write a short review or ask a question"}, validators=[DataRequired(), Length(0, 10000, message="Length must be less than 10,000 characters.")])

    rating = SelectField("Rating (1-5), or leave blank", choices=[(None, "---"), (1,1), (2,2), (3,3), (4,4), (5,5)], validators=[DataRequired()])
    submit = SubmitField("Comment")

""" Reply Form """
class ReplyForm(FlaskForm):
    reply = StringField("Reply", widget=TextArea(), render_kw={"placeholder":"Reply..."},)
    submit = SubmitField("Reply")




