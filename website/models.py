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
	first_name = db.Column(db.String(50)
#	notes = db.relationship('Note')

class History(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	client_name = db.Column(db.String(250))
	date = db.Column(db.DateTime(timezone = True), default = func.now())
	value = db.Column(db.Float)
	service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
	pay_met_id = db.Column(db.Integer, db.ForeignKey('paymentmethod.id'))

class Service(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	type = db.Column(db.String(150), unique = True)
	history = db.relationship('History')

class PaymentMethod(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	type = db.Column(db.String(100), unique = True)
	history = db.relationship('History')
