from datetime import datetime
from flask import render_template, session, redirect, url_for
from . import main
# from .forms import NameForm
from .. import db
from ..models import User


@main.route('/', methods=['GET', 'POST'])
def index():
    print("in index route...")
    return render_template('index.html',
                            current_time=datetime.utcnow())

""" Event Details form"""


""" Events detail route """



""" Event listings route
query parameters in the url """

""" Dashboard route
query parameters in the url """
@main.route('/dashboard/<user_id>', methods=['GET'])
def dashboard(user_id):
    return render_template('dashboard.html', user=user_id)




""" Sign in route """
@main.route('/sign-in', methods=['GET'])
def sign_in():
    return render_template('sign-in.html')


""" Register route """
@main.route('/register', methods=['GET'])
def register():
    return render_template('register.html')


""" User Profile route """