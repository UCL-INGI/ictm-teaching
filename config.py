from decorators import login_required
from db import db, Configuration
from flask import Blueprint, render_template, flash, current_app, url_for, request, make_response, redirect, session, \
    Flask

config_bp = Blueprint('config', __name__)


@config_bp.route('/next_year', methods=['POST'])
@login_required
def next_year():
    last_year = Configuration.query.order_by(Configuration.year.desc()).first()
    new_year = last_year.year + 1

    try:
        # Check whether the following year already exists in the database
        existing_config = Configuration.query.filter_by(year=new_year).first()
        if existing_config is not None:
            return make_response("The year already exists", 500)

        config = Configuration(year=new_year)
        db.session.add(config)
        db.session.commit()
        Configuration.update_current_year(config.id)

    except Exception as e:
        db.session.rollback()
        raise e

    return redirect(url_for("index"))
