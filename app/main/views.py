from math import ceil
from datetime import datetime
from pytz import UTC

from flask import render_template, session, redirect, url_for, flash, abort, request, make_response
from flask_login import current_user, login_required
from icalendar import Calendar
from icalendar import Event as iEvent

from . import main
from .. import db
from ..models import User, RegularUser, OrganizationUser, Event, Preference, Comment, Reply
from .forms import EventForm, RSVPForm, CancelRSVPForm, EventSearchForm, UpdateRegularUserForm, UpdateOrganizationUserForm, CommentForm, ReplyForm
from functools import wraps



class rec_up_event():
    def __init__ (self, event):
        self.weekday = event.event_date.from_date.strftime('%A')
        self.date = event.event_date.from_date.strftime('%b %d, %Y')
        self.start_time = event.event_date.from_date.strftime('%I:%M %p')
        self.end_time = event.event_date.to_date.strftime('%I:%M %p')
        self.title = event.title
        self.location = event.location
        self.organizer = event.organizer
        self.preferences = event.targeted_preferences
        #self.link = event.link
        

""" org_user_required
Decorator that checks if user is an organization """


def org_user_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.role == "organization":
            return render_template("errors/403.html")

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
    """
    This function renders the index page for the logged-in user.

    Parameters:
    None

    Returns:
    A rendered template of index.html with the recommended 
    and upcoming events for the user.

    Description:
    The function first gets the current user and checks 
    their role. If the user is an organization, it redirects 
    them to the profile-org page. Otherwise, it gets the 
    recommended events based on the user's preferences and 
    the upcoming events based on the user's id. Then, it 
    passes these events as arguments to the render_template 
    function, which returns the index.html template with the 
    events data.
    """
    user = current_user

    if user.role == "organization":
        return redirect(url_for("/profile-org"))

    recommended_events = Event.get_recommended(user.preferences)
    upcoming_events = Event.get_upcoming(user.id)
    rec_events_dict_list = []
    for event in recommended_events:
        preferences = []
        for pref_id in event.targeted_preferences:
            preferences.append(Preference.get_preference_by_id(pref_id))
        rec_events_dict_list.append({
            "event": event,
            "preferences": preferences
        }) 

    return render_template('dashboard.html',
                           recommended_events=rec_events_dict_list,
                           upcoming_events=upcoming_events)     

""" Event Details form
    - Allows org users to create events
DATA: 
    - form: EventForm
"""


@main.route('/event/create', methods=['GET', 'POST'])
@login_required
@org_user_required
def event_form():
    """
    This function renders the event creation form 
    for the logged-in organization user and handles 
    the submission of the form.

    Parameters:
    None

    Returns:
    A rendered template of event_create.html with the 
    event form, or a redirection to the event details 
    page if the form is successfully submitted.

    Description:
    The function first creates an instance of the EventForm 
    class, which is a custom form for creating events. Then, 
    it checks if the form is validated on submit, which 
    means the user has filled in all the required fields 
    and clicked the submit button. If the form is validated, 
    it tries to create a new Event document with the data 
    from the form fields, such as location, organizer, event 
    date, title, description, and targeted preferences. It 
    also saves the new event to the database and updates the 
    preferences collection with the event count for each preference. 
    Then, it redirects the user to the event details page for 
    the newly created event. If the form is not validated or there 
    is an exception during the event creation, it passes the form 
    as an argument to the render_template function, which returns 
    the event_create.html template with the form data.
    """
    form = EventForm()
    if form.validate_on_submit():
        try:
            event = Event(location={"place": form.location_place.data, "address": form.location_address.data, "room": form.location_room.data},
                        organizer={"author_id": current_user.id,
                                    "name": current_user.name},
                        event_date={"from_date": form.from_date.data,
                                    "to_date": form.to_date.data},
                        registration_open_until=form.registration_open_until.data,
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
    return render_template('event_create.html', form=form, form_is_update=False)


""" Events detail route 
    - Takes in event id, and gives back event details
DATA:
    - event: Event
    - comments: Comment[]
    - user_is_attendee: boolean
    - form: RSVPForm | CancelRSVPForm
    - comment_form: CommentForm
This function handles the GET and POST requests for the event details page.
It requires the user to be logged in and takes the event id as an argument.
It renders the event details template with the following information:
- event: the Event object with the given id
- user_is_attendee: a boolean value indicating if the current user is attending the event
- comments: a list of Comment objects for the event
- form: either an RSVPForm or a CancelRSVPForm depending on the user's status
- comment_form: a CommentForm for the user to submit a comment and rating
If the event id is invalid, it renders the event not found template.
If the form or comment_form is submitted and validated, it updates the database accordingly and redirects to the same page.


"""
@main.route('/event/<id>', methods=['GET', 'POST'])
@login_required
def event_details(id):

    # get event
    event = Event.get_by_id(id=id)

    # Check if event is valid
    if not event:
        return render_template('errors/event_not_found.html')

    is_owner = False
    if str(event.organizer.author_id) == str(current_user.id):
        is_owner = True
    
    # check if registration still open
    registration_open = True
    if event.registration_open_until:
        if datetime.now() > event.registration_open_until:
            registration_open = False
    elif datetime.now() > event.event_date.from_date:
        registration_open = False
        


    # create RSVP form
    form = RSVPForm()

    comment_form = CommentForm()

    # check if user already is RSVP'ed, if so, change RSVPForm to CancelRSVPForm
    user_is_attendee = False
    for attendee in event.attendees:
        if attendee.author_id == current_user.id:
            user_is_attendee = True
            form = CancelRSVPForm()

    # get preferences data, list of Preference objects
    preferences = []
    for pref_id in event.targeted_preferences:
        preferences.append(Preference.get_preference_by_id(pref_id))
    
    # VALIDATE FORMS
    if form.validate_on_submit():
        if isinstance(form, RSVPForm):
            name = ""
            if current_user.role == "regular":
                name = f"{current_user.first_name} {current_user.last_name}"
            else:
                name = current_user.name
            Event.add_attendee(event.id, current_user.id, name)
            RegularUser.add_event(current_user.id, event.id)
            user_is_attendee = True
            form = CancelRSVPForm()
        elif isinstance(form, CancelRSVPForm):
            Event.remove_attendee(event.id, current_user.id)
            RegularUser.remove_event(current_user.id, event.id)
            user_is_attendee = False
            form = RSVPForm()
        return redirect(url_for("main.event_details", id=id))

    if comment_form.validate_on_submit():
        name = ""
        if current_user.role == "regular":
            name = f"{current_user.first_name} {current_user.last_name}"
        else:
            name = current_user.name
        if comment_form.rating.data:
            comment = Comment(event_id=id,
            author={"author_id":  current_user.id, "name": name}, 
            content=comment_form.content.data)
            comment = comment.save()
        else:
            comment = Comment(event_id=id,
                author={"author_id":  current_user.id, "name": name}, 
                content=comment_form.content.data,
                rating=comment_form.rating.data)
            comment = comment.save()
        return redirect(url_for("main.event_details", id=event.id))
        
    
    # get comments for the event
    comments = Comment.get_comments_by_event_id(id)

    reply_form = ReplyForm()
    return render_template('event_details.html', event=event, user_is_attendee=user_is_attendee, user_is_owner=is_owner, registration_open=registration_open, targeted_preferences=preferences, comments=comments, form=form, comment_form=comment_form, reply_form=reply_form)


""" Reply to a comment """
@main.route('/event/<event_id>/comment/reply/<comment_id>', methods=['POST'])
@login_required
def comment_reply(event_id, comment_id):
    comment = Comment.get_comment_by_id(id=comment_id)
    if not comment:
        return redirect(url_for("main.event_details", id=event_id))
    
    form = ReplyForm()

    if form.validate_on_submit():
        name = ""
        if current_user.role == "regular":
            name = f"{current_user.first_name} {current_user.last_name}"
        else:
            name = current_user.name
        reply = Reply(content=form.reply.data,
                      author={"author_id": current_user.id, "name": name})
        Comment.add_reply(comment_id, reply)
    return redirect(url_for("main.event_details", id=event_id, _anchor=comment_id))



""" Event Update form
    - Allows org users to create events
DATA: 
    - form: EventForm
"""


@main.route('/event/update/<id>', methods=['GET', 'POST'])
@login_required
@org_user_required
def event_update(id):
    """
    This function renders the event update form for the 
    logged-in organization user and handles the submission 
    of the form.

    Parameters:
    id: The id of the event to be updated.

    Returns:
    A rendered template of event_create.html with the event 
    form, or a redirection to the event details page if the 
    form is successfully submitted, or a redirection to the 
    error pages if the event is not valid or the user is not 
    authorized.

    Description:
    The function first gets the event document by the id 
    parameter and checks if it is valid. If not, it redirects 
    the user to the 404 error page. If the event is valid, 
    it checks if the user is the same as the organizer of 
    the event. If not, it redirects the user to the 403 
    error page. If the user is authorized, it creates an 
    instance of the EventForm class, which is a custom form 
    for updating events. It also sets the default values of 
    the form fields to the current values of the event fields, 
    such as location, event date, title, description, and 
    targeted preferences. Then, it validates the form on submit, 
    which means the user has filled in all the required fields 
    and clicked the submit button. If the form is validated, 
    it tries to update the event document with the new data 
    from the form fields using the update_one method. It also 
    updates the preferences collection with the event count 
    for each preference, by finding the newly added and removed 
    preferences and incrementing or decrementing the event 
    count accordingly. Then, it redirects the user to the 
    event details page for the updated event. If the form is 
    not validated or there is an exception during the event update, 
    it passes the form as an argument to the render_template function, 
    which returns the event_create.html template with the form data.
    """
    # get event
    event = Event.get_by_id(id=id)

    # Check if event is valid
    if not event:
        return render_template("errors/event_not_found.html")

    # Check if org user is right one
    if event.organizer.author_id != current_user.id:
        return render_template("errors/403.html")

    # Everything valid, set the form
    form = EventForm(location_place=event.location.place,
        locaton_address=event.location.address,
        location_room=event.location.room,
        from_date=event.event_date.from_date,
        to_date=event.event_date.to_date,
        registration_open_until=event.registration_open_until,
        description=event.description,
        title=event.title,
        targeted_preferences=[str(preference) for preference in event.targeted_preferences])


    if form.validate_on_submit():
        try:

            updated_event = Event.objects(id=event.id).update_one(location__place=form.location_place.data,
                location__address=form.location_address.data,
                location__room=form.location_room.data,
                event_date__from_date=form.from_date.data,
                event_date__to_date=form.to_date.data,
                registration_open_until=form.registration_open_until.data,
                title=form.title.data,
                description=form.description.data,
                targeted_preferences=form.targeted_preferences.data)

            # update preferences
            # convert old preferences to a list of strings
            old_preferences = [str(x) for x in event.targeted_preferences]
            # find newly added preferences
            new_preferences = [
                x for x in form.targeted_preferences.data if x not in old_preferences]

            # find removed preferences
            removed_preferences = [
                x for x in old_preferences if x not in form.targeted_preferences.data]

            # increase/decrease event count
            for preference in new_preferences:
                Preference.inc_event_count(preference)
            for preference in removed_preferences:
                Preference.inc_event_count(preference, inc=-1)

            return redirect(url_for(f'main.event_details', id=str(event.id)))
        except Exception as e:
            print(e)
            pass
    return render_template('event_create.html', event=event, form=form, form_is_update=True)


""" Event delete route
Deletes an event """


@main.route('/event/delete/<id>', methods=['GET'])
@login_required
@org_user_required
def event_delete(id):
    """
    This function deletes the event with the given id and 
    redirects the user to their profile page.

    Parameters:
    id: The id of the event to be deleted.

    Returns:
    A redirection to the profile page of the logged-in 
    organization user, or a redirection to the error pages 
    if the event is not valid or the user is not authorized.

    Description:
    The function first gets the event document by the id 
    parameter and checks if it is valid. If not, it redirects 
    the user to the 404 error page. If the event is valid, 
    it checks if the user is the same as the organizer of the 
    event. If not, it redirects the user to the 403 error page. 
    If the user is authorized, it deletes the event document from 
    the database using the delete method. Then, it redirects the 
    user to their profile page using the get_profile_org function 
    with the current user id.
    """
    # get event
    event = Event.get_by_id(id=id)

    # Check if event is valid
    if not event:
        return render_template("errors/event_not_found.html")

    # Check if org user is right one
    if event.organizer.author_id != current_user.id:
        return render_template("errors/403.html")

    # delete event
    event.delete()

    return redirect(url_for("main.get_profile_org", id=current_user.id))


""" Event listings route"""


@main.route('/event/search', methods=['GET', 'POST'])
@login_required
def event_search():

    #   get session if it exists
    page = request.args.get('page')
    search = request.args.get('search')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    preferences = request.args.get('preferences')
    items_per_page = request.args.get('items_per_page')


    # set page to 0 if not in args
    if page != None:
        page = int(page)
    else:
        page = 0
    if page < 0:
        page = 0

    if items_per_page != None:
        items_per_page = int(items_per_page)
    else:
        items_per_page = 10

    if preferences:
        preferences = preferences.split("__")
    
    form = EventSearchForm(search=search,
        preferences=preferences,
        items_per_page=items_per_page)
   
    # check form
    if form.validate_on_submit():
        if form.submit.data:
            # update variables
            page = 0
            search = form.search.data
            start_date = form.start_date.data
            end_date = form.end_date.data
            preferences = form.preferences.data
            items_per_page = int(form.items_per_page.data)

        if not preferences: 
            preferences = []
        return redirect(url_for("main.event_search", 
            search=search, 
            start_date=start_date, 
            end_date=end_date, 
            preferences= "__".join(preferences) if preferences else "", 
            items_per_page=items_per_page,
            page=page,
            _anchor='filtered-events'))
        
    else:
        if start_date:
            form.start_date.data = datetime.strptime(start_date, "%Y-%m-%d").date()
        if end_date:
            form.end_date.data = datetime.strptime(end_date, "%Y-%m-%d").date()
    # perform the search
    events, count = Event.search(search=search,
                                 start_date=start_date,
                                 end_date=end_date,
                                 preferences=preferences,
                                 page=page,
                                 items_per_page=items_per_page)

    max_pages = ceil(count/items_per_page)

    show_prev_button = True
    show_next_button = True
    if page <= 0:
        show_prev_button = False
    if page >= max_pages-1:
        show_next_button = False
    return render_template(f'event_list.html', events=events, form=form, page=page, max_pages=max_pages, count=count, show_next_button=show_next_button, show_prev_button=show_prev_button)


""" View Profile route
 """
@main.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """
    This function renders the profile page for the logged-in 
    user and shows their event summary.

    Parameters:
    None

    Returns:
    A rendered template of profile.html with the user data and 
    the future and past events, or a redirection to the profile-org 
    page if the user is an organization.

    Description:
    The function first gets the current user and checks their role. 
    If the user is an organization, it redirects them to the 
    profile-org page using the get_profile_org function with the 
    user id. If the user is a regular user, it gets the future 
    and past events that the user has registered for by calling 
    the get_summary_from_list_future and get_summary_from_list_past 
    functions of the Event class with the user's registered_events list. 
    These functions return a list of event summaries, which are 
    dictionaries with the event id, title, date, and image. Then, 
    it passes the user, the future_events, and the past_events as 
    arguments to the render_template function, which returns the 
    profile.html template with the data.

    """
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
    """
    This function renders the profile page for the organization 
    user with the given id and shows their event summary.

    Parameters:
    id: The id of the organization user to be displayed.

    Returns:
    A rendered template of profile_org.html with the user 
    data and the future and past events, or a redirection 
    to the 404 error page if the user is not valid.

    Description:
    The function first gets the organization user document by 
    the id parameter and checks if it is valid. If not, it 
    redirects the user to the 404 error page. If the user is 
    valid, it checks if the user id is the same as the current 
    user id and sets the current_user_is_specified variable to 
    True or False accordingly. This variable is used to determine 
    if the profile page is for the current user or another user. 
    Next, it gets the future and past events that the user has 
    organized by calling the get_organization_events_future and 
    get_organization_events_past functions of the Event class 
    with the user id. These functions return a list of event 
    documents that match the criteria. Then, it passes the user, 
    the current_user_is_specified, the future_events, and the 
    past_events as arguments to the render_template function, 
    which returns the profile_org.html template with the data.

    """
    user = OrganizationUser.get_by_id(id)

    if user == None:
        return render_template("errors/user_not_found.html")

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
    """
    This function renders the profile edit page for the logged-in 
    regular user and handles the submission of the update form.

    Parameters:
    None

    Returns:
    A rendered template of update_profile.html with the update 
    form and the user data, or a redirection to the profile 
    page if the form is successfully submitted, or a redirection 
    to the update_profile_organization page if the user is an organization.

    Description:
    The function first gets the current user and checks their role. 
    If the user is an organization, it redirects them to the 
    update_profile_organization page using the update_profile_organization 
    function with the user id. If the user is a regular user, 
    it creates an instance of the UpdateRegularUserForm class, 
    which is a custom form for updating the user's first name, 
    last name, and preferences. It also sets the default values 
    of the form fields to the current values of the user fields. 
    Then, it validates the form on submit, which means the user 
    has filled in all the required fields and clicked the submit 
    button. If the form is validated, it tries to update the user 
    document and the user object with the new data from the form 
    fields. It also commits the changes to the database using the 
    update_one method. Then, it redirects the user to their profile 
    page using the get_profile function. If the form is not validated 
    or there is an exception during the update, it flashes a message 
    to the user and passes the form and the user as arguments to the 
    render_template function, which returns the update_profile.html 
    template with the data.
    """

    user = current_user
    if user.role == "organization":
        return redirect(url_for("main.update_profile_organization"))

    form = UpdateRegularUserForm(
        first_name=user.first_name, last_name=user.last_name, preferences=user.preferences)

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
@main.route("/profile-org/edit", methods=['GET', 'POST'])
@login_required
def update_profile_organization():
    """
    This function renders the profile edit page for the 
    logged-in organization user and handles the submission 
    of the update form.

    Parameters:
    None

    Returns:
    A rendered template of update_profile_org.html with 
    the update form and the user data, or a redirection 
    to the profile page if the form is successfully submitted, 
    or a redirection to the update_profile_regular page if the 
    user is a regular user.

    Description:
    The function first gets the current user and checks their role. 
    If the user is a regular user, it redirects them to the update_profile_regular 
    page using the update_profile_regular function with the user id. 
    If the user is an organization user, it creates an instance of the 
    UpdateOrganizationUserForm class, which is a custom form for updating 
    the user's name. It also sets the default value of the form field 
    to the current value of the user's name. Then, it validates the form 
    on submit, which means the user has filled in the required field and 
    clicked the submit button. If the form is validated, it tries to update 
    the user document and the user object with the new data from the form 
    field. It also commits the changes to the database using the update_one 
    method. Then, it redirects the user to their profile page using the 
    get_profile function. If the form is not validated or there is an 
    exception during the update, it flashes a message to the user and 
    passes the form and the user as arguments to the render_template 
    function, which returns the update_profile_org.html template with 
    the data.
    """
    form = UpdateOrganizationUserForm()
    user = current_user
    if user.role == "regular":
        return redirect(url_for("main.update_profile_regular"))

    if form.validate_on_submit():
        try:
            user.name = form.name.data
            OrganizationUser.objects(
                id=user.id).update_one(name=form.name.data)
            return redirect(url_for("main.get_profile"))
        except:
            flash("An error occurred while updating your profile")

    return render_template('update_profile_org.html', form=form, user=user)



@main.route("/event/ics/<id>", methods=['GET'])
@login_required
def calendar(id):

    # get event
    event = Event.get_by_id(id=id)

    # Check if event is valid
    if not event:
        return render_template('event_not_found.html')
    
    # Create a Calendar object
    cal = Calendar()
    cal.add("prodid", "-//My calendar product//mxm.dk//")
    cal.add("version", "2.0")
    cal.add("method", "PUBLISH")

    # Create an Event object
    ievent = iEvent()
    ievent.add("summary", event.title)
    ievent.add("description", event.description)
    ievent.add("dtstart", event.event_date.from_date)
    ievent.add("dtend", event.event_date.to_date)
    # event.add("dtend", datetime(2023, 11, 9, 17, 0, 0, tzinfo=UTC))
    ievent.add("dtstamp", datetime.now())
    ievent.add("location", event.location.address)
    ievent.add("uid", "20231109T160000Z-123456@mxm.dk")

    # Add the Event object to the Calendar object
    cal.add_component(ievent)

    # Convert the Calendar object to a string
    cal_str = cal.to_ical()

    # Create a Flask response object
    response = make_response(cal_str)
    # Set the content type and disposition headers
    response.headers["Content-Type"] = "text/calendar"
    response.headers["Content-Disposition"] = f"attachment; filename={event.title}.ics"

    # Return the response object
    return response