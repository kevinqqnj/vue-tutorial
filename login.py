#!/usr/bin/env python
# encoding: utf-8
from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, g
from flask_login import (LoginManager, login_required, login_user, current_user, 
                             logout_user, UserMixin)
from flask_debugtoolbar import DebugToolbarExtension
from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp

app = Flask(__name__)   #, static_folder='/dist/static')
 
class UserJWT(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id

users = [
    UserJWT(1, 'joe', 'pass'),
    UserJWT(2, 'user2', 'abcxyz'),
]

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}

def authenticate(username, password):
    print 'auth argvs:', username, password
    user = username_table.get(username, None)
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return user

def identity(payload):
    print 'payload:', payload
    user_id = payload['identity']
    return userid_table.get(user_id, None)

# user models
class User(UserMixin):
    def is_authenticated(self):
        return True
 
    def is_actice(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return "abc@ddd.com"
 
# flask-login
app.secret_key = 's3cr3t#@#$$%%!#Ffgdef12'
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
login_manager.init_app(app)
jwt = JWT(app, authenticate, identity)
toolbar = DebugToolbarExtension(app)

@login_manager.user_loader
def load_user(user_id):
    user = User()
    print user_id, user.get_id()
    return user
    # print query.filter(User.id == 2).first().name
    # print query.get(2).name # 以主键获取，等效于上句
 
auth = Blueprint('auth', __name__)

@app.before_request
def before_request():
#    print g.user
    g.user = current_user
    print 'before_request:', current_user
 
@auth.route('/login', methods=['GET', 'POST'])
def login():
    req = request
    if g.user is not None and g.user.is_authenticated :
        return render_template('login.html', req=g.user)
    if request.method=='POST':
        if request.form.get('name', '') == 'kevin' and request.form.get('password', '') == '111':
            user = User()
            login_user(user)
            return redirect(request.args.get('next') or url_for('index'))
        else: flash('Invalid username or password.')
    return render_template('login.html', req=g.user)

@auth.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return "<body>logout page</body>"


@app.route('/')
def index():
	req = request
	gtxt = g.user
	return render_template('index.html')
#	return "<body>Hello, <br>========= %s <br>========= %s</body>" % (request.headers, (current_user))
     
# test method
@app.route('/test')
@login_required
@jwt_required()
def test():
    return "<body>yes , you are allowed</body>"


@app.route('/__webpack_hmr')
def npm():
    return redirect('http://localhost:8080/__webpack_hmr')

 
app.register_blueprint(auth, url_prefix='/auth')

if __name__ == '__main__':
    app.run(debug=True)
