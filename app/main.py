from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_moment import Moment


app = Flask(__name__)
moment = Moment(app)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = '23J1CJIO23NO12IJL1NL'



@app.route('/', methods=['GET', 'POST'])
def index():
   
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html'), 500


if __name__ == "__main__": 
    app.run(host ='0.0.0.0', port = 5000, debug = True)