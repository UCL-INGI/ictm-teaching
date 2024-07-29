from functools import wraps
from flask import session, redirect, url_for, flash
from db import db, User, Role
import auth


# Decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("logged_in", False):
            return auth.login()
        else:
            return f(*args, **kwargs)

    return decorated_function


def check_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id_profile = kwargs.get('user_id')
            user = db.session.query(User).get(session["user_id"])
            if not user.allowed(access_level) or (user_id_profile and user.id != user_id_profile and not user.allowed(Role.ADMIN)):
                flash("Permission denied. You do not have access to this page.", "error")
                return redirect(url_for("index"))
            else:
                return f(*args, **kwargs)

        return decorated_function

    return decorator
