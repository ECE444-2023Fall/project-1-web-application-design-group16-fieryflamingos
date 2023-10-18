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