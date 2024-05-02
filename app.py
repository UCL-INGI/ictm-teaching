from auth import auth_bp
from user import user_bp
from decorators import *
from db import db, User
from flask import Flask, render_template, redirect, session, request, url_for, make_response, flash
from flask_sqlalchemy import SQLAlchemy
import json


app = Flask(__name__)
app.config.from_file("config.json", load=json.load)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ictm-teaching.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Core blueprints
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(user_bp, url_prefix="/user")

db.init_app(app)
with app.app_context():
    db.create_all()

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