# encoding: utf-8
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_security import UserMixin, RoleMixin
from datetime import datetime

# Create Flask application
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data-dev.sqlite'

db = SQLAlchemy(app)

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')))

# superuser, admin, author, editor, user
class Role(db.Model, RoleMixin):
	__tablename__ = 'roles'	
	id = db.Column(db.Integer(), primary_key=True)
	name = db.Column(db.String(80), unique=True)
	description = db.Column(db.String(255))
	
	def __repr__(self):
		return '<Role %s>' % self.name
    
# 订阅公众号和User是多对多关系
class Subscription(db.Model):
    __tablename__ = 'subscriptions'
    id = db.Column(db.Integer(), primary_key=True)
    # follower_id
    subscriber_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # followed_id
    mp_id = db.Column(db.Integer, db.ForeignKey('mps.id'))
                         #   primary_key=True)
    subscribe_timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
    	return '<Subscription %d-%d>' % (self.subscriber_id, self.mp_id)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    last_login_at = db.Column(db.DateTime())
    current_login_at = db.Column(db.DateTime())
    last_login_ip = db.Column(db.String(63))
    current_login_ip = db.Column(db.String(63))
    login_count = db.Column(db.Integer)
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users'))#, lazy='dynamic'))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    mps = db.relationship('Subscription',
                               foreign_keys=[Subscription.subscriber_id],
                               backref=db.backref('subscriber', lazy='joined'),
                               lazy='dynamic',		# select dynamic subquery
                               cascade='all, delete-orphan')


# Create admin
admin = Admin(app, name='MyAdmin', template_mode='bootstrap3')

# Add model views
admin.add_view(ModelView(Role, db.session))
admin.add_view(ModelView(User, db.session))

app.run()