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


def check_access_level(*allowed_roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id_profile = kwargs.get('user_id')
            user = db.session.query(User).get(session["user_id"])

            # Check if the user has not the required role
            if not any(user.allowed(role) for role in allowed_roles):
                flash("Permission denied. You do not have access to this page.", "error")
                return redirect(url_for("index"))

            # Check if the user is trying to access a profile that is not his own
            if user_id_profile and user.id != user_id_profile and not user.allowed(Role.ADMIN):
                flash("Permission denied. You do not have access to this page.", "error")
                return redirect(url_for("index"))

            return f(*args, **kwargs)

        return decorated_function

    return decorator
