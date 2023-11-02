from datetime import datetime
from flask import render_template, session, redirect, url_for, current_app, flash
from flask_login import current_user, login_required
from . import main
# from .forms import NameForm
from .. import db
from ..models import User, Event
from forms import EventForm
from functools import wraps


def org_user_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.role == "organization":
            return redirect(url_for('errors.401'))

        # flask 1.x compatibility
        # current_app.ensure_sync is only available in Flask >= 2.0
        if callable(getattr(current_app, "ensure_sync", None)):
            return current_app.ensure_sync(func)(*args, **kwargs)
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
"""
@main.route('/event/create', methods=['GET'])
@login_required
@org_user_required
def event_form():
    form = EventForm()
    if form.validate_on_submit():
        try:
            event = Event(location={"place": form.place.data, "location": form.location.data, "room": form.room.data},
                        organizer={"author_id": current_user.id, "name": current_user.name},
                        event_date={"from_date": form.from_date.data, "to_date": form.to_date.data},
                        title=form.title.data,
                        description=form.description.data,
                        targeted_prefernces=form.targeted_preferences.data
            )
            event.save()
            flash('You can now login.')
            return redirect(url_for('auth.login'))
        except Exception as e:
            print(e)
            pass
    return render_template('event_create.html', form=form)


""" Events detail route 
    - Takes in event id, and gives back event details
"""
@main.route('/event/<id>', methods=['GET'])
@login_required
def event_details():
    event = Event.get_by_id(id=id)
    eventValid = False
    if event:
        eventValid = True
    return render_template('event_details.html', event=event, eventValid=eventValid)



""" Event listings route
query parameters in the url """



