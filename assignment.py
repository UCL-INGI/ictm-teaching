from decorators import login_required, check_access_level
from db import db, User, Course, PreferenceAssignment, Teacher, Researcher, Organization, \
    ResearcherSupervisor, Role, Assignment, AssignmentLine
from flask import Blueprint, render_template, flash, current_app, url_for, request, make_response, redirect, session, \
    Flask, jsonify
from util import get_current_year
from enums import DEFAULT_MAX_LOAD

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
@check_access_level(Role.ADMIN)
def load_data():
    current_year = get_current_year()

    courses = [serialize_model(course) for course in
               db.session.query(Course).filter_by(year=current_year).order_by(Course.quadri).all() or []]
    supervisors = [serialize_model(supervisor) for supervisor in db.session.query(ResearcherSupervisor).all() or []]
    teachers = {teacher.id: serialize_model(teacher) for teacher in
                db.session.query(Teacher).filter_by(course_year=current_year).all() or []}
    researchers = {researcher.id: serialize_model(researcher) for researcher in
                   db.session.query(Researcher).all() or []}
    preferences = {preference.id: serialize_model(preference) for preference in
                   db.session.query(PreferenceAssignment).filter_by(course_year=current_year).all() or []}
    organizations = {organization.id: serialize_model(organization) for organization in
                     db.session.query(Organization).all() or []}

    saved_data = db.session.query(Assignment).order_by(Assignment.id.desc()).first()
    saved_data_serialized = [serialize_model(line) for line in saved_data.assignment_lines] if saved_data else []

    user_ids = [user.id for user in saved_data.users] if saved_data else []
    users = {user.id: serialize_model(user) for user in db.session.query(User).filter(
        (User.active == True) | (User.id.in_(user_ids))
    ).all() or []}


    data = {
        'courses': courses,
        'users': users,
        'supervisors': supervisors,
        'teachers': teachers,
        'researchers': researchers,
        'preferences': preferences,
        'organizations': organizations,
        'current_year': current_year,
        'saved_data': saved_data_serialized,
        'MAX_LOAD': DEFAULT_MAX_LOAD,
    }

    return jsonify(data)


@assignment_bp.route('/publish_assignments', methods=['POST'])
@login_required
def publish_assignments():
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    current_year = get_current_year()
    is_draft = data.get('isDraft')

    assignment = Assignment(is_draft=is_draft)
    db.session.add(assignment)
    db.session.commit()

    for item in data.get('data'):
        user_data = item.get('userData')
        course_data = item.get('courseData')

        if course_data and user_data:
            for id, properties in course_data.items():
                try:
                    assignment_line = AssignmentLine(course_id=id, course_year=current_year,
                                                     user_id=user_data.get('user_id'),
                                                     load_q1=user_data.get('load_q1'), load_q2=user_data.get('load_q2'),
                                                     position=properties.get('position'),
                                                     comment=properties.get('comment'),
                                                     assignment_id=assignment.id)
                    db.session.add(assignment_line)
                except Exception as e:
                    return jsonify({"error": str(e)}), 400

            db.session.commit()

    db.session.commit()

    return jsonify({"message": "Assignments published successfully"}), 200
