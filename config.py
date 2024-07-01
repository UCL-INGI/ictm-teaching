from decorators import login_required
from db import db, Configuration
from flask import Blueprint, render_template, flash, current_app, url_for, request, make_response, redirect, session, \
    Flask

config_bp = Blueprint('config', __name__)


@config_bp.route('/next_year', methods=['POST'])
@login_required
def next_year():
    last_year = Configuration.query.order_by(Configuration.year.desc()).first()

    current_year = last_year.year

    try:
        # Check whether the following year already exists in the database
        existing_config = Configuration.query.filter_by(year=current_year + 1).first()
        if existing_config is not None:
            return make_response("The year already exists", 500)

        session['current_year'] = current_year + 1
        config = Configuration(year=current_year + 1)
        db.session.add(config)
        db.session.commit()
        Configuration.update_current_year(config.id)

    except Exception as e:
        db.session.rollback()
        raise e

    return redirect(url_for("index"))


@config_bp.route('/update_current_year', methods=['POST'])
@login_required
def update_current_year():
    current_year = request.form.get('selected_year')
    session['current_year'] = int(current_year)
    flash('Updated current year', 'success')
    return redirect(url_for("index"))
