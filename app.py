import datetime

import jinja2.defaults
from sqlalchemy import and_
from sqlalchemy.orm import joinedload

from auth import auth_bp
from user import user_bp
from course import course_bp
from config import config_bp
from course_preference import course_preference_bp
from assignment import assignment_bp
from db import db, Year, Organization, User, Course, Teacher, Researcher, Evaluation, AssignmentPublished
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
app.register_blueprint(assignment_bp, url_prefix="/assignment")


def get_configurations():
    return db.session.query(Year).order_by(Year.year.asc()).all()


def get_organization():
    return db.session.query(Organization).all()


def is_researcher():
    return db.session.query(Researcher).filter_by(user_id=session['user_id']).first() is not None


@app.context_processor
def inject_configurations():
    return dict(configurations=get_configurations(), organizations_code=get_organization(), quadri=QUADRI,
                language=LANGUAGES, researcher_type=RESEARCHERS_TYPE, dynamic_year=get_current_year(),
                tasks=TASK, evaluation_hour=EVALUATION_HOUR, workloads=WORKLOAD, is_researcher=is_researcher())


# Routes
@app.route('/')
@login_required
def index():
    current_year = get_current_year()
    year = db.session.query(Year).filter_by(year=current_year).first()
    user = db.session.query(User).filter_by(email=session['email']).first()
    researcher = db.session.query(Researcher).filter_by(user_id=user.id).first()
    teacher = db.session.query(Teacher).filter_by(user_id=user.id).first() if user.is_teacher else None

    # Teacher data
    courses_teacher = []
    researcher_supervised = []

    # Researcher data
    researcher_courses = []
    researcher_current_course = []
    researcher_evaluations = []

    if teacher:
        # Get the teacher's courses
        courses_teacher = db.session.query(Course).join(Teacher).filter(
            and_(Teacher.user_id == user.id, Course.year == current_year)
        ).all()

        users_supervised = teacher.user.researchers
        for researcher_supervisor in users_supervised:
            # Filter assigned_courses wth current year
            researcher = researcher_supervisor.researcher
            current_year_courses = [
                course for course in researcher.assigned_courses if course.year == current_year
            ]
            researcher.current_assigned_courses = current_year_courses
            researcher_supervised.append(researcher)

    elif researcher:
        # Get the courses where the researcher is assigned
        researcher_courses = researcher.assigned_courses
        researcher_current_course = [
            course for course in researcher_courses if course.year == current_year
        ]
        researcher_evaluations = researcher.user.evaluations

    return render_template("home.html", user=user, courses_teacher=courses_teacher,
                           researcher_supervised=researcher_supervised, researcher_courses=researcher_courses,
                           researcher_current_course=researcher_current_course, evaluations=researcher_evaluations)


if __name__ == '__main__':
    app.run()
