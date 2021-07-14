from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key = True)
	email = db.Column(db.String(100), unique = True)
	password = db.Column(db.String(150))
	name = db.Column(db.String(100))
	active = db.Column(db.Integer)
	transactions = db.relationship('Transaction')

class Transaction(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	date = db.Column(db.DateTime(timezone = True), default = func.now())
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	service_id = db.Column(db.Integer)
	subservice_id = db.Column(db.Integer, db.ForeignKey('service.id'))
	payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'))
	client_name = db.Column(db.String(150))
	total = db.Column(db.Float)
	comments = db.Column(db.String(600))

class Service(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	service_type = db.Column(db.String(100))
	parent_id = db.Column(db.Integer, db.ForeignKey('service.id'))
	active = db.Column(db.Integer)
	transactions = db.relationship('Transaction')
	parent = db.relationship("Service", remote_side=[id])

class Payment(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	payment_type = db.Column(db.String(100), unique = True)
	active = db.Column(db.Integer)
	transactions = db.relationship('Transaction')

class Client(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	client_name = db.Column(db.String(150))
