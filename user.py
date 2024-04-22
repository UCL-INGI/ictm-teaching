from decorators import login_required
from db import db, User
from flask import Blueprint, render_template, flash, current_app, url_for, request, make_response, redirect, session
import re

user_bp = Blueprint('user', __name__)


@user_bp.route('/register')
@login_required
def register():
    return render_template('register.html')


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

    if not contains_valid_characters(name):
        return make_response("Invalid characters in name", 400)
    if not contains_valid_characters(first_name):
        return make_response("Invalid characters in first name", 400)
    if email != '' and not is_valid_email(email):
        return make_response("Invalid email format", 400)

    try:
        new_user = User(name=name, first_name=first_name, email=email)
        db.session.add(new_user)
        db.session.commit()
    except:
        db.session.rollback()
        raise
    return redirect(url_for("index"))


@user_bp.route('/profile')
@login_required
def profile():
    return render_template("profile.html")


@user_bp.route('update_profile', methods=['POST'])
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
