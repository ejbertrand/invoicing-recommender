from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User (db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key = True)
	user_email = db.Column(db.String(100), unique = True)
	password = db.Column(db.String(150))
	user_name = db.Column(db.String(100))
	user_active = db.Column(db.Integer)
	user_transactions = db.relationship('Transaction')

class Payment (db.Model):
	id = db.Column(db.Integer, primary_key = True)
	payment_type = db.Column(db.String(100), unique = True)
	payment_active = db.Column(db.Integer)
	payment_transactions = db.relationship('Transaction')

class Identification (db.Model):
	id = db.Column(db.Integer, primary_key = True)
	id_type = db.Column(db.String(100), unique = True)
	id_active = db.Column(db.Integer)
	id_clients = db.relationship('Client')

class Client (db.Model):
	id = db.Column(db.Integer, primary_key = True)
	client_name = db.Column(db.String(150), nullable = False)
	address = db.Column(db.String(200), nullable = False)
	tel_number = db.Column(db.String(100), nullable = False)
	alt_number = db.Column(db.String(100))
	client_email = db.Column(db.String(100))
	id_id = db.Column(db.Integer, db.ForeignKey('identification.id'))
	id_number = db.Column(db.String(50))
	client_transactions = db.relationship('Transaction')

class Service (db.Model):
	id = db.Column(db.Integer, primary_key = True)
	service_type = db.Column(db.String(100))
	parent_id = db.Column(db.Integer, db.ForeignKey('service.id'))
	service_active = db.Column(db.Integer)
	service_transactions = db.relationship('Transaction_Details')
	service_parent = db.relationship("Service", remote_side=[id])

class Transaction (db.Model):
	id = db.Column(db.Integer, primary_key = True)
	date = db.Column(db.DateTime(timezone = True), default = func.now())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'))
	client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
	account = db.Column(db.Numeric(precision = 7, scale = 2, asdecimal = True))
	payment = db.Column(db.Numeric(precision = 7, scale = 2, asdecimal = True))
	balance = db.Column(db.Numeric(precision = 7, scale = 2, asdecimal = True))
	comment = db.Column(db.String(600))
	transaction_details = db.relationship('Transaction_Details')

class Transaction_Details (db.Model):
	id = db.Column(db.Integer, primary_key = True)
	transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'))
	service_id = db.Column(db.Integer)
	subservice_id = db.Column(db.Integer, db.ForeignKey('service.id'))
	total = db.Column(db.Numeric(precision = 7, scale = 2, asdecimal = True))
