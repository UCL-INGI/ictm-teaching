from decorators import login_required
from db import db, Researcher, PreferenceAssignment
from flask import Blueprint, render_template, flash, url_for, request, make_response, redirect, \
    Flask, jsonify, session
import json

course_preference_bp = Blueprint('course_preference', __name__)

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)


@course_preference_bp.route('/save_preference', methods=['POST'])
@login_required
def save_preference():
    preferences = request.form.getlist('preferences[]')
    user_id = session["user_id"]
    researcher = Researcher.query.filter(Researcher.user_id == user_id).first()

    for preference in preferences:
        try:
            course_id, course_year = preference.split("-", 1)
            new_preference = PreferenceAssignment(course_id=course_id, course_year=course_year, researcher_id=researcher.id)
            db.session.add(new_preference)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    return redirect(url_for("user.profile"))


@course_preference_bp.route('/delete_preference', methods=['GET'])
@login_required
def delete_preference():
    preference_id = request.args.get('preference')
    try:
        db.session.query(PreferenceAssignment).filter_by(id=preference_id).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

    return redirect(url_for("user.profile"))

