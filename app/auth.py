from flask import Blueprint, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user

from . import db
from .forms import RegisterForm, LoginForm
from .models import User

bp = Blueprint("auth", __name__)


@bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        # con l'email dell'admin si diventa admin, gli altri sono user
        if user.email == current_app.config["ADMIN_EMAIL"]:
            user.role = "admin"
        db.session.add(user)
        db.session.commit()
        flash("Registrazione completata, adesso puoi fare il login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).filter_by(email=form.email.data))
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            flash("Ciao " + user.username + "!", "success")
            return redirect(url_for("main.index"))
        flash("Email o password non corretti.", "danger")

    return render_template("login.html", form=form)


@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Hai fatto il logout.", "info")
    return redirect(url_for("main.index"))
