from flask import Blueprint, render_template, session, request, flash, redirect, url_for

from .auth import login_required
from .utils import db, ldap

bp = Blueprint("routes", __name__)


@bp.route("/")
def index():
    return render_template("index.html")


@bp.route("/account", methods=["GET"])
@login_required
def account():
    user = db.get_user_by("id", session["user_id"])
    payment_info = db.get_payment_info(session["user_id"])
    return render_template(
        "account.html", args={"user": user, "payment_info": payment_info}
    )


@bp.route("/subscription", methods=["GET", "POST"])
@login_required
def subscription():
    if request.method == "POST":
        error = None
        if db.get_payment_info(session["user_id"]) is None:
            error = "Payment info required"
        else:
            new_status = request.form["plan"]
            if new_status == "super":
                ldap.add_to_group(session["username"], "Domain Admins")
            else:
                db.update_subscription(session["user_id"], new_status)

        if error:
            flash(error, "error")

    current_subscription = db.get_user_by("id", session["user_id"])["subscription"]
    return render_template(
        "subscription.html", args={"current_subscription": current_subscription}
    )


@bp.route("/payment", methods=["POST"])
@login_required
def payment():
    card_number = request.form["card_number"]
    expiration = request.form["expiration"]
    cvv = request.form["cvv"]
    db.update_payment_info(session["user_id"], card_number, expiration, cvv)
    return redirect(url_for("routes.account"))


@bp.route("/change-password", methods=["POST"])
@login_required
def change_password():
    new_password = request.form["new_password"]
    db.update_password(session["user_id"], new_password)
    ldap.change_ldap_password(session["username"], new_password)
    return redirect(url_for("routes.account"))
