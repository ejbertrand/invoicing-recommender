from flask import Blueprint, render_template, request, flash, jsonify, make_response, session, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.orm import aliased
from sqlalchemy.sql import text as SQLQuery
from ..models import Service, Payment, Transaction, User, Identification, Client
from .. import db
import json
import pdfkit
from datetime import datetime
import pytz

views = Blueprint("views", __name__)

g_utc = pytz.utc	
g_utc_dt = datetime.now(tz = g_utc)
g_timezone = 'America/Chicago'
g_invoice_dt = g_utc_dt.astimezone(pytz.timezone(g_timezone))  

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
	try:
		services = db.session.query(Service).filter_by(parent_id=None).all()
		payments = db.session.query(Payment).all()
		if (session["transaction_state"] == "ACTIVE"):
			formatted_account = "{:,.2f}".format(round(session["account"], 2))
			return render_template("home.html", user = current_user, services = services, \
				payments = payments, transaction_state = session["transaction_state"], \
				client_name = session["client_name"], payment_id = session["payment_id"], \
				comments = session["comments"], items = session["items"], account = formatted_account)
		else:
			return render_template("home.html", user = current_user, services = services, \
				payments = payments, transaction_state = session["transaction_state"])
	except KeyError:
		print("\nOops: A KeyError exception was raised\n")
		return redirect(url_for('auth.logout'))


###################################################################
# Function:		configure_service
# Purpose:		Loads the Service Config page
# Return vals: 	Rendered HTML of the Services config page
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
# Return vals: 	Rendered HTML of the Payments config page
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
# Function:		configure_identification
# Purpose:		Loads the Payment Config page, and adds a new 
#				payment if called with POST
# Return vals: 	Rendered HTML of the Identifications config page
###################################################################
@views.route("/identification-config", methods = ['GET', 'POST'])
@login_required
def configure_identification():
	if request.method == 'POST':
		id_type = request.form.get("identification-type")
		if len(id_type) < 3:
			flash("The identification form is too short!", category = "error")
		else:
			new_identification = Identification(id_type = id_type, id_active = 1)
			db.session.add(new_identification)
			db.session.commit()
			flash("Identification form added!", category = "success")
	all_identifications = db.session.query(Identification).all()
	return render_template("identifications.html", user = current_user, identifications = all_identifications)


###################################################################
# Function:		show_transactions
# Purpose:		Loads the Transactions page
# Return vals: 	Rendered HTML of Transactions page
###################################################################
@views.route('/transactions')
@login_required
def show_transactions():
	#ParentService = aliased(Service)
	transactions = (
		db.session.query(
			Transaction.id,
			Transaction.date,
			User.user_name,
			#ParentService.service_type, ## To enable
			#Service.service_type,
			Payment.payment_type,
			Transaction.client_name,
			Transaction.account,
			Transaction.comment
		)
		.join(User)
		#.join(Service)
		#.join(Service.service_parent.of_type(ParentService))
		.join(Payment)
		.order_by(Transaction.id.asc())
		.all()
	)
	return render_template("transactions.html", user = current_user, transactions = transactions)


###################################################################
# Function:		clients
# Purpose:		Add, delete, or modify clients' information
# Return vals: 	Rendered HTML of the Clients page
###################################################################
@views.route("/clients")
@login_required
def clients():
	all_identifications = db.session.query(Identification).all()
	clients = (
		db.session.query(
			Client.client_name,
			Client.tel_number,
			Client.alt_number,
			Client.client_email,
			Identification.id_type,
			Client.id_number,
			Client.address,
		)
		.join(Identification)
		.order_by(Client.client_name.asc())
		.all()
	)
	return render_template("clients.html", user = current_user, identifications = all_identifications, \
		clients = clients)



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
	session["account"] = 0.00
	session["payment_amount"] = 0.00
	session["balance"] = 0.00
	session["printed_invoice"] = 0
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
	session['account'] += float(total)
	session["transaction_state"] = "ACTIVE"
	formatted_account = "{:,.2f}".format(round(session["account"], 2))
	json_response = jsonify({"table": session["items"], "account": formatted_account})
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
	session['account'] -= float(total.replace(',', ''))
	formatted_account = "{:,.2f}".format(round(session["account"], 2))
	json_response = jsonify({"table": session["items"], "account": formatted_account})
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
	session["account"] = 0.00
	session["payment_amount"] = 0.00
	session["balance"] = 0.00
	session["printed_invoice"] = 0
	return jsonify()


###################################################################
# Function:		set_invoice_info
# Purpose:		Saves variable sessions before printing an invoice
# Return vals: 	JSON containing a flag value
###################################################################
@views.route('/set-invoice-info', methods = ["POST"])
@login_required
def set_invoice_info():
	transaction_dic = json.loads(request.data)
	flag = 0	# OK
	if (not session["items"]):
		flag = 1	# No items
	elif (session["account"] == 0):
		flag = 2	# No account
	elif (not check_float(transaction_dic["payment_amount"])):
		flag = 3	# Payment is not a numerical value
	else:
		session["client_name"] = transaction_dic['client_name']
		session["payment_id"] = int(transaction_dic['payment_id'])
		session["comments"] = transaction_dic['comments']
		session["payment_amount"] = float(transaction_dic["payment_amount"])
		session["balance"] = session["account"] - session["payment_amount"]
	return jsonify({"flag": flag})


###################################################################
# Function:		print_invoice
# Purpose:		Generate a PDF invoice
# Return vals: 	A PDF invoice
###################################################################
@views.route('/print-invoice')
@login_required
def print_invoice():
	global g_utc_dt, g_invoice_dt
	utc_dt = datetime.now(tz = g_utc)
	g_invoice_dt = utc_dt.astimezone(pytz.timezone(g_timezone))  
	day = g_invoice_dt.day
	year = g_invoice_dt.year
	months_dic = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", \
		8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
	month = months_dic[g_invoice_dt.month]
	hour = 12 if (g_invoice_dt.hour % 12 == 0) else (g_invoice_dt.hour % 12)
	period = "AM" if (g_invoice_dt.hour) < 12 else "PM"
	minute = g_invoice_dt.minute
	minute_formatted = str(minute) if minute > 9 else '0' + str(minute)
	date = month + " " + str(day) + ", " + str(year)
	time = str(hour) + ":" + minute_formatted + " " + period

	payment = db.session.query(Payment.payment_type).filter_by(id = session['payment_id']).all()
	formatted_account = "{:,.2f}".format(round(session["account"], 2))
	formatted_payment = "{:,.2f}".format(round(session["payment_amount"], 2))
	formatted_balance = "{:,.2f}".format(round(session["balance"], 2))

	invoice_number = 24 # Need to retrieve from DB
	client_address = "87 Private St. Seattle, WA" # Need to retrieve from DB
	client_email = "smith@gmail.com" # Need to retrieve from DB
	client_telno = "990-302-1898" # Need to retrieve from DB

	rendered = render_template("invoice.html", invoice_number = invoice_number, client_name = session["client_name"], \
		payment = payment[0][0], items = session["items"], account = formatted_account, payment_amount = formatted_payment, \
		balance = formatted_balance, date = date, time = time, client_address = client_address, client_email = client_email, \
		client_telno = client_telno) 
	pdf = pdfkit.from_string(rendered, False)
	response = make_response(pdf)
	response.headers['Content-Type'] = 'application/pdf'
	response.headers['Content-Disposition'] = 'inline; filename=invoice.pdf'
	session["printed_invoice"] = 1
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
	if (not session["printed_invoice"]):
		flag = 3
	else:
		#transaction_dic = json.loads(request.data)
		#client_name = transaction_dic["client_name"]
		#payment_id = transaction_dic['payment_id']
		#comments = transaction_dic["comments"]
		transaction = Transaction(
			date = g_invoice_dt,
			user_id = current_user.id,
			#payment_id = payment_id,
			payment_id = session["payment_id"],
			client_name = session["client_name"],
			#client_name = client_name,
			account = session['account'],
			payment = session["payment_amount"],
			balance = session["balance"],
			#comment = comments)
			comment = session["comments"])
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
# Function:		delete_identification
# Purpose:		Delete an identification type
# Return vals: 	Empty JSON
###################################################################
@views.route("/delete-identification", methods = ["POST"])
@login_required
def delete_identification():
	identification_dic = json.loads(request.data)
	identification_id = identification_dic['identification_id']
	identification = Identification.query.get(identification_id)
	if identification:
		db.session.delete(identification)
		db.session.commit()
	return jsonify({})


###################################################################
# Function:		add_client
# Purpose:		Adds a client
# Return vals: 	A call to the configure_service function to render
#				the Service Config page
###################################################################
@views.route("/add-client", methods = ["POST"])
@login_required
def add_client():
	alerts = 0
	client_name = request.form.get("client_name")
	client_address = request.form.get("client_address")
	client_tel = request.form.get("client_tel")
	client_stel = request.form.get("client_stel")
	client_email = request.form.get("client_email")
	id_id = request.form.get("choose_id")
	client_idno = request.form.get("client_idno")

	if (client_name == "" or len(client_name) < 3):
		flash("The name is too short!", category = "error")
		alerts += 1
	if (client_address == "" or len(client_address) < 5):
		flash("The address is too short!", category = "error")
		alerts += 1
	if (client_tel == "" or len(client_tel) < 10):
		flash("The telephone number is too short!", category = "error")
		alerts += 1
	if (alerts == 0):
		new_client = Client(client_name = client_name, address = client_address, tel_number = client_tel, \
			alt_number = client_stel, id_id = id_id, id_number = client_idno, client_email = client_email)
		db.session.add(new_client)
		db.session.commit()
		flash("Client added!", category = "success")
	return clients()



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