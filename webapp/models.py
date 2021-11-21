from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User (db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key = True)
	email = db.Column(db.String(100), unique = True)
	password = db.Column(db.String(150))
	name = db.Column(db.String(100))
	active = db.Column(db.Integer)
	user_transaction = db.relationship('Transaction')

class Payment (db.Model):
	id = db.Column(db.Integer, primary_key = True)
	type = db.Column(db.String(100), unique = True)
	active = db.Column(db.Integer)
	payment_transaction = db.relationship('Transaction')

class Identification (db.Model):
	id = db.Column(db.Integer, primary_key = True)
	type = db.Column(db.String(100), unique = True)
	active = db.Column(db.Integer)
	identification_client = db.relationship('Client')

class Client (db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(150), nullable = False)
	address = db.Column(db.String(200), nullable = False)
	main_phone = db.Column(db.String(100), nullable = False)
	secondary_phone = db.Column(db.String(100))
	email = db.Column(db.String(100))
	identification_id = db.Column(db.Integer, db.ForeignKey('identification.id'))
	identification_number = db.Column(db.String(50))
	balance = db.Column(db.Numeric(precision = 7, scale = 2, asdecimal = True))
	client_transaction = db.relationship('Transaction')

class Service (db.Model):
	id = db.Column(db.Integer, primary_key = True)
	type = db.Column(db.String(100))
	service_parent_id = db.Column(db.Integer, db.ForeignKey('service.id'))
	active = db.Column(db.Integer)
	service_transaction = db.relationship('Transaction_Details')
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
	state = db.Column(db.String(1))
	type = db.Column(db.String(3))
	transaction_details = db.relationship('Transaction_Details')

class Transaction_Details (db.Model):
	id = db.Column(db.Integer, primary_key = True)
	transaction_id = db.Column(db.Integer, db.ForeignKey('transaction.id'))
	service_id = db.Column(db.Integer)
	subservice_id = db.Column(db.Integer, db.ForeignKey('service.id'))
	total = db.Column(db.Numeric(precision = 7, scale = 2, asdecimal = True))
