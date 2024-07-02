from decorators import login_required
from db import db, User, Researcher, Course, PreferenceAssignment
from flask import Blueprint, render_template, flash, url_for, request, make_response, redirect, session, \
    Flask
from enums import DEFAULT_MAX_LOAD
import re, json

user_bp = Blueprint('user', __name__)


@user_bp.route('/register')
@login_required
def register():
    current_year = int(request.args.get('current_year'))
    all_users = db.session.query(User).filter(User.admin == 0, User.is_teacher == 1, User.active == 1).all()
    return render_template('register.html', supervisors=all_users, current_year=current_year)


def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None


def contains_valid_characters(name):
    name_regex = r'^[\w\s-]+$'
    return re.match(name_regex, name) is not None


@user_bp.route('/add_user', methods=['POST'])
@login_required
def add_user():
    form = request.form
    if not form:
        return make_response("Problem with form request", 500)

    current_year = int(request.args.get('current_year'))
    name = request.form['name']
    first_name = request.form['first_name']
    email = request.form['email']
    if not contains_valid_characters(name):
        return make_response("Invalid characters in name", 400)
    if not contains_valid_characters(first_name):
        return make_response("Invalid characters in first name", 400)
    if email != '' and not is_valid_email(email):
        return make_response("Invalid email format", 400)

    organization_code = request.form['organization_code']
    is_teacher = 'is_teacher' in request.form
    is_researcher = 'is_researcher' in request.form
    supervisor_id = request.form.get('supervisor') if is_researcher else None
    researcher_type = request.form['researcher_type'] if is_researcher else None

    try:
        new_user = User(name=name, first_name=first_name, email=email, is_teacher=is_teacher,
                        is_researcher=is_researcher, supervisor_id=supervisor_id,
                        organization_id=organization_code)
        db.session.add(new_user)
        db.session.commit()
        if is_researcher:
            all_loads = DEFAULT_MAX_LOAD
            max_load = all_loads.get(researcher_type, 0)
            new_researcher = Researcher(user_id=new_user.id, researcher_type=researcher_type,
                                        max_loads=max_load)
            db.session.add(new_researcher)
            db.session.commit()
    except:
        db.session.rollback()
        raise

    return redirect(url_for("user.register", current_year=current_year))


@user_bp.route('/users/<string:user_type>')
@login_required
def users(user_type):
    base_query = db.session.query(User).filter(User.admin == 0)
    current_year = int(request.args.get('current_year'))

    if user_type == 'teacher':
        base_query = base_query.filter(User.is_teacher == 1, User.active == 1)
    elif user_type == 'researcher':
        base_query = base_query.filter(User.is_researcher == 1, User.active == 1)
    elif user_type == 'archived':
        base_query = base_query.filter(User.active == 0)

    all_users = base_query.all()
    return render_template('users.html', users=all_users, user_type=user_type, current_year=current_year)


@user_bp.route('/profile/<int:user_id>')
@login_required
def user_profile(user_id):
    all_users = db.session.query(User).filter(User.admin == 0, User.is_teacher == 1, User.active == 1).all()
    my_user = db.session.query(User).filter_by(id=user_id).first()
    researcher = db.session.query(Researcher).filter(Researcher.user_id == my_user.id).first()
    current_year = int(request.args.get('current_year'))
    my_profile = my_user.email == session["email"]

    preferences = []
    if researcher:
        preferences = db.session.query(PreferenceAssignment).filter_by(researcher_id=researcher.id,
                                                                       course_year=current_year).all()
    courses = []
    if my_profile and my_user.organization:
        courses = db.session.query(Course).filter(Course.year == current_year,
                                                  Course.organizations.contains(my_user.organization)
                                                  ).all()

    if my_user is None:
        return make_response("The user is not found", 404)

    return render_template('user_profile.html', user=my_user, supervisors=all_users, researcher=researcher,
                           courses=courses, preferences=preferences,
                           my_profile=my_profile, current_year=current_year)


@user_bp.route('/update_user_profile', methods=['POST'])
@login_required
def update_user_profile():
    form = request.form
    if not form:
        return make_response("Problem with form request", 500)

    current_year = int(request.args.get('current_year'))
    name = request.form['name']
    first_name = request.form['first_name']
    email = request.form['email']

    if not contains_valid_characters(name):
        return make_response("Invalid characters in name", 400)
    if not contains_valid_characters(first_name):
        return make_response("Invalid characters in first name", 400)
    if email != '' and not is_valid_email(email):
        return make_response("Invalid email format", 400)

    user_id = request.form['user_id']
    organization_code = None if request.form['organization_code'] == 'None' else request.form['organization_code']
    is_teacher = 1 if 'is_teacher' in request.form else 0
    is_researcher = 1 if 'is_researcher' in request.form else 0
    supervisor_id = request.form.get('supervisor') if is_researcher else None
    researcher_type = request.form['researcher_type'] if is_researcher else None
    max_loads = request.form['max_load'] if is_researcher else None

    user = db.session.query(User).filter(User.id == user_id).first()
    researcher = db.session.query(Researcher).filter(Researcher.user_id == user.id).first()
    if user is None:
        return make_response("User not found", 404)

    try:
        user.first_name = first_name
        user.name = name
        user.email = email
        user.organization_id = organization_code
        user.is_teacher = is_teacher
        user.is_researcher = is_researcher
        user.supervisor_id = supervisor_id
        if is_researcher:
            researcher.max_loads = max_loads
            researcher.researcher_type = researcher_type
        db.session.commit()
    except Exception as e:
        db.session.rollback()
    return redirect(url_for("user.user_profile", user_id=user_id, current_year=current_year))


@user_bp.route('/disable/<int:user_id>')
@login_required
def disable(user_id):
    user_type = request.args.get('user_type')
    current_year = int(request.args.get('current_year'))
    try:
        user = db.session.query(User).filter_by(id=user_id).first()
        if user is None:
            return make_response("User not found", 404)

        user.active = 0
        db.session.commit()
        flash("User deactivated successfully.", "success")
    except ValueError as e:
        db.session.rollback()
        flash(str(e), "error")
    except Exception as e:
        db.session.rollback()
        raise e

    return redirect(url_for("user.users", user_type=user_type, current_year=current_year))


@user_bp.route('/enable/<int:user_id>')
@login_required
def enable(user_id):
    current_year = int(request.args.get('current_year'))
    try:
        user = db.session.query(User).filter_by(id=user_id).first()
        if user is None:
            return make_response("User not found", 404)

        user.active = 1
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

    return redirect(url_for("user.users", user_type='archived', current_year=current_year))
