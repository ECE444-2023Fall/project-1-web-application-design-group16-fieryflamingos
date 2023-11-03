from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, abort
from flask_login import current_user, login_required
from . import main
# from .forms import NameForm
from .. import db
from ..models import User, RegularUser, OrganizationUser, Event, Preference, Comment
from .forms import EventForm, RSVPForm, CancelRSVPForm, EventSearchForm, UpdateRegularUserForm, UpdateOrganizationUserForm
from functools import wraps

from math import ceil


""" org_user_required
Decorator that checks if user is an organization """
def org_user_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.role == "organization":
            redirect(url_for('errors.403'))

        return func(*args, **kwargs)

    return decorated_view



""" Dashboard:
Data: 
    Recommended Events
    Upcoming Events
Organizations users get redirected to their profile page
"""
@main.route('/', methods=['GET'])
@login_required
def index():
    user = current_user

    if user.role == "organization":
        return redirect(url_for("/profile-org"))

    recommended_events = Event.get_recommended(user.preferences)
    upcoming_events = Event.get_upcoming(user.id)
    
    return render_template('index.html',
                            recommended_events=recommended_events,
                            upcoming_events=upcoming_events)

 

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
    if form.validate_on_submit():
        try:
            event = Event(location={"place": form.location_place.data, "address": form.location_address.data, "room": form.location_room.data},
                        organizer={"author_id": current_user.id, "name": current_user.name},
                        event_date={"from_date": form.from_date.data, "to_date": form.to_date.data},
                        title=form.title.data,
                        description=form.description.data,
                        targeted_preferences=form.targeted_preferences.data
            )
            event = event.save()

            # update preferences
            for preference in form.targeted_preferences.data:
                Preference.inc_event_count(preference)
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


""" Event Update form
    - Allows org users to create events
DATA: 
    - form: EventForm
"""
@main.route('/event/update/<id>', methods=['GET', 'POST'])
@login_required
@org_user_required
def event_form(id):
    # get event
    event = Event.get_by_id(id=id)

    # Check if event is valid
    if not event:
        return redirect(url_for('errors.404'))
    
    # Check if org user is right one
    if event.organizer.author_id != current_user.id:
        return redirect(url_for("errors.403"))
    
    # Everything valid, set the form 
    form = EventForm(location_place=event.location.place,
                     locaton_address=event.location.address,
                     location_room=event.location.room,
                     from_date=event.event_date.from_date,
                     to_date=event.event_date.to_date,
                     description=event.description,
                     title=event.title,
                     targeted_preferences=event.targeted_preferences)
    
    if form.validate_on_submit():
        try:
         
            updated_event = Event.objects(id=event.id).update_one(location__place=form.location_place.data,
                                                                 location__address=form.location_address.data,
                                                                 location__room=form.location_room.data,
                                                                 event_date__from_date=form.from_date.data,
                                                                 event_date__to_date=form.to_date.data,
                                                                 title=form.title.data,
                                                                 description=form.description.data,
                                                                 targeted_preferences=form.targeted_preferences.data)

            # update preferences
            # convert old preferences to a list of strings
            old_preferences = [str(x) for x in event.targeted_preferences]
            # find newly added preferences
            new_preferences = [x for x in form.targeted_preferences.data if x not in old_preferences]

            # find removed preferences
            removed_preferences = [x for x in old_preferences if x not in form.targeted_preferences.data]

            # increase/decrease event count
            for preference in new_preferences:
                Preference.inc_event_count(preference)
            for preference in removed_preferences:
                Preference.inc_event_count(preference, inc=-1)

            return redirect(url_for(f'main.event_details', id=str(event.id)))
        except Exception as e:
            print(e)
            pass
    return render_template('event_create.html', form=form)


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



""" View Profile route
 """
@main.route('/profile', methods=['GET'])
@login_required
def get_profile():
    user = current_user

    if user.role == "organization":
        return redirect(url_for("main.get_profile_org", id=user.id))
    
    # get event summary
    future_events = Event.get_summary_from_list_future(user.registered_events)
    past_events = Event.get_summary_from_list_past(user.registered_events)

    return render_template('profile.html', user=user, future_events=future_events, past_events=past_events)


""" View organization profile """
@main.route('/profile-org/<id>', methods=['GET'])
@login_required
def get_profile_org(id):
    user = OrganizationUser.get_by_id(id)

    if user == None:
        return redirect(url_for("errors.404"))
    
    if user.id == current_user.id:
        current_user_is_specified = True

    # get event summary
    future_events = Event.get_organization_events_future(user.id)
    past_events = Event.get_organization_events_past(user.id)

    # get events
    return render_template('profile_org.html', user=user, current_user_is_specified=current_user_is_specified, future_events=future_events, past_events=past_events)


""" Edit profile route
Edit your own profile. this route is reserved for
regular users """
@main.route("/profile/edit", methods=['GET', 'POST'])
@login_required
def update_profile_regular():
    user = current_user
    if user.role == "organization":
        return redirect(url_for("main.update_profile_organization"))

    form = UpdateRegularUserForm(first_name=user.first_name, last_name=user.last_name,preferences=user.preferences)

    if form.validate_on_submit():
        try:
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.preferences = form.preferences.data
            RegularUser.objects(id=user.id).update_one(first_name=form.first_name.data,
                                                last_name=form.last_name.data,
                                                preferences=form.preferences.data)
            
            return redirect(url_for("main.get_profile"))
        except:
            flash("An error occurred while updating your profile")
    return render_template('update_profile.html', form=form, user=user)


""" Edit organization profile route """
@main.route("/profile/edit-org", methods=['GET', 'POST'])
@login_required
def update_profile_organization():
    user = current_user
    if user.role == "regular":
        return redirect(url_for("main.update_profile_regular"))
    
    form = UpdateOrganizationUserForm(name=user.name)

    if form.validate_on_submit():
        try:
            user.name = form.name.data
            OrganizationUser.objects(id=user.id).update_one(name=form.name.data)
            return redirect(url_for("main.get_profile"))
        except:
            flash("An error occurred while updating your profile")

    return render_template('update_profile_org.html', form=form, user=user)


