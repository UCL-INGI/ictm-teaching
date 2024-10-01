from decorators import login_required, check_access_level
from db import db, Configuration, Role
from flask import Blueprint, render_template, flash, current_app, url_for, request, make_response, redirect, session, \
    Flask

config_bp = Blueprint('config', __name__)


# This method allows the admin to create a new academic year.
@config_bp.route('/new_year', methods=['POST'])
@login_required
@check_access_level(Role.ADMIN)
def new_year():
    last_year = Configuration.query.order_by(Configuration.year.desc()).first()
    new_year = last_year.year + 1

    try:
        # Check whether the following year already exists in the database
        existing_config = Configuration.query.filter_by(year=new_year).first()
        if existing_config is not None:
            flash("The year already exists", "error")
            return redirect(url_for("index"))

        config = Configuration(year=new_year)
        db.session.add(config)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        flash("An error occurred while processing your request. Please try again.", "error")
        return redirect(url_for("index"))

    return redirect(url_for("index"))


# This method allows the admin to move on to the next academic year for all users.
@config_bp.route('/next_year', methods=['POST'])
@login_required
@check_access_level(Role.ADMIN)
def next_year():
    current_year = Configuration.query.filter_by(is_current_year=True).first()
    try:
        is_new_year = Configuration.query.filter_by(year=current_year.year + 1).first()

        # Check if the following year already exists
        if is_new_year is None:
            # Create the new year entry automatically
            is_new_year = Configuration(year=current_year.year + 1, is_current_year=True)
            db.session.add(is_new_year)
            flash("New year created automatically", "success")
        else:
            # If the new year exists, just update the current year status
            is_new_year.is_current_year = True

        current_year.is_current_year = False
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        flash("An error occurred while processing your request. Please try again.", "error")
        return redirect(url_for("index"))

    return redirect(url_for("index"))

