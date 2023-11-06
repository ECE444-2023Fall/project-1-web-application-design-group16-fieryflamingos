from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, abort
from flask_login import current_user, login_required
from . import main
# from .forms import NameForm
from .. import db
from ..models import User, RegularUser, OrganizationUser, Event, Preference, Comment
from .forms import EventForm, RSVPForm, CancelRSVPForm, EventSearchForm, UpdateRegularUserForm, UpdateOrganizationUserForm, CommentForm
from functools import wraps

from math import ceil


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

    return render_template('index.html',
                           recommended_events=recommended_events,
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
        return render_template('event_not_found.html')

    # create RSVP form
    form = RSVPForm()

    comment_form = CommentForm()

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
        comment = Comment(event_id=id,
            author={"author_id":  current_user.id, "name": name}, 
            content=comment_form.content.data,
            rating=comment_form.rating.data)
        comment = comment.save()
    
    # get comments for the event
    comments = Comment.get_comments_by_event_id(id)
    return render_template('event_details.html', event=event, user_is_attendee=user_is_attendee, comments=comments, form=form, comment_form=comment_form)


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
        return render_template("errors/404.html")

    # Check if org user is right one
    if event.organizer.author_id != current_user.id:
        return render_template("errors/403.html")

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
    return render_template('event_create.html', form=form)


""" Event delete route
Deletes an event """


@main.route('/event/delete/<id>', methods=['POST'])
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
        return render_template("errors/404.html")

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
    """
    This function renders the event search page for the 
    logged-in user and handles the search form and pagination.

    Parameters:
    None

    Returns:
    A rendered template of event_list.html with the search 
    form, the search results, and the pagination.

    Description:
    The function first creates an instance of the EventSearchForm 
    class, which is a custom form for searching events by keywords, 
    date range, and preferences. Then, it tries to get the session 
    variables for the search parameters, such as page, search, 
    from_date, to_date, preferences, items_per_page, and max_pages. 
    These variables are used to store the user's search input and 
    the pagination state. If the session variables are not set, 
    it assigns some default values to them. Next, it validates the 
    form on submit, which means the user has filled in the form 
    fields and clicked the submit, next page, or prev page buttons. 
    If the form is validated, it checks which button was clicked. 
    If the submit button was clicked, it updates the session variables 
    with the new form data and resets the page to 0. If the next page 
    button was clicked and the page is not the last one, it increments 
    the page by 1 and updates the session variable. If the prev page 
    button was clicked and the page is not the first one, it decrements 
    the page by 1 and updates the session variable. Then, it calls the 
    search method of the Event class with the search parameters and gets 
    the events and the count of the matching events. It also calculates 
    the max_pages by dividing the count by the items_per_page and updates 
    the session variable. Finally, it passes the events, the form, the page, 
    and the max_pages as arguments to the render_template function, 
    which returns the event_list.html template with the data.

    """
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
        return render_template("errors/404.html")

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
    user = current_user
    if user.role == "regular":
        return redirect(url_for("main.update_profile_regular"))

    form = UpdateOrganizationUserForm(name=user.name)

    if form.validate_on_submit():
        try:
            user.name = form.name.data
            OrganizationUser.objects(
                id=user.id).update_one(name=form.name.data)
            return redirect(url_for("main.get_profile"))
        except:
            flash("An error occurred while updating your profile")

    return render_template('update_profile_org.html', form=form, user=user)
