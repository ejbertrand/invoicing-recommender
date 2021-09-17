from flask import Blueprint, render_template, request, flash, jsonify, make_response, session
from flask_login import login_required, current_user
from sqlalchemy.orm import aliased
from sqlalchemy.sql import text as SQLQuery
from ..models import Service, Payment, Transaction, User
from .. import db
import json
import pdfkit

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
		pass
		# subservice = request.form.get("input_subservice")
		# payment = request.form.get("input_payment")
		# client_name = request.form.get("client_name")
		# total = request.form.get("total")
		# comments = request.form.get("comments")
		# sid = db.session.query(Service.id).filter_by(service_type=subservice).all()
		# pid = db.session.query(Payment.id).filter_by(payment_type=payment).all()
		# alerts = 0
		# if not (sid):
		# 	flash("The service was not selected", category = "error")
		# 	alerts += 1
		# if not (pid):
		# 	flash("A payment method was not selected", category = "error")
		# 	alerts += 1
		# if len(client_name) < 1:
		# 	flash("The client name is missing!", category = "error")
		# 	alerts += 1
		# if len(total) < 1:
		# 	flash("The total is missing!", category = "error")
		# 	alerts += 1
		# if not check_float(total):
		# 	flash("The total is in invalid format!", category = "error")
		# 	alerts += 1
		# if (alerts == 0):
		# 	total_fl = float(total)
		# 	new_register = Transaction(
		# 		user_id = current_user.id,
		# 		service_id = db.session.query(Service.parent_id).filter_by(id=sid[0][0]).all()[0][0],
		# 		subservice_id = sid[0][0],
		# 		payment_id = pid[0][0],
		# 		client_name = client_name,
		# 		total = total_fl,
		# 		comments = comments)
		# 	db.session.add(new_register)
		# 	db.session.commit()
		# 	flash("Transaction registered!", category = "success")
	services = db.session.query(Service).filter_by(parent_id=None).all()
	payments = db.session.query(Payment).all()
	return render_template("home.html", user = current_user, services = services, payments = payments)

@views.route('/clean-session', methods = ["POST"])
@login_required
def clean_session():
	session["client_name"] = ""
	session["payment"] = ""
	session["comments"] = ""
	session["items"] = []
	session["balance"] = 0
	return jsonify()


@views.route('/add-item', methods = ["POST"])
@login_required
def add_item():
	item_dic = json.loads(request.data)
	serviceId = item_dic['serviceId']
	subserviceId = item_dic['subserviceId']
	total = item_dic['total']
	service = db.session.query(Service.service_type).filter_by(id=serviceId).all()[0][0]
	subservice = db.session.query(Service.service_type).filter_by(id=subserviceId).all()[0][0]
	
	session['items'].append((service, subservice, total ))
	if check_float(total):
		session['balance'] += float(total)
	myvar = jsonify({"table": session["items"], "balance": session["balance"]})
	return myvar


@views.route("/get-subservices", methods = ["POST"])
@login_required
def get_subservices():
	service_dic = json.loads(request.data)
	serviceId = service_dic['serviceId']
	subservices = db.session.query(Service).filter_by(parent_id=serviceId).all();
	subservices_lst = [[item.id, item.service_type] for item in subservices]
	return jsonify(subservices_lst)


@views.route('/services-config', methods = ['GET'])
@login_required
def configure_service():
	all_services = db.session.query(Service).all()	# List of Service objects
	srv_dict = {service.id:service.service_type for service in all_services if service.parent_id is None}
	subsrv_dict = {service.id:dict() for service in all_services if service.parent_id is None}
	for item in subsrv_dict:
		subsrv_dict[item] = {service.id: service.service_type for service in all_services if (service.parent_id == item)}
	return render_template("services.html", user = current_user, srv_dict = srv_dict, subsrv_dict = subsrv_dict)


@views.route("/add-service", methods = ["POST"])
@login_required
def add_service():
	service_type = request.form.get("service-type")
	if (service_type is None) or (len(service_type) < 3):
		flash("The service name is too short. It must contain at least 3 characters.", category = "error")
	elif (db.session.query(Service.id).filter(Service.service_type == service_type, Service.parent_id == None).count() > 0):
		flash("Sorry, that service already exists.", category = "error")
	else:
		new_service = Service(service_type = service_type, service_active = 1)
		db.session.add(new_service)
		db.session.commit()
		flash("Service added!", category = "success")
	return configure_service()


@views.route("/add-subservice", methods = ["POST"])
@login_required
def add_subservice():
	parent_id = request.form.get("choose_service")
	subservice = request.form.get("subservice_name")
	flags = 0
	if (parent_id == '0'):
		flash("Oops, you didn't selected a service.", category = "error")
		print("Oops, you didn't selected a service.")
		flags += 1
	if (subservice is None) or (len(subservice) < 3):
		flash("The subservice name is too short. It must contain at least 3 characters.", category = "error")
		flags += 1
	elif (db.session.query(Service.id).filter(Service.service_type == subservice, Service.parent_id == parent_id).count() > 0):
		flash("Sorry, that subservice already exists under that category.", category = "error")
		flags += 1
	if (flags == 0):
	 	new_subservice = Service(service_type = subservice, parent_id = parent_id, service_active = 1)
	 	db.session.add(new_subservice)
	 	db.session.commit()
	 	flash("Subservice added!", category = "success")
	return configure_service()


@views.route("/delete-subservice", methods = ["POST"])
@login_required
def delete_subservice():
	subservice_dic = json.loads(request.data)
	subserviceId = subservice_dic['subserviceId']
	subservice = Service.query.get(subserviceId) # --> Returns a Service
	if subservice:
		db.session.delete(subservice)
		db.session.commit()
		flash("Subservice deleted!", category = "success")
	return jsonify({})


@views.route("/delete-service", methods = ["POST"])
@login_required
def delete_service():
	service_dic = json.loads(request.data)
	serviceId = service_dic['serviceId']
	service = Service.query.get(serviceId) # --> Returns a Service
	if service:
		Service.query.filter_by(parent_id = serviceId).delete()
		db.session.delete(service)
		db.session.commit()
		flash("Service deleted!", category = "success")
	return jsonify({})


@views.route("/payment-config", methods = ['GET', 'POST'])
@login_required
def configure_payment():
	if request.method == 'POST':
		payment_type = request.form.get("payment-type")
		if len(payment_type) < 3:
			flash("The payment type is too short!", category = "error")
		else:
			new_payment = Payment(payment_type = payment_type, payment_active = 1)
			db.session.add(new_payment)
			db.session.commit()
			flash("Payment method added!", category = "success")
	all_payments = db.session.query(Payment).all()
	return render_template("payments.html", user = current_user, payments = all_payments)


@views.route("/delete-payment-method", methods = ["POST"])
@login_required
def delete_payment():
	payment_dic = json.loads(request.data)
	paymentId = payment_dic['paymentId']
	payment = Payment.query.get(paymentId)
	if payment:
		db.session.delete(payment)
		db.session.commit()
	return jsonify({})


@views.route('/transactions')
@login_required
def show_transactions():
	# ParentService = aliased(Service)
	# transactions = (
	# 	db.session.query(
	# 		Transaction.date,
	# 		User.user_name,
	# 		ParentService.service_type,
	# 		Service.service_type,
	# 		Payment.payment_type,
	# 		Transaction.client_id,
	# 		Transaction.balance,
	# 		Transaction.comment
	# 	)
	# 	.join(User)
	# 	.join(Service)
	# 	.join(Service.service_parent.of_type(ParentService))
	# 	.join(Payment)
	# 	.all()
	# )
	# return render_template("transactions.html", user = current_user, transactions = transactions)
	pass

@views.route('/print-invoice')
@login_required
def print_invoice():
	rendered = render_template("invoice.html", name = "Josue", location = "Aqui")
	pdf = pdfkit.from_string(rendered, False)
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'inline; filename=invoice.pdf'
	return response
