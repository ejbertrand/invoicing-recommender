from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session
from ..models import User
from werkzeug.security import generate_password_hash, check_password_hash
from .. import db, mail
from flask_login import login_user, login_required, logout_user, current_user
from flask_mail import Message

auth = Blueprint("auth", __name__)

def send_mail(email):
	msg = Message('Welcome to AT Center Inc!', sender = 'no-reply@atcenterinc.com', recipients = [email])
	msg.body = "Hello, welcome to AT Center Inc. \nChancho Chanchia, Chi!\n\n -Gracias"
	mail.send(msg)


@auth.route("/login", methods = ["GET", "POST"])
def login():
	if not current_user.is_authenticated:
		if request.method == "POST":
			user_email = request.form.get("user_email")
			user_password = request.form.get("user_password")
			user = User.query.filter_by(email = user_email).first()
			if user:
				if check_password_hash(user.password, user_password):
					flash("Logged in succesfully!", category = "sucess")
					login_user(user, remember = True)
					session["transaction_state"] = "INACTIVE"
					return redirect(url_for("views.home"))
				else:
					flash("Incorrect password, try again.", category = "error")
			else:
				flash("Email does not exist.", category = "error")
		return render_template("login.html", user = current_user)
	else:
		return redirect(url_for("views.home"))


@auth.route("/logout")
@login_required
def logout():
	session["transaction_state"] = "INACTIVE"
	logout_user()
	return redirect(url_for("auth.login"))


@auth.route("/sign-up", methods = ["GET", "POST"])
def sign_up():
	if not current_user.is_authenticated:
		if request.method == "POST":
			user_email = request.form.get("user_email")
			user_name = request.form.get("user_name")
			user_password1 = request.form.get("user_password1")
			user_password2 = request.form.get("user_password2")
			user = User.query.filter_by(email = user_email).first()
			if user:
				flash("Email already exists.", category = "error")
			elif len(user_email) <= 3:
				flash("Email must be greater than 3 characters.", category = "error")
			elif len(user_name) < 2:
				flash("Name must be greater than 1 character.", category = "error")
			elif user_password1 != user_password2:
				flash("Passwords don't match.", category = "error")
			elif len(user_password1) < 7:
				flash("Password must be at least 7 characters.", category = "error")
			else:
				new_user = User(email = user_email, password = generate_password_hash(user_password1, method = "sha256"), name = user_name, active = 1)
				db.session.add(new_user)
				db.session.commit()
				login_user(new_user, remember = True)
				# send_mail(email)
				flash("Account created!", category = "success")
				return redirect(url_for("views.home"))
		return render_template("sign_up.html", user = current_user)
	else:
		return redirect(url_for("views.home"))
