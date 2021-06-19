
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_redis import FlaskRedis
from flask_login import LoginManager
from flask_assets import Environment



# Globally accessible libraries
db = SQLAlchemy()
login_manager = LoginManager()
assets = Environment()

r = FlaskRedis()

def create_app():
	
	"""Initialize the core application."""
	app = Flask(__name__, instance_relative_config=False)
	app.config.from_object('config.Config')

    # Initialize Plugins
    #db.init_app(app)
	r.init_app(app)
	db.init_app(app)
	login_manager.init_app(app)
	assets.init_app(app)
	with app.app_context():
        #Import parts of our application
		from .homePage import home
		from .homePage import auth
		from .recordsPage import records
		from .adminPage import admin
        # Register Blueprints
		app.register_blueprint(home.home_bp)
		app.register_blueprint(auth.auth_bp)
		app.register_blueprint(records.records_bp)
		app.register_blueprint(admin.admin_bp)
		
		return app
