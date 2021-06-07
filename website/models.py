from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

#class Note(db.Model):
#	id = db.Column(db.Integer, primary_key = True)
#	data = db.Column(db.String(10000))
#	date = db.Column(db.DateTime(timezone = True), default = func.now())
#	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key = True)
	email = db.Column(db.String(150), unique = True)
	password = db.Column(db.String(150))
	first_name = db.Column(db.String(50))
#	notes = db.relationship('Note')

class Transaction(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	date = db.Column(db.DateTime(timezone = True), default = func.now())
	service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
	payment_id = db.Column(db.Integer, db.ForeignKey('payment.id'))
	client_name = db.Column(db.String(100))
	total = db.Column(db.Float)
	comments = db.Column(db.String(250))

class Service(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	type = db.Column(db.String(50), unique = True)
	history = db.relationship('Transaction')

class Payment(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	type = db.Column(db.String(50), unique = True)
	history = db.relationship('Transaction')
