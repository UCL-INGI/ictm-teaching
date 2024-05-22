from decorators import login_required
from db import db, Configuration
from flask import Blueprint, render_template, flash, current_app, url_for, request, make_response, redirect, session, \
    Flask

config_bp = Blueprint('config', __name__)


@config_bp.route('/next_year', methods=['GET'])
@login_required
def next_year():
    last_year = Configuration.query.order_by(Configuration.year.desc()).first()

    if last_year:
        current_year = last_year.year
        start_year, end_year = map(int, current_year.split('-'))
        next_start_year = start_year + 1
        next_end_year = end_year + 1
        next_academic_year = f"{next_start_year}-{next_end_year}"

        try:
            # Check whether the following year already exists in the database
            existing_config = Configuration.query.filter_by(year=next_academic_year).first()
            if existing_config is None:
                config = Configuration(year=next_academic_year)
                db.session.add(config)
                db.session.commit()
                Configuration.update_current_year(config.id)
            else:
                flash('There is no configuration yet', 'warning')
        except Exception as e:
            db.session.rollback()
            raise e

        return redirect(url_for("index"))


@config_bp.route('/update_current_year', methods=['POST'])
@login_required
def update_current_year():
    current_year = request.form.get('selected_year')
    session['current_year'] = current_year
    flash('Updated current year', 'success')

    return redirect(url_for("index"))
