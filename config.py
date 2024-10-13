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
        flash("An error has occurred. We will solve it as soon as possible", "error")

        return redirect(url_for("config.manage_years"))

    return redirect(url_for("config.manage_years"))


# This method allows the admin to move on to the next academic year for all users.
@config_bp.route('/next_year', methods=['POST'])
@login_required
@check_access_level(Role.ADMIN)
def next_year():
    current_year = Configuration.query.filter_by(is_current_year=True).first()
    try:
        new_year = Configuration.query.filter_by(year=current_year.year + 1).first()

        # Check if the following year already exists
        if new_year is None:
            # Create the new year entry automatically
            new_year = Configuration(year=current_year.year + 1, is_current_year=True)
            db.session.add(new_year)
            flash("New year created automatically", "success")
        else:
            # If the new year exists, just update the current year status
            new_year.is_current_year = True

        current_year.is_current_year = False
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        logging.error(f'An error occurred: {str(e)}', exc_einfo=True)
        flash("An error has occurred. We will solve it as soon as possible", "error")

        return redirect(url_for("config.manage_years"))

    return redirect(url_for("config.manage_years"))


@config_bp.route('/delete_year/<int:id_year>', methods=['POST'])
@login_required
@check_access_level(Role.ADMIN)
def delete_year(id_year):
    try:
        config = Configuration.query.get(id_year)
        if config.is_current_year:
            flash("You cannot delete the current year", "error")
        else:
            db.session.delete(config)
            db.session.commit()
            flash("Year deleted successfully", "success")
    except Exception as e:
        db.session.rollback()
        logging.error(f'An error occurred while deleting year {id_year}: {str(e)}', exc_info=True)
        flash("An error occurred. Please try again.", "error")

    return redirect(url_for("config.manage_years"))

