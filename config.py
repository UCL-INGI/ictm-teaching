from decorators import login_required, check_access_level
from db import db, Configuration, Role
from flask import Blueprint, render_template, flash, current_app, url_for, request, make_response, redirect, session, \
    Flask
import logging

config_bp = Blueprint('config', __name__)


@config_bp.route('/manage_years', methods=['GET'])
@login_required
@check_access_level(Role.ADMIN)
def manage_years():
    configurations = Configuration.query.order_by(Configuration.year.desc()).all()
    return render_template('config.html', configurations=configurations)


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
        flash("Year created successfully", "success")

    except Exception as e:
        db.session.rollback()
        logging.error(f'An error occurred: {str(e)}', exc_einfo=True)
        flash(f"An error occurred while creating the year {new_year} - {new_year + 1}.", "error")

    return redirect(url_for("config.manage_years"))


# This method allows the admin to move on to the next academic year for all users.
@config_bp.route('/change_year/<int:year>', methods=['POST'])
@login_required
@check_access_level(Role.ADMIN)
def change_year(year):
    try:
        new_current_year = Configuration.query.filter_by(year=year).first()
        Configuration.update_current_year(new_current_year.id)

    except Exception as e:
        db.session.rollback()
        logging.error(f'An error occurred: {str(e)}', exc_einfo=True)
        flash(f"An error occurred while trying to change the current year to {year} - {year + 1}.", "error")

    return redirect(url_for("config.manage_years"))

