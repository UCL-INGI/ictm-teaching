import json
from functools import wraps
from flask import Flask, render_template, redirect, session, request, url_for, make_response, flash
from db import User, Session

import auth
from auth import auth_bp

app = Flask(__name__)

app.config.from_file("config.json", load=json.load)

# Core blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")


# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in", False):
            return auth.login()
        else:
            return f(*args, **kwargs)
    return decorated_function


# Routes
@app.route('/')
def index():  # put application's code here
    return render_template("index.html")


@app.route('/private')
@login_required
def private():
    return render_template("private.html")

@app.route('/register')
@login_required
def register():
    return render_template('register.html')


@app.route('/add_user', methods=['POST'])
@login_required
def add_user():
    form = request.form
    if form:
        name = request.form['name']
        first_name = request.form['first_name']
        email = request.form['email']

        db_session = Session()
        try:
            new_user = User(name=name, first_name=first_name, email=email)
            db_session.add(new_user)
            db_session.commit()
        except:
            db_session.rollback()
            raise
        return redirect(url_for("index"))
    else:
        return make_response("Problem with form request", 500)

@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html")


@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    form = request.form
    if form:
        name = request.form['name']
        first_name = request.form['first_name']
        email = request.form['email']

        db_session = Session()
        user = db_session.query(User).filter(User.email == email).first()
        if user:
            try:
                user.first_name = first_name
                user.name = name
                db_session.commit()
                session["first_name"] = first_name
                session["name"] = name
            except Exception as e:
                db_session.rollback()
            return redirect(url_for("profile"))
        else:
            flash('User not found', 'danger')
    else:
        return make_response("Problem with form request", 500)


if __name__ == '__main__':
    app.run()
