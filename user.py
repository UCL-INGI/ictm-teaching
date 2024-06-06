from decorators import login_required
from db import db, User, Researcher, Course, Configuration, PreferenceAssignment
from flask import Blueprint, render_template, flash, url_for, request, make_response, redirect, session, \
    Flask
import re, json

user_bp = Blueprint('user', __name__)

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)
with open('config.json') as config_file:
    app.config.update(json.load(config_file))

researcher_types = ['Phd', 'Postdoc', 'Teaching assistant', 'Other']


def get_default_max_load(researcher_type):
    defaults = {
        'Phd': 2,
        'Postdoc': 1,
        'Teaching assistant': 4,
        'Other': 1,
    }
    return defaults.get(researcher_type, 0)


@user_bp.route('/register')
@login_required
def register():
    all_users = db.session.query(User).filter(User.admin == 0, User.is_teacher == 1, User.active == 1).all()
    return render_template('register.html', supervisors=all_users, researcher_type=researcher_types)


def is_valid_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None


def contains_valid_characters(name):
    name_regex = r'^\w+$'
    return re.match(name_regex, name) is not None


@user_bp.route('/add_user', methods=['POST'])
@login_required
def add_user():
    form = request.form
    if not form:
        return make_response("Problem with form request", 500)

    name = request.form['name']
    first_name = request.form['first_name']
    email = request.form['email']
    organization_code = request.form['organization_code']
    is_teacher = 'is_teacher' in request.form
    is_researcher = 'is_researcher' in request.form
    supervisor_id = request.form.get('supervisor') if is_researcher else None
    researcher_type = request.form['researcher_type'] if is_researcher else None

    # Make email unique
    is_user_exist = db.session.query(User).filter(User.email == email).first()

    if not contains_valid_characters(name):
        return make_response("Invalid characters in name", 400)
    if not contains_valid_characters(first_name):
        return make_response("Invalid characters in first name", 400)
    if email != '' and not is_valid_email(email):
        return make_response("Invalid email format", 400)

    try:
        new_user = User(name=name, first_name=first_name, email=email, is_teacher=is_teacher,
                        is_researcher=is_researcher, supervisor_id=supervisor_id,
                        organization_id=organization_code)
        db.session.add(new_user)
        db.session.commit()
        if is_researcher:
            max_load = get_default_max_load(researcher_type)
            new_researcher = Researcher(user_id=new_user.id, researcher_type=researcher_type,
                                        max_loads=max_load)
            db.session.add(new_researcher)
            db.session.commit()
    except:
        db.session.rollback()
        raise

    return redirect(url_for("user.register"))


@user_bp.route('/profile')
@login_required
def profile():
    email = session["email"]
    current_year = session["current_year"]
    user = db.session.query(User).filter(User.email == email).first()
    researcher = db.session.query(Researcher).filter(Researcher.user_id == user.id).first()

    preferences = []
    if researcher:
        preferences = db.session.query(PreferenceAssignment).filter_by(researcher_id=researcher.id,
                                                                       course_year=current_year).all()

    courses = db.session.query(Course).filter(Course.year == current_year,
                                              Course.organizations.contains(user.organization)
                                              ).all()

    return render_template("profile.html", user=user, researcher=researcher, courses=courses, preferences=preferences)


@user_bp.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    form = request.form
    if not form:
        return make_response("Problem with form request", 500)

    name = request.form['name']
    first_name = request.form['first_name']
    email = request.form['email']

    if not contains_valid_characters(name):
        return make_response("Invalid characters in name", 400)
    if not contains_valid_characters(first_name):
        return make_response("Invalid characters in first name", 400)
    if email != '' and not is_valid_email(email):
        return make_response("Invalid email format", 400)

    user = db.session.query(User).filter(User.email == email).first()
    if user:
        try:
            user.first_name = first_name
            user.name = name
            db.session.commit()
            session["first_name"] = first_name
            session["name"] = name
        except Exception as e:
            db.session.rollback()
        return redirect(url_for("user.profile"))
    else:
        flash('User not found', 'danger')


@user_bp.route('/users/<string:user_type>')
@login_required
def users(user_type):
    base_query = db.session.query(User).filter(User.admin == 0)

    if user_type == 'teacher':
        base_query = base_query.filter(User.is_teacher == 1, User.active == 1)
    elif user_type == 'researcher':
        base_query = base_query.filter(User.is_researcher == 1, User.active == 1)
    elif user_type == 'archived':
        base_query = base_query.filter(User.active == 0)

    all_users = base_query.all()
    return render_template('users.html', users=all_users, user_type=user_type)


@user_bp.route('/profile/<int:user_id>')
@login_required
def user_profile(user_id):
    all_users = db.session.query(User).filter(User.admin == 0, User.is_teacher == 1, User.active == 1).all()
    my_user = db.session.query(User).filter_by(id=user_id).first()
    researcher = db.session.query(Researcher).filter(Researcher.user_id == my_user.id).first()
    current_year = session["current_year"]

    preferences = []
    if researcher:
        preferences = db.session.query(PreferenceAssignment).filter_by(researcher_id=researcher.id,
                                                                       course_year=current_year).all()
    if my_user:
        return render_template('user_profile.html', user=my_user, supervisors=all_users, researcher=researcher,
                               researcher_type=researcher_types, preferences=preferences)
    else:
        return make_response("The user is not found", 500)


@user_bp.route('/update_user_profile', methods=['POST'])
@login_required
def update_user_profile():
    form = request.form
    if form:
        name = request.form['name']
        first_name = request.form['first_name']
        email = request.form['email']
        user_id = request.form['user_id']
        organization_code = request.form['organization_code']
        is_teacher = 'is_teacher' in request.form
        is_researcher = 'is_researcher' in request.form
        supervisor_id = request.form.get('supervisor') if is_researcher else None
        researcher_type = request.form['researcher_type'] if is_researcher else None
        max_loads = request.form['max_load'] if is_researcher else None

        user = db.session.query(User).filter(User.id == user_id).first()
        researcher = db.session.query(Researcher).filter(Researcher.user_id == user.id).first()
        if user:
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
            return redirect(url_for("user.user_profile", user_id=user_id))
        else:
            flash('User not found', 'danger')
    else:
        return make_response("Problem with form request", 500)


@user_bp.route('/disable/<int:user_id>')
@login_required
def disable(user_id):
    try:
        user = db.session.query(User).filter_by(id=user_id).first()
        user.active = 0
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

    return redirect(url_for("user.users", user_type='archived'))


@user_bp.route('/enable/<int:user_id>')
@login_required
def enable(user_id):
    try:
        user = db.session.query(User).filter_by(id=user_id).first()
        user.active = 1
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

    return redirect(url_for("user.users", user_type='archived'))
