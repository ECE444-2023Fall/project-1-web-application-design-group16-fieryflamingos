from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, request
from flask_login import current_user, login_required
from . import main
# from .forms import NameForm
from .. import db
from ..models import User, Event, Preference, Comment
from .forms import EventForm, RSVPForm, CancelRSVPForm, EventSearchForm
from functools import wraps

from math import ceil


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



""" Event listings route"""
@main.route('/event/search', methods=['GET', 'POST'])
@login_required
def event_search():
    form = EventSearchForm()
   
    #   get session if it exists
    page = session.get('search_page')
    search = session.get('search_search')
    from_date = session.get('search_from_date')
    to_date = session.get('search_to_date')
    preferences = session.get('search_preferences')
    items_per_page = session.get('search_items_per_page')
    max_pages = session.get('search_max_pages')

    # set page to 0 if not in session
    if not page:
        page = 0
        session['search_page'] = 0
    if not items_per_page:
        items_per_page = 10
        session['search_items_per_page'] = 10

    # check form
    if form.validate_on_submit():
        if form.submit.data:
            # update session
            session['search_search'] = form.search.data
            session['search_from_date'] = form.from_date.data
            session['search_to_date'] = form.to_date.data
            session['search_preferences'] = form.targeted_preferences.data
            session['search_items_per_page'] = form.items_per_page.data
            session['search_page'] = 0

            # update variables
            page = 0
            search = form.search.data
            from_date = form.from_date.data
            to_date = form.to_date.data
            preferences = form.targeted_preferences.data
            items_per_page = int(form.items_per_page.data)

        # go to next page
        elif form.next_page.data and page+1 < max_pages:
            page += 1
            session['search_page'] = page

        # go to prev page
        elif form.prev_page.data and page > 0:
            page -= 1
            session['search_page'] = page

        
    # perform the search
    events, count = Event.search(search=search,
        from_date=from_date,
        to_date=to_date,
        preferences=preferences,
        page=page,
        items_per_page=items_per_page)
    
    max_pages = ceil(count/items_per_page)
    session['search_max_pages'] = max_pages

    return render_template('event_list.html', events=events, form=form, page=page, max_pages=max_pages)




