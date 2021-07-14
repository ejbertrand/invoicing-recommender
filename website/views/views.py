from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy.orm import aliased
from ..models import Service, Payment, Transaction, User
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
		subservice = request.form.get("input_subservice")
		payment = request.form.get("input_payment")
		client_name = request.form.get("client_name")
		total = request.form.get("total")
		comments = request.form.get("comments")
		sid = db.session.query(Service.id).filter_by(service_type=subservice).all()
		pid = db.session.query(Payment.id).filter_by(payment_type=payment).all()
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
			new_register = Transaction(
				user_id = current_user.id,
				service_id = db.session.query(Service.parent_id).filter_by(id=sid[0][0]).all()[0][0],
				subservice_id = sid[0][0],
				payment_id = pid[0][0],
				client_name = client_name,
				total = total_fl,
				comments = comments)
			db.session.add(new_register)
			db.session.commit()
			flash("Transaction registered!", category = "success")
	services = db.session.query(Service).filter_by(parent_id=None).all()
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
			new_service = Service(service_type = service_type, active = 1)
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
			new_payment = Payment(payment_type = payment_type, active = 1)
			db.session.add(new_payment)
			db.session.commit()
			flash("Payment method added!", category = "success")
	all_payments = db.session.query(Payment).all()
	return render_template("payments.html", user = current_user, payments = all_payments)

@views.route('/transactions')
def show_transactions():
	ParentService = aliased(Service)
	transactions = (
		db.session.query(
			Transaction.date,
			User.name,
			ParentService.service_type,
			Service.service_type,
			Payment.payment_type,
			Transaction.client_name,
			Transaction.total,
			Transaction.comments
		)
		.join(User)
		.join(Service)
		.join(Service.parent.of_type(ParentService))
		.join(Payment)
		.all()
	)
	return render_template("transactions.html", user = current_user, transactions = transactions)


@views.route("/delete-service", methods = ["POST"])
def delete_service():
	service_dic = json.loads(request.data)
	serviceId = service_dic['serviceId']
	service = Service.query.get(serviceId)
	if service:
		db.session.delete(service)
		db.session.commit()
	return jsonify({})


@views.route("/delete-payment-method", methods = ["POST"])
def delete_payment():
	payment_dic = json.loads(request.data)
	paymentId = payment_dic['paymentId']
	payment = Payment.query.get(paymentId)
	if payment:
		db.session.delete(payment)
		db.session.commit()
	return jsonify({})


@views.route("/get-subservices", methods = ["POST"])
def get_subservices():
	service_dic = json.loads(request.data)
	serviceId = service_dic['serviceId']
	subservices = db.session.query(Service.service_type).filter_by(parent_id=serviceId).all()
	subservices_lst = [item[0] for item in subservices]
	return jsonify(subservices_lst)
