from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from ..models import Service, Payment, Transaction
from .. import db
import json

views = Blueprint("views", __name__)

def check_float(potential_float):
	try:
		float(potential_float)
		return True
	except ValueError:
		return False

@views.route('/', methods = ["GET", "POST"])
@login_required
def home():
	if request.method == "POST":
		service_id = request.form.get("input_service")
		payment_id = request.form.get("input_payment")
		client_name = request.form.get("client_name")
		total = request.form.get("total")
		comments = request.form.get("comments")
		sid = db.session.query(Service.id).filter_by(type=request.form.get("input_service")).all()
		pid = db.session.query(Payment.id).filter_by(type=request.form.get("input_payment")).all()
		alerts = 0
		if not (sid):
			flash("The service was not selected", category = "error")
			alerts += 1
		if not (pid):
			flash("A payment method was not selected", category = "error")
			alerts += 1
		if len(client_name) < 1:
			flash("The client name is missing!", category = "error")
			alerts += 1
		if len(total) < 1:
			flash("The total is missing!", category = "error")
			alerts += 1
		if not check_float(total):
			flash("The total is in invalid format!", category = "error")
			alerts += 1
		if (alerts == 0):
			total_fl = float(total)
			new_register = Transaction(service_id = sid[0][0], payment_id = pid[0][0], client_name = client_name, total = total_fl, comments = comments)
			db.session.add(new_register)
			db.session.commit()
			flash("Transaction registered!", category = "success")
	services = db.session.query(Service).all()
	payments = db.session.query(Payment).all()
	return render_template("home.html", user = current_user, services = services, payments = payments)

@views.route('/services-config', methods = ['GET', 'POST'])
@login_required
def configure_service():
	if request.method == 'POST':
		service_type = request.form.get("service-type")
		if len(service_type) < 3:
			flash("The service type is too short!", category = "error")
		else:
			new_service = Service(type = service_type)
			db.session.add(new_service)
			db.session.commit()
			flash("Service added!", category = "success")
	all_services = db.session.query(Service).all()
	return render_template("services.html", user = current_user, services = all_services)

@views.route("/payment-config", methods = ['GET', 'POST'])
@login_required
def configure_payment():
	if request.method == 'POST':
		payment_type = request.form.get("payment-type")
		if len(payment_type) < 3:
			flash("The payment type is too short!", category = "error")
		else:
			new_payment = Payment(type = payment_type)
			db.session.add(new_payment)
			db.session.commit()
			flash("Payment method added!", category = "success")
	all_payments = db.session.query(Payment).all()
	return render_template("payments.html", user = current_user, payments = all_payments)

@views.route('/transactions')
def show_transactions():
	transactions = db.session.query(Transaction).all()
	return render_template("transactions.html", user = current_user, transactions = transactions)

@views.route("/delete-service", methods = ["POST"])
def delete_service():
	service = json.loads(request.data)
	serviceId = service['serviceId']
	service = Service.query.get(serviceId)
	if service:
		#if service.user_id == current_user.id:
		db.session.delete(service)
		db.session.commit()
	return jsonify({})

@views.route("/delete-payment-method", methods = ["POST"])
def delete_payment():
	payment = json.loads(request.data)
	paymentId = payment['paymentId']
	payment = Payment.query.get(paymentId)
	if payment:
		db.session.delete(payment)
		db.session.commit()
	return jsonify({})
