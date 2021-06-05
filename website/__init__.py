from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail, Message

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
	from .views.views import views
	from .views.auth import auth
	from .models import User, Note
	app = Flask(__name__)
	app.config["SECRET_KEY"] = b'\x95Q\xfe\xbd\x04c7\xf6I\xabR\x86\xb6U6I\xc34k\x13\xf7q\xa8\xd3`3y"\x17\xa6\x1c\xa7'
	app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{DB_NAME}'
	db.init_app(app)
	create_database(app)
	# Define mail configuration
	app.config['MAIL_SERVER'] = 'smtp.gmail.com'
	app.config['MAIL_PORT'] = 465
	app.config['MAIL_USERNAME'] = 'fifo.bertrand@gmail.com'
	app.config['MAIL_PASSWORD'] = 'Piano89FIFO'
	app.config['MAIL_USE_TLS'] = False
	app.config['MAIL_USE_SSL'] = True
	mail = Mail(app)
	msg = Message('Hello', sender = 'fifo.bertrand@gmail.com', recipients = ['eddasjbertrand@gmail.com'])
	msg.body = "Chancho Chanchia, Chiiiiiii"
	with app.app_context():
		mail.send(msg)
	# Finished defining mail configuration
	app.register_blueprint(views, url_prefix = '/')
	app.register_blueprint(auth, url_prefix = '/')
	login_manager = LoginManager()
	login_manager.login_view = "auth.login"
	login_manager.init_app(app)
	@login_manager.user_loader
	def load_user(id):
		return User.query.get(int(id))
	return app

def create_database(app):
	if not path.exists('website/' + DB_NAME):
		db.create_all(app = app)
		print("Created Database!")
