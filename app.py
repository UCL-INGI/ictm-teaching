from auth import auth_bp
from user import user_bp
from course import course_bp
from config import config_bp
from course_preference import course_preference_bp
from db import db, Configuration, Organization
from decorators import *
from flask import Flask, render_template, session
import json

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Core blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(user_bp, url_prefix="/user")
app.register_blueprint(course_bp, url_prefix="/course")
app.register_blueprint(config_bp, url_prefix="/config")
app.register_blueprint(course_preference_bp, url_prefix="/course_preference")


def get_configurations():
    if session.get('logged_in'):
        return db.session.query(Configuration).all()
    else:
        return []


def get_organization():
    if session.get('logged_in'):
        return db.session.query(Organization).all()
    else:
        return []


@app.context_processor
def inject_configurations():
    return dict(configurations=get_configurations(), organizations_code=get_organization())


# Routes
@app.route('/')
def index():  # put application's code here
    if session and session['logged_in']:
        return render_template("home.html")
    else:
        return render_template("index.html")


@app.route('/private')
@login_required
def private():
    return render_template("private.html")


if __name__ == '__main__':
    app.run()
