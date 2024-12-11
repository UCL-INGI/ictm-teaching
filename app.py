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
    teacher = db.session.query(Teacher).filter_by(user_id=user.id).first() if user.is_teacher else None

    data = {}

    if user.is_teacher:
        # Populate teacher-specific data
        teacher_courses = db.session.query(Course).join(Teacher).filter(
            and_(Teacher.user_id == user.id, Course.year == current_year)
        ).all()

        supervised_researchers = []
        for researcher_supervisor in teacher.user.researchers:
            researcher = researcher_supervisor.researcher
            current_year_courses = [
                course for course in researcher.assigned_courses if course.year == current_year
            ]
            researcher.current_assigned_courses = current_year_courses
            supervised_researchers.append(researcher)

        data.update({
            "teacher_courses": teacher_courses,
            "supervised_researchers": supervised_researchers
        })

    # To change if we decide to use session to store roles
    elif is_researcher():
        researcher = db.session.query(Researcher).filter_by(user_id=user.id).first()
        # Populate researcher-specific data
        researcher_courses = researcher.assigned_courses
        current_courses = [
            course for course in researcher_courses if course.year == current_year
        ]
        evaluations = researcher.user.evaluations

        data.update({
            "researcher_courses": researcher_courses,
            "current_courses": current_courses,
            "researcher_evaluations": evaluations
        })

    return render_template("home.html", user=user, data=data)


if __name__ == '__main__':
    app.run()
