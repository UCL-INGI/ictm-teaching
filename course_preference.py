from decorators import login_required
from db import db, Researcher, PreferenceAssignment
from flask import Blueprint, render_template, flash, url_for, request, make_response, redirect, \
    Flask, jsonify, session
import json

from util import get_current_year

course_preference_bp = Blueprint('course_preference', __name__)


def delete_old_preferences(researcher_id, course_ids, current_year):
    try:
        db.session.query(PreferenceAssignment).filter(
            PreferenceAssignment.researcher_id == researcher_id,
            PreferenceAssignment.course_year == current_year,
            ~PreferenceAssignment.course_id.in_(course_ids)
        ).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e


@course_preference_bp.route('/save_preference', methods=['POST'])
@login_required
def save_preference():
    data = request.get_json()
    current_year = get_current_year()

    if data is None:
        return make_response("No data received", 500)

    preferences = data['preferences']
    if preferences is None:
        return make_response("No preferences received", 500)

    user_id = session["user_id"]
    researcher = Researcher.query.filter(Researcher.user_id == user_id).first()
    if researcher is None:
        return make_response("User is not a researcher", 500)

    new_course_ids = {preference.split("-", 1)[0] for preference in preferences}
    delete_old_preferences(researcher.id, new_course_ids, current_year)

    for preference in preferences:
        try:
            course_id, course_year = preference.split("-", 1)
            existing_preference = db.session.query(PreferenceAssignment).filter_by(
                course_id=course_id,
                course_year=course_year,
                researcher_id=researcher.id
            ).first()

            if existing_preference is None:
                new_preference = PreferenceAssignment(course_id=course_id, course_year=course_year,
                                                      researcher_id=researcher.id)
                db.session.add(new_preference)
                db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    return redirect(url_for("user.user_profile", user_id=user_id, current_year=current_year))


@course_preference_bp.route('/delete_preference', methods=['GET'])
@login_required
def delete_preference():
    preference_id = request.args.get('preference')
    current_year = get_current_year()
    try:
        db.session.query(PreferenceAssignment).filter_by(id=preference_id).delete()
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

    return redirect(url_for("user.user_profile", user_id=session["user_id"], current_year=current_year))
