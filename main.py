from flask import Flask, render_template, session, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, ValidationError


app = Flask(__name__)
moment = Moment(app)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = '23J1CJIO23NO12IJL1NL'



@app.route('/', methods=['GET', 'POST'])
def index():
   
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error-pages/404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error-pages/500.html'), 500


if __name__ == "__main__": 
    app.run(host ='0.0.0.0', port = 5000, debug = True)