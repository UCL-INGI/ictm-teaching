from db import db, User
from flask import Blueprint, current_app, url_for, request, make_response, redirect, session
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.utils import OneLogin_Saml2_Utils

auth_bp = Blueprint('auth', __name__)


def prepare_saml_request(request):
    acs_config = current_app.config["SAML"]["sp"]["assertionConsumerService"]
    acs_config["url"] = url_for("auth.callback", _external=True)
    return {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.host,
        'server_port': request.environ["SERVER_PORT"],
        'script_name': request.path,
        'get_data': request.args.copy(),
        'post_data': request.form.copy(),
        'query_string': request.query_string
    }


@auth_bp.route('/metadata')
def metadata():
    auth = OneLogin_Saml2_Auth(prepare_saml_request(request), current_app.config["SAML"])
    metadata = auth.get_settings().get_sp_metadata()
    errors = auth.get_settings().validate_metadata(metadata)

    if len(errors) == 0:
        resp = make_response(metadata, 200)
        resp.headers['Content-Type'] = 'text/xml'
    else:
        resp = make_response(', '.join(errors), 500)
    return resp


def check_or_create_user(user):
    try:
        is_user = db.session.query(User).filter(User.email == user.email).first()
        if is_user is None:
            db.session.add(user)
            db.session.commit()
            db.session.refresh(user)
        else:
            user = is_user
        return user
    except:
        db.session.rollback()
        raise


@auth_bp.route("/callback", methods=['GET', 'POST'])
def callback():
    auth = OneLogin_Saml2_Auth(prepare_saml_request(request), current_app.config["SAML"])
    auth.process_response()
    errors = auth.get_errors()
    if len(errors) == 0:
        auth_attrs = auth.get_attributes()
        mappings = current_app.config["SAML"]["attributes"]
        attrs = {key: auth_attrs.get(mapping, []) for key, mapping in mappings.items()}

        uid = attrs["uid"][0]
        first_name = attrs["givenName"][0] if len(attrs["givenName"]) else ''
        name = attrs["sn"][0]
        email = attrs["email"][0]

        session["logged_in"] = True
        session["uid"] = uid
        session["email"] = email

        user = User(name=name, first_name=first_name, email=email)
        updated_user = check_or_create_user(user)
        session["user_id"] = updated_user.id
        session["first_name"] = updated_user.first_name
        session["name"] = updated_user.name
        session["is_admin"] = updated_user.is_admin

        # Redirect to desired url
        self_url = OneLogin_Saml2_Utils.get_self_url(prepare_saml_request(request))
        if 'RelayState' in request.form and self_url != request.form['RelayState']:
            return redirect(auth.redirect_to(request.form['RelayState']))
    else:
        return make_response(", ".join(errors), 500)

    return make_response("saml_acs_error", 500)


@auth_bp.route('/login')
def login():
    auth = OneLogin_Saml2_Auth(prepare_saml_request(request), current_app.config["SAML"])
    return redirect(auth.login(url_for("index", _external=True)))


@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("index"))


@auth_bp.route('register')
def register():
    return redirect(url_for("register"))
