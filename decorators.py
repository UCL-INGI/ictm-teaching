from functools import wraps
from flask import session, redirect, url_for
from db import db, User
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
            if not session.get("logged_in", False):
                return auth.login()

            user = db.session.query(User).get(session["user_id"])
            if not user.allowed(access_level):
                return redirect(url_for("index"))
            else:
                return f(*args, **kwargs)

        return decorated_function

    return decorator
