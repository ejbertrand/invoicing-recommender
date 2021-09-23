from flask import Blueprint, render_template, request, flash, jsonify, make_response, session
from flask_login import login_required, current_user
from sqlalchemy.orm import aliased
from sqlalchemy.sql import text as SQLQuery
from ..models import Service, Payment, Transaction, User
from .. import db
import json
import pdfkit
import datetime

views = Blueprint("views", __name__)


###################################################################
###################    RENDERING     ##############################
###################################################################

###################################################################
# Function:		home
# Purpose:		Loads the home page
# Return vals: 	Rendered HTML of the home page
###################################################################
@views.route('/')
@login_required
def home():
	services = db.session.query(Service).filter_by(parent_id=None).all()
	payments = db.session.query(Payment).all()
	if (session["transaction_state"] == "ACTIVE"):
		formatted_balance = "{:,.2f}".format(round(session["balance"], 2))
		return render_template("home.html", user = current_user, services = services, \
			payments = payments, transaction_state = session["transaction_state"], \
			client_name = session["client_name"], payment_id = session["payment_id"], \
			comments = session["comments"], items = session["items"], balance = formatted_balance)
	else:
		return render_template("home.html", user = current_user, services = services, \
			payments = payments, transaction_state = session["transaction_state"])


###################################################################
# Function:		configure_service
# Purpose:		Loads the Service Config page
# Return vals: 	Rendered HTML of the Service Config page
###################################################################
@views.route('/services-config')
@login_required
def configure_service():
	all_services = db.session.query(Service).all()	# List of Service objects
	srv_dict = {service.id:service.service_type for service in all_services if service.parent_id is None}
	subsrv_dict = {service.id:dict() for service in all_services if service.parent_id is None}
	for item in subsrv_dict:
		subsrv_dict[item] = {service.id: service.service_type for service in all_services if (service.parent_id == item)}
	return render_template("services.html", user = current_user, srv_dict = srv_dict, subsrv_dict = subsrv_dict)


###################################################################
# Function:		configure_payment
# Purpose:		Loads the Payment Config page, and adds a new 
#				payment if called with POST
# Return vals: 	Rendered HTML of the Payment Config page
###################################################################
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


###################################################################
# Function:		show_transactions
# Purpose:		Loads the Transactions page
# Return vals: 	Rendered HTML of Transactions page
###################################################################
@views.route('/transactions')
@login_required
def show_transactions():
	ParentService = aliased(Service)
	transactions = (
		db.session.query(
			Transaction.id,
			Transaction.date,
			User.user_name,
			#ParentService.service_type, ## To enable
			#Service.service_type,
			Payment.payment_type,
			Transaction.client_name,
			Transaction.balance,
			Transaction.comment
		)
		.join(User)
		#.join(Service)
		#.join(Service.service_parent.of_type(ParentService))
		.join(Payment)
		.all()
	)
	return render_template("transactions.html", user = current_user, transactions = transactions)


###################################################################
# Function:		get_subservices
# Purpose:		Get the subservices associated to a service
# Return vals: 	JSON containing the subservice list
###################################################################
@views.route("/get-subservices", methods = ["POST"])
@login_required
def get_subservices():
	service_dic = json.loads(request.data)
	serviceId = service_dic['serviceId']
	subservices = db.session.query(Service).filter_by(parent_id=serviceId).all();
	subservices_lst = [[item.id, item.service_type] for item in subservices]
	return jsonify(subservices_lst)




###################################################################
###################    SESSION     ################################
###################################################################

###################################################################
# Function:		open_transaction
# Purpose:		Set transaction state to active and cleans session 
# 				variables
# Return vals: 	Empty JSON
###################################################################
@views.route("/open-transaction", methods = ["POST"])
@login_required
def open_transaction():
	session["transaction_state"] = "OPEN"
	session["client_name"] = ""
	session["payment_id"] = 0
	session["comments"] = ""
	session["items"] = []
	session["balance"] = 0.00
	return jsonify({})


###################################################################
# Function:		add_item
# Purpose:		Adds an item into the items table
# Return vals: 	JSON containing the updated table
###################################################################
@views.route('/add-item', methods = ["POST"])
@login_required
def add_item():
	item_dic = json.loads(request.data)
	serviceId = item_dic["serviceId"]
	subserviceId = item_dic["subserviceId"]
	total = float(item_dic["total"])
	session["client_name"] = item_dic["client_name"]
	session["payment_id"] = int(item_dic["payment_id"])
	session["comments"] = item_dic["comments"]
	service = db.session.query(Service.service_type).filter_by(id=serviceId).all()[0][0]
	subservice = db.session.query(Service.service_type).filter_by(id=subserviceId).all()[0][0]
	session['items'].append((service, subservice, "{:,.2f}".format((total))))
	session['balance'] += float(total)
	session["transaction_state"] = "ACTIVE"
	formatted_balance = "{:,.2f}".format(round(session["balance"], 2))
	json_response = jsonify({"table": session["items"], "balance": formatted_balance})
	return json_response


###################################################################
# Function:		delete_item
# Purpose:		Deletes an item from the items table
# Return vals: 	JSON containing the updated table
###################################################################
@views.route('/delete-item', methods = ["POST"])
@login_required
def delete_item():
	item_dic = json.loads(request.data)
	rowId = item_dic['rowId']
	total = session['items'][rowId][2]
	session['items'].pop(rowId)
	session['balance'] -= float(total.replace(',', ''))
	formatted_balance = "{:,.2f}".format(round(session["balance"], 2))
	json_response = jsonify({"table": session["items"], "balance": formatted_balance})
	return json_response


###################################################################
# Function:		clean_session
# Purpose:		Clean session variables
# Return vals: 	Empty JSON
###################################################################
@views.route('/clean-session', methods = ["POST"])
@login_required
def clean_session():
	session["transaction_state"] = "INACTIVE"
	session["client_name"] = ""
	session["payment_id"] = 0
	session["comments"] = ""
	session["items"] = []
	session["balance"] = 0.00
	return jsonify()


###################################################################
# Function:		set_invoice_info
# Purpose:		Saves variable sessions before printing an invoice
# Return vals: 	JSON containing a flag value
###################################################################
@views.route('/set-invoice-info', methods = ["POST"])
@login_required
def set_invoice_info():
	flag = 0	# OK
	if (not session["items"]):
		flag = 1	# No items
	elif (session["balance"] == 0):
		flag = 2	# No balance
	else:
		transaction_dic = json.loads(request.data)
		session["client_name"] = transaction_dic['client_name']
		session["payment_id"] = int(transaction_dic['payment_id'])
		session["comments"] = transaction_dic['comments']
	return jsonify({"flag": flag})


###################################################################
# Function:		print_invoice
# Purpose:		Generate a PDF invoice
# Return vals: 	A PDF invoice
###################################################################
@views.route('/print-invoice')
@login_required
def print_invoice():
	invoice_number = 24 # Need to retrieve from DB
	day = datetime.datetime.now().day
	year = datetime.datetime.now().year
	months_dic = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", \
		8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
	month = months_dic[datetime.datetime.now().month]
	date = month + " " + str(day) + ", " + str(year)
	payment = db.session.query(Payment.payment_type).filter_by(id = session['payment_id']).all()
	formatted_balance = "{:,.2f}".format(round(session["balance"], 2))
	client_address = "87 Private St. Seattle, WA" # Need to retrieve from DB
	client_email = "smith@gmail.com" # Need to retrieve from DB
	client_telno = "990-302-1898" # Need to retrieve from DB
	rendered = render_template("invoice.html", invoice_number = invoice_number, client_name = session["client_name"], \
		payment = payment[0][0], items = session["items"], balance = formatted_balance, date = date, \
			client_address = client_address, client_email = client_email, client_telno = client_telno) 
	pdf = pdfkit.from_string(rendered, False)
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'inline; filename=invoice.pdf'
	return response


###################################################################
# Function:		close_transaction
# Purpose:		Saves the transaction into the database
# Return vals: 	JSON containing a flag value
###################################################################
@views.route('close-transaction', methods = ['POST'])
@login_required
def close_transaction():
	flag = 0
	if (not session["items"]):
		flag = 1	# No items
	elif (session["balance"] == 0):
		flag = 2	# No balance
	else:
		transaction_dic = json.loads(request.data)
		client_name = transaction_dic["client_name"]
		payment_id = transaction_dic['payment_id']
		comments = transaction_dic["comments"]
		#payment_id = db.session.query(Payment.id).filter_by(payment_type=payment).all()
		transaction = Transaction(
			user_id = current_user.id,
			payment_id = payment_id,
			client_name = client_name,
			balance = session['balance'],
			comment = comments)
		db.session.add(transaction)
		db.session.commit()
		## NEED DO ADD THE DETAILS OF THE TRANSACTION, BUT FOR THAT, WE NEED THE ID OF THE INVOICE
			#service_id = db.session.query(Service.parent_id).filter_by(id=sid[0][0]).all()[0][0],
			#subservice_id = sid[0][0],
	return jsonify({"flag": flag})




###################################################################
###################    CONFIGURATION    ###########################
###################################################################

###################################################################
# Function:		add_service
# Purpose:		Adds a service
# Return vals: 	A call to the configure_service function to render
#				the Service Config page
###################################################################
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


###################################################################
# Function:		add_subservice
# Purpose:		Adds a subservice
# Return vals: 	A call to the configure_service function to render
#				the Service Config page
###################################################################
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


###################################################################
# Function:		delete_service
# Purpose:		Deletes a service
# Return vals: 	Empty JSON
###################################################################
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


###################################################################
# Function:		delete_subservice
# Purpose:		Deletes a subservice
# Return vals: 	Empty JSON
###################################################################
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


###################################################################
# Function:		delete_payment
# Purpose:		Delete a payment method
# Return vals: 	Empty JSON
###################################################################
@views.route("/delete-payment-method", methods = ["POST"])
@login_required
def delete_payment():
	payment_dic = json.loads(request.data)
	payment_id = payment_dic['payment_id']
	payment = Payment.query.get(payment_id)
	if payment:
		db.session.delete(payment)
		db.session.commit()
	return jsonify({})




###################################################################
###################    HELPER FUNCTIONS    ########################
###################################################################

###################################################################
# Function:		check_float
# Purpose:		Verifies if an object is a float
# Return vals: 	True if it is, False if not
###################################################################
def check_float(potential_float):
	try:
		float(potential_float)
		return True
	except ValueError:
		return False