from datetime import datetime
from flask import render_template, session, redirect, url_for, flash
from flask_login import current_user, login_required
from . import main
# from .forms import NameForm
from .. import db
from ..models import User, Event, Preference, Comment
from .forms import EventForm, RSVPForm, CancelRSVPForm
from functools import wraps


""" org_user_required
Decorator that checks if user is an organization """
def org_user_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.role == "organization":
            return redirect(url_for('errors.401'))

        return func(*args, **kwargs)

    return decorated_view



""" Dashboard:
Data: 
    Recommended Events
    Upcoming Events
"""
@main.route('/', methods=['GET'])
@login_required
def index():
    user = current_user
    try:
        recommended_events = Event.get_recommended(user.preferences)
        upcoming_events = Event.get_upcoming(user.id)
        
        return render_template('index.html',
                                recommended_events=recommended_events,
                                upcoming_events=upcoming_events)
    except Exception as e:
        return render_template('index.html')

 

""" Basic Nav Bar Template"""
@main.route('/base', methods=['GET'])
def base():
    return render_template('base.html')


""" Event Details form
    - Allows org users to create events
DATA: 
    - form: EventForm
"""
@main.route('/event/create', methods=['GET', 'POST'])
@login_required
@org_user_required
def event_form():
    form = EventForm()
    print("INSIDE HERE")
    print("from_date: ", form.from_date.data)
    print("to_date: ", form.to_date.data)
    if form.validate_on_submit():
        print("place: ", form.location_place.data)
        print("address: ", form.location_address.data)
        print("room: ", form.location_room.data)
        print("current_user: ", current_user.name)
        print("title: ", form.title.data)
        print("description: ", form.description.data)
        print("preferences: ", form.targeted_preferences.data)
        try:
            event = Event(location={"place": form.location_place.data, "address": form.location_address.data, "room": form.location_room.data},
                        organizer={"author_id": current_user.id, "name": current_user.name},
                        event_date={"from_date": form.from_date.data, "to_date": form.to_date.data},
                        title=form.title.data,
                        description=form.description.data,
                        targeted_preferences=form.targeted_preferences.data
            )
            event = event.save()
            return redirect(url_for(f'main.event_details', id=str(event.id)))
        except Exception as e:
            print(e)
            pass
    return render_template('event_create.html', form=form)


""" Events detail route 
    - Takes in event id, and gives back event details
DATA:
    - event: Event
    - comments: Comment[]
    - user_is_attendee: boolean
    - form: RSVPForm | CancelRSVPForm

"""
@main.route('/event/<id>', methods=['GET', 'POST'])
@login_required
def event_details(id):
    # get event
    event = Event.get_by_id(id=id)

    # Check if event is valid
    if not event:
        return redirect(url_for('errors.404'))

    # create RSVP form
    form = RSVPForm()

    # check if user already is RSVP'ed, if so, change RSVPForm to CancelRSVPForm
    user_is_attendee = False
    for attendee in event.attendees:
        if attendee.id == current_user.id:
            user_is_attendee = True
            form = CancelRSVPForm()
    
    # get preferences data, list of Preference objects
    preferences = []
    for pref_id in event.targeted_preferences:
        preferences.append(Preference.get_preference_by_id(pref_id))
    
    # get comments for the event
    comments = Comment.get_comments_by_event_id(id)

    # VALIDATE FORMS
    if form.validate_on_submit():
        if isinstance(form, RSVPForm):
            name = ""
            if current_user.role == "regular":
                name = f"{current_user.first_name} {current_user.last_name}"
            else:
                name = current_user.name
            event = event.add_attendee(event.id, current_user.id, name)
            user_is_attendee = True
            form = CancelRSVPForm()
        elif isinstance(form, CancelRSVPForm):
            event = event.remove_attendee(event.id, current_user.id)
            user_is_attendee = False
            form = RSVPForm()

    
    return render_template('event_details.html', event=event, user_is_attendee=user_is_attendee, comments=comments, form=form)



""" Event listings route
query parameters in the url """



