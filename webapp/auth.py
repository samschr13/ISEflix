import functools
from .utils.ldap import ldap_exists, create_ldap_user

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from sqlalchemy import exc

from .utils import db

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        error = None

        if not username:
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None:
            try:
                if not ldap_exists(username):
                    create_ldap_user(username, password)
                db.insert_user(username, password)
            except exc.IntegrityError as e:
                error = e
            else:
                return redirect(url_for("auth.login"))
        flash(error, "error")

    return render_template("auth/register.html")


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = db.get_user_by("username", username)

        error = None
        if user is None:
            error = "Incorrect username."
        elif not password == user["password"]:
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user["id"]
            session["username"] = username
            return redirect(url_for("routes.account"))
        flash(error, "error")
    return render_template("auth/login.html")


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = db.get_user_by("id", user_id)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return wrapped_view
