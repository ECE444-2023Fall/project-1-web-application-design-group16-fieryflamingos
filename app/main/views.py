from datetime import datetime
from flask import render_template, session, redirect, url_for
from flask_login import _get_user, login_required
from . import main
# from .forms import NameForm
from .. import db
from ..models import User, Event


""" Dashboard:
Data: 
    Recommended Events
    Upcoming Events
"""
@main.route('/', methods=['GET'])
@login_required
def index():
    user_id = _get_user()
    user = User.objects(id=user_id).get()

    recommended_events = Event.get_recommended(user.preferences)
    upcoming_events = Event.get_upcoming(user_id)
    
    return render_template('index.html',
                            recommended_events=recommended_events,
                            upcoming_events=upcoming_events)