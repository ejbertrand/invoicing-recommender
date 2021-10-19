from flask import Blueprint, render_template, request, flash, jsonify, make_response, session, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.orm import aliased
from sqlalchemy.sql import text as SQLQuery
from sqlalchemy.sql.expression import func
from ..models import Service, Payment, Transaction, User, Identification, Client, Transaction_Details
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
		clients = db.session.query(Client).order_by(Client.name.asc()).all()
		services = db.session.query(Service).filter_by(service_parent_id=None).all()
		payments = db.session.query(Payment).all()
		if (session["transaction_state"] == "ACTIVE"):
			formatted_account = "{:,.2f}".format(round(session["account"], 2))
			formatted_payment = "{:,.2f}".format(round(session["payment_amount"], 2))
			return render_template("home.html", user = current_user, services = services, \
				payments = payments, transaction_state = session["transaction_state"], \
				client_id = session["client_id"], payment_id = session["payment_id"], \
				comments = session["comments"], items = session["items_print"], \
				formatted_payment = formatted_payment, clients = clients, account = formatted_account)
		else:
			return render_template("home.html", user = current_user, services = services, \
				payments = payments, transaction_state = session["transaction_state"], \
				clients = clients)
	except KeyError:
		print("\nOops: A KeyError exception was raised. (Probably no Clients, Services and Payments registered yet.\n")
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
	srv_dict = {service.id:service.type for service in all_services if service.service_parent_id is None}
	subsrv_dict = {service.id:dict() for service in all_services if service.service_parent_id is None}
	for item in subsrv_dict:
		subsrv_dict[item] = {service.id: service.type for service in all_services if (service.service_parent_id == item)}
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
		payment_type = request.form.get("payment_type")
		if len(payment_type) < 3:
			flash("The payment type is too short!", category = "error")
		else:
			new_payment = Payment(type = payment_type, active = 1)
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
		identification_type = request.form.get("identification_type")
		if len(identification_type) < 3:
			flash("The identification form is too short!", category = "error")
		else:
			new_identification = Identification(type = identification_type, active = 1)
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
	transactions = (
		db.session.query(
			Transaction.id,
			Transaction.date,
			User.name,
			Payment.type,
			Client.name,
			Transaction.account,
			Transaction.payment,
			Transaction.balance,
			Transaction.comment
		)
		.join(User)
		.join(Payment)
		.join(Client)
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
			Client.id,
			Client.name,
			Client.main_phone,
			Client.secondary_phone,
			Client.email,
			Identification.type,
			Client.identification_number,
			Client.address,
		)
		.join(Identification)
		.order_by(Client.name.asc())
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
	service_parent_id = service_dic['service_parent_id']
	subservices = db.session.query(Service).filter_by(service_parent_id=service_parent_id).all()
	subservices_lst = [[subservice.id, subservice.type] for subservice in subservices]
	return jsonify(subservices_lst)



#############################################################################
# Function:		get_id_types
# Purpose:		Get the types of IDs avaiable
# Return vals: 	JSON containing a list of tuples containing (ID_id, ID_types)
#############################################################################
@views.route("/get-id-types", methods = ["POST"])
@login_required
def get_id_types():
	identifications_dic = json.loads(request.data)
	chosen_id_type = identifications_dic['chosen_id_type']
	chosen_id = db.session.query(Identification.id).filter_by(type=chosen_id_type).all()
	identifications = db.session.query(Identification).all()
	identifications_lst = [[identification.id, identification.type] for identification in identifications]
	identifications_lst.append(chosen_id[0][0])
	return jsonify(identifications_lst)





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
	session["client_id"] = 0
	session["payment_id"] = 0
	session["comments"] = ""
	session["items"] = []
	session["items_print"] = []
	session["account"] = 0.00
	session["payment_amount"] = 0.00
	session["balance"] = 0.00
	session["printed_invoice"] = 0
	session["invoice_number"] = None
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
	service_id = item_dic["service_id"]
	subservice_id = item_dic["subservice_id"]
	total = float(item_dic["total"])
	session["client_id"] = int(item_dic["client_id"])
	session["payment_id"] = int(item_dic["payment_id"])
	session["comments"] = item_dic["comments"]
	service = db.session.query(Service.type).filter_by(id=service_id).all()[0][0]
	subservice = db.session.query(Service.type).filter_by(id=subservice_id).all()[0][0]
	session["items"].append((service_id, subservice_id, total))
	session["items_print"].append((service, subservice, "{:,.2f}".format((total))))
	session["account"] += float(total)
	session["transaction_state"] = "ACTIVE"
	formatted_account = "{:,.2f}".format(round(session["account"], 2))
	json_response = jsonify({"table": session["items_print"], "account": formatted_account})
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
	row_id = item_dic['row_id']
	total = session["items"][row_id][2]
	session["items"].pop(row_id)
	session["items_print"].pop(row_id)
	#session['account'] -= float(total.replace(',', ''))
	session['account'] -= total
	formatted_account = "{:,.2f}".format(round(session["account"], 2))
	json_response = jsonify({"table": session["items_print"], "account": formatted_account})
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
	session["client_id"] = 0
	session["payment_id"] = 0
	session["comments"] = ""
	session["items"] = []
	session["items_print"] = []
	session["account"] = 0.00
	session["payment_amount"] = 0.00
	session["balance"] = 0.00
	session["printed_invoice"] = 0
	session["invoice_number"] = None
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
		session["client_id"] = int(transaction_dic['client_id'])
		session["payment_id"] = int(transaction_dic['payment_id'])
		session["comments"] = transaction_dic['comments']
		session["payment_amount"] = float(transaction_dic["payment_amount"])
		session["balance"] = session["account"] - session["payment_amount"]
		try:
			session["invoice_number"] = db.session.query(func.max(Transaction.id)).all()[0][0]
			if session["invoice_number"]:
				session["invoice_number"] += + 1
			else:
				session["invoice_number"] = 1
		except Exception as e:
			flag = 4	# Failure on getting the invoice number
			print(e)
	return jsonify({"flag": flag})


###################################################################
# Function:		print_invoice
# Purpose:		Generate a PDF invoice
# Return vals: 	A PDF invoice
###################################################################
@views.route('/print-invoice')
@login_required
def print_invoice():
	try:
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

		client = db.session.query(Client).filter_by(id = session["client_id"]).all()[0]
		payment = db.session.query(Payment.type).filter_by(id = session['payment_id']).all()
		formatted_account = "{:,.2f}".format(round(session["account"], 2))
		formatted_payment = "{:,.2f}".format(round(session["payment_amount"], 2))
		formatted_balance = "{:,.2f}".format(round(session["balance"], 2))
	
		client_name = client.name
		client_address = client.address #"87 Private St. Seattle, WA" # Need to retrieve from DB
		client_email = client.email #"smith@gmail.com" # Need to retrieve from DB
		client_main_phone = client.main_phone #"990-302-1898" # Need to retrieve from DB

		rendered = render_template("invoice.html", invoice_number = session["invoice_number"], client_name = client_name, \
			payment = payment[0][0], items = session["items_print"], account = formatted_account, payment_amount = formatted_payment, \
			balance = formatted_balance, date = date, time = time, client_address = client_address, client_email = client_email, \
			client_main_phone = client_main_phone) 
		pdf = pdfkit.from_string(rendered, False)
		response = make_response(pdf)
		response.headers['Content-Type'] = 'application/pdf'
		response.headers['Content-Disposition'] = 'inline; filename=invoice.pdf'
		session["printed_invoice"] = 1
		
		return (response)
	except Exception as e:
		print(e)
		return (e)


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
		try:
			transaction = Transaction(
				date = g_invoice_dt,
				user_id = current_user.id,
				payment_id = session["payment_id"],
				client_id = session["client_id"],
				account = session['account'],
				payment = session["payment_amount"],
				balance = session["balance"],
				comment = session["comments"])
			db.session.add(transaction)
			for item in session["items"]:
				detail = Transaction_Details(
					transaction_id = session["invoice_number"],
					service_id = item[0],
					subservice_id = item[1],
					total = item[2])
				db.session.add(detail)
			if (session["balance"] != 0):
				client = db.session.query(Client).filter_by(id=int(session["client_id"])).all()[0]
				if (client):
					previous_balance = float(client.balance)
					client.balance = previous_balance + session["balance"]
			db.session.commit()
		except Exception as e:
			flag = 3
			print(e)
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
	service_type = request.form.get("service_type")
	if (service_type is None) or (len(service_type) < 3):
		flash("The service name is too short. It must contain at least 3 characters.", category = "error")
	elif (db.session.query(Service.id).filter(Service.type == service_type, Service.id == None).count() > 0):
		flash("Sorry, that service already exists.", category = "error")
	else:
		new_service = Service(type = service_type, active = 1)
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
	service_parent_id = request.form.get("choose_service")
	subservice_type = request.form.get("subservice_type")
	flags = 0
	if (service_parent_id == '0'):
		flash("Oops, you didn't selected a service.", category = "error")
		flags += 1
	if (subservice_type is None) or (len(subservice_type) < 3):
		flash("The subservice name is too short. It must contain at least 3 characters.", category = "error")
		flags += 1
	elif (db.session.query(Service.id).filter(Service.type == subservice_type, Service.id == service_parent_id).count() > 0):
		flash("Sorry, that subservice already exists under that category.", category = "error")
		flags += 1
	if (flags == 0):
	 	new_subservice = Service(type = subservice_type, service_parent_id = service_parent_id, active = 1)
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
	service_id = service_dic['service_id']
	service = Service.query.get(service_id)
	if service:
		Service.query.filter_by(id=service_id).delete()
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
	subservice_id = subservice_dic['subservice_id']
	subservice = Service.query.get(subservice_id)
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
	flag = 0
	client_dic = json.loads(request.data)
	client_name = client_dic["client_name"]
	client_address = client_dic["client_address"]
	client_main_phone = client_dic["client_main_phone"]
	client_secondary_phone = client_dic["client_secondary_phone"]
	client_email = client_dic["client_email"]
	client_identification_id = client_dic["client_identification_id"]
	if (client_identification_id == '0' or not client_identification_id):
		client_identification_id = db.session.query(func.min(Identification.id)).first()[0]
	client_identification_number = client_dic["client_identification_number"]
	try:
		new_client = Client(name = client_name, address = client_address, main_phone = client_main_phone, \
			secondary_phone = client_secondary_phone, identification_id = client_identification_id, \
			identification_number = client_identification_number, email = client_email, balance = 0)
		db.session.add(new_client)
		db.session.commit()
	except Exception as e:
		flag = 1
		print(e)
	return jsonify({"flag": flag})


###################################################################
# Function:		delete_client
# Purpose:		Deletes a client
# Return vals: 	Empty JSON
###################################################################
@views.route("/delete-client", methods = ["POST"])
@login_required
def	delete_client():
	client_dic = json.loads(request.data)
	client_id = client_dic["client_id"]
	client = Client.query.get(client_id)
	if client:
		db.session.delete(client)
		db.session.commit()
	return jsonify({})


@views.route("/edit-client", methods = ["POST"])
@login_required
def	edit_client():
	client_dic = json.loads(request.data)
	client_id = client_dic["client_id"]
	client_name = client_dic["client_name"]
	client_main_phone = client_dic["client_main_phone"]
	client_secondary_phone = client_dic["client_secondary_phone"]
	client_email = client_dic["client_email"]
	client_identification_type = client_dic["client_identification_type"]
	client_identification_number = client_dic["client_identification_number"]
	client_address = client_dic["client_address"]
	identification = db.session.query(Identification).filter_by(type=client_identification_type).all()[0]
	client = db.session.query(Client).filter_by(id=int(client_id)).all()[0]
	if (client and id):
		updated_client = Client.query.filter_by(id=client.id).first()
		updated_client.name = client_name
		updated_client.main_phone = client_main_phone
		updated_client.secondary_phone = client_secondary_phone
		updated_client.email = client_email
		updated_client.identification_id = identification.id
		updated_client.identification_number = client_identification_number
		updated_client.address = client_address
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