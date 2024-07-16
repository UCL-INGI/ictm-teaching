from decorators import login_required
from db import db, User, Course, PreferenceAssignment, Teacher, Researcher, Organization
from flask import Blueprint, render_template, flash, current_app, url_for, request, make_response, redirect, session, \
    Flask, jsonify
from util import get_current_year

assignment_bp = Blueprint('assignment', __name__)


@assignment_bp.route('/assignments', methods=['GET'])
@login_required
def assignments():
    return render_template('assignment.html')


def serialize_model(model):
    """Converts a SQLAlchemy model object into a dictionary."""
    return {column.name: getattr(model, column.name) for column in model.__table__.columns}


@assignment_bp.route('/load_data', methods=['GET'])
@login_required
def load_data():
    current_year = get_current_year()
    courses = db.session.query(Course).order_by(Course.quadri).all()
    users = db.session.query(User).filter_by(admin=False, active=True).all()
    teachers = db.session.query(Teacher).all()
    researchers = db.session.query(Researcher).all()
    preferences = db.session.query(PreferenceAssignment).all()
    organizations = db.session.query(Organization).all()

    data = {
        'courses': [serialize_model(course) for course in courses if course.year == current_year],
        'users': [serialize_model(user) for user in users],
        'teachers': [serialize_model(teacher) for teacher in teachers],
        'researchers': [serialize_model(researcher) for researcher in researchers],
        'preferences': [serialize_model(preference) for preference in preferences],
        'organizations': [serialize_model(organization) for organization in organizations],
        'current_year': current_year
    }

    return jsonify(data)


@assignment_bp.route('/publish_assignments', methods=['POST, GET'])
@login_required
def publish_assignments():
    pass