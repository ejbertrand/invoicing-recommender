from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
mail = Mail()

def create_app():
	from .views.views import views
	from .views.auth import auth
	from .models import User
	#------- Flask app creation ---------------------#
	app = Flask(__name__)
	app.config.from_object('config.DevelopmentConfig')
	db.init_app(app)
	#create_database(app)
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

#def create_database(app):
#	db.create_all(app = app)
#	print("Created Database!")
