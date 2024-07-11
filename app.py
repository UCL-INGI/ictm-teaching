import datetime

import jinja2.defaults

from auth import auth_bp
from user import user_bp
from course import course_bp
from config import config_bp
from course_preference import course_preference_bp
from db import db, Configuration, Organization, User, Course
from decorators import *
from flask import Flask, render_template, session, request
from enums import *
from util import get_current_year
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
    return db.session.query(Configuration).all()


def get_organization():
    return db.session.query(Organization).all()


@app.context_processor
def inject_configurations():
    return dict(configurations=get_configurations(), organizations_code=get_organization(), quadri=QUADRI, language=LANGUAGES, researcher_type=RESEARCHERS_TYPE, dynamic_year=get_current_year())


# Routes
@app.route('/')
def index():  # put application's code here
    if session and session['logged_in']:
        user = db.session.query(User).filter_by(email=session['email']).first()
        courses = db.session.query(Course).all()
        teachers_course = {
            course
            for course in courses
            for teacher in course.course_teacher if teacher.user_id == user.id
        }
        return render_template("home.html", user=user, courses=teachers_course)
    else:
        return redirect(url_for("auth.login"))


if __name__ == '__main__':
    app.run()
