from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
DB_NAME = "database.db"
mail = Mail()

def create_app():
	from .views.views import views
	from .views.auth import auth
	from .models import User#, Note
	app = Flask(__name__)
	app.config["SECRET_KEY"] = b'\x95Q\xfe\xbd\x04c7\xf6I\xabR\x86\xb6U6I\xc34k\x13\xf7q\xa8\xd3`3y"\x17\xa6\x1c\xa7'
	app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{DB_NAME}'
	db.init_app(app)
	app.config['MAIL_SERVER']='smtp.gmail.com'
	app.config['MAIL_PORT'] = 465
	app.config['MAIL_USERNAME'] = 'user@email.com'
	app.config['MAIL_PASSWORD'] = 'myPassword'
	app.config['MAIL_USE_TLS'] = False
	app.config['MAIL_USE_SSL'] = True
	mail.init_app(app)
	app.register_blueprint(views, url_prefix = '/')
	app.register_blueprint(auth, url_prefix = '/')
	create_database(app)
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
