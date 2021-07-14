from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
DB_NAME = "atcenter"
mail = Mail()

def create_app():
	from .views.views import views
	from .views.auth import auth
	from .models import User
	#------- Flask app creation ---------------------#
	app = Flask(__name__)
	app.config["SECRET_KEY"] = #SOME SECRET KEY
	#------- DB Configuration and Initializattion ---#
	app.config["SQLALCHEMY_DATABASE_URI"] = #SOME DATABASE URI
	db.init_app(app)
	create_database(app)
	#------- Mail Server Configuration --------------#
	app.config['MAIL_SERVER'] = #SOME MAIL SERVER
	app.config['MAIL_PORT'] = #SOME PORT
	app.config['MAIL_USERNAME'] = #SOME USERNAME'
	app.config['MAIL_PASSWORD'] = #SOME PASSWORD
	app.config['MAIL_USE_TLS'] = #SOME CONFIG
	app.config['MAIL_USE_SSL'] = #SOME CONFIG
	mail.init_app(app)
	#------- Blueprints registration ----------------#
	app.register_blueprint(views, url_prefix = '/')
	app.register_blueprint(auth, url_prefix = '/')
	#------- Calling the Login Manager and Loader ---#
	login_manager = LoginManager()
	login_manager.login_view = "auth.login"
	login_manager.init_app(app)
	@login_manager.user_loader
	def load_user(id):
		return User.query.get(int(id))
	return app

def create_database(app):
	db.create_all(app = app)
	print("Database Created!")
