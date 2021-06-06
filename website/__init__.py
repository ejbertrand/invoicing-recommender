from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
	# 2. Changed the hierarchy of the views
	from .views.views import views
	from .views.auth import auth
	from .models import User, Note
	app = Flask(__name__)
	# 1. Changed the SECRET KEY
	app.config["SECRET_KEY"] = b'\x95Q\xfe\xbd\x04c7\xf6I\xabR\x86\xb6U6I\xc34k\x13\xf7q\xa8\xd3`3y"\x17\xa6\x1c\xa7'
	app.config["SQLALCHEMY_DATABASE_URI"] = f'sqlite:///{DB_NAME}'
	db.init_app(app)
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
