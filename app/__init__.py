# encoding: utf-8
from flask import Flask, abort, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_security import Security, SQLAlchemyUserDatastore, current_user, \
    UserMixin, RoleMixin, login_required, auth_token_required, http_auth_required
from flask_security.utils import encrypt_password
from flask_admin.contrib import sqla
from flask_admin import Admin, helpers as admin_helpers

db = SQLAlchemy()

# models引用必须在 db/login_manager之后，不然会循环引用
from .models import User, Role

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(datastore=user_datastore)

# Create admin
admin = Admin(name=u'简读Admin')

def create_app(config_name):
	app = Flask(__name__)
	app.config.from_object(config[config_name])
	config[config_name].init_app(app)

	db.init_app(app)
	security.init_app(app)
	admin.init_app(app)

	from .main import main as main_blueprint
	app.register_blueprint(main_blueprint)

	from .api_1_0 import api as api_1_0_blueprint
	app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

	return app
