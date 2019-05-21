# encoding: utf-8
from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app, request, url_for, jsonify
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, auth_token_required, http_auth_required
from . import db

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')))

#class Role_User(db.Model):
 #   __tablename__ = 'roles_users'
  #  user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
   #                         primary_key=True)
    #role_name = db.Column(db.Integer, db.ForeignKey('roles.name'))


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

#    @property
#    def password(self):
#        raise AttributeError('password is not a readable attribute')
#
#    @password.setter
#    def password(self, password):
#        self.password_hash = generate_password_hash(password)
#
#    def verify_password(self, password):
#        return check_password_hash(self.password_hash, password)
#
#    def ping(self):
#        self.last_seen = datetime.utcnow()
#        db.session.add(self)

    def subscribe(self, mp):
        if not self.is_subscribing(mp):
            f = Subscription(subscriber_id=self.id, mp_id=mp.id)
            db.session.add(f)

    def unsubscribe(self, mp):
        f = Subscription.filter_by(subscriber_id=self.id, mp_id=mp.id).first()
        if f:
            db.session.delete(f)

    def is_subscribing(self, mp):
        return self.mps.filter_by(mp_id=mp.id).first() is not None

    @property
    def subscribed_mps(self):
    	# SQLAlchemy 过滤器和联结
        return Mp.query.join(Subscription, Subscription.mp_id == Mp.id)\
            .filter(Subscription.subscriber_id == self.id)

    @property
    def subscribed_mps_str(self):
        mplist = [] 
        i = 1
    	# SQLAlchemy 过滤器和联结
        mps = Mp.query.join(Subscription, Subscription.mp_id == Mp.id)\
            .filter(Subscription.subscriber_id == self.id)
        for mp in mps:
        		mplist.append('<Mp-%d %s_%s>' % (mp.id, mp.weixinhao, mp.mpName) )
        		i+=1
#        return '\n\n'.join(mplist)
        return mplist

    def to_json(self):
        json_user = {
            'url': url_for('api.get_user', id=self.id, _external=True),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
#            'posts': url_for('api.get_user_posts', id=self.id, _external=True),
#            'followed_posts': url_for('api.get_user_followed_posts', id=self.id, _external=True),
            'mp_count': self.subscribed_mps.count()
        }
        return json_user

    def __repr__(self):
        return '<User-%d %r>' % (self.id, self.email)

# 公众号
class Mp(db.Model):
    __tablename__ = 'mps'
    id = db.Column(db.Integer, primary_key=True)
    weixinhao = db.Column(db.Text)
    openid = db.Column(db.Text)
    image = db.Column(db.Text)
    summary = db.Column(db.Text)
    sync_time = db.Column(db.DateTime, index=True, default=datetime.utcnow)	# Search.vue: date
    mpName = db.Column(db.Text)
    encGzhUrl = db.Column(db.Text)	# 临时主页
    subscribeDate = db.Column(db.DateTime())
    # 如果加了dynamic, Flask-Admin里会显示raw SQL
    articles = db.relationship('Article', backref='mp', lazy='dynamic')
    subscribers = db.relationship('Subscription',
                               foreign_keys=[Subscription.mp_id],
                               backref=db.backref('mp', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    def to_json(self):
        json_mp = {
            'weixinhao': self.weixinhao,
            'mpName': self.mpName,
            'image': self.image,
            'summary': self.summary,
            'encGzhUrl': self.encGzhUrl,
            'openid': self.openid,
            'subscribeDate': self.subscribeDate,
            'articles_count': self.articles.count()
        }
        return json_mp

    @staticmethod
    def from_json(json_post):
        mps = json_post.get('mps')
        print mps
        if mps is None or mps == '':
            raise ('POST does not have mps')
        Mps = []
        for mp in mps:
#        	print mp
        	Mps.append( Mp(mpName=mp['mpName'], 
        		image=mp['image'], 
        		weixinhao=mp['weixinhao'],
        		encGzhUrl=mp['encGzhUrl'],
        		openid=mp['openid'],
        		) )
        return Mps

    @property	# for Flask-Admin column_formatters use
    def subscribers_str(self):
        ulist = [] 
        i = 1
    	# SQLAlchemy 过滤器和联结
        users = User.query.join(Subscription, Subscription.subscriber_id == User.id)\
            .filter(Subscription.mp_id == self.id)
        for user in users:
        		ulist.append('<User-%d %s>' % (user.id, user.email) )
        		i+=1
#        return '\n\n'.join(mplist)
        return ulist

    @property
    def articles_str(self):
        alist = [] 
        i = 1
    	# SQLAlchemy 过滤器
        articles = Article.query.filter(Article.mp_id == self.id)
        for a in articles:
        		alist.append('<Article-%d %s>' % (a.id, a.title) )
        		i+=1
        return alist

    def __repr__(self):
    	return '<Mp-%d %s>' % (self.id, self.mpName)

# 公众号的文章
class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text)
    author = db.Column(db.Text)
    source_url = db.Column(db.Text)
    content_url = db.Column(db.Text)
    timestamp = db.Column(db.Integer)
    last_sync = db.Column(db.DateTime(), default=datetime.utcnow)
    cover = db.Column(db.Text)
    digest = db.Column(db.Text)
    body_html = db.Column(db.Text)
    fileid = db.Column(db.Integer)
    
    mp_id = db.Column(db.Integer, db.ForeignKey('mps.id'))

    def to_json(self):
        json_article = {
            'title': self.title,
            'content_url': self.content_url,
            'cover': self.cover,
            'digest': self.digest,
            'fileid': self.fileid,
            'timestamp': self.timestamp,
        }
        return json_article

    @staticmethod
    def from_json(article_json):
        title = article_json.get('title')
        return Article(title=title)

    def __repr__(self):
    	return '<Article-%d %s>' % (self.id, self.title)

class Alembic(db.Model):
    __tablename__ = 'alembic_version'
    version_num = db.Column(db.String(32), primary_key=True, nullable=False)

    @staticmethod
    def clear_A():
        for a in Alembic.query.all():
            print a.version_num
            db.session.delete(a)
        db.session.commit()
        print '======== data in Table: Alembic cleared!'

"""
In [1]: u=User()

In [2]: u
Out[2]: <User None>

In [3]: u.password="cat"

In [4]: u.password_hash
Out[4]: 'pbkdf2:sha1:1000$7QUJktd8$4c947175478983d70c939512d22b43d54d9b6e57'

In [5]: u2=User()

In [7]: u2.password="cat"

In [8]: u2.password_hash
Out[8]: 'pbkdf2:sha1:1000$HLSGLeRg$461c67ddf0f78fda561f74ffd94374d215009593'

In [10]: db.session.add(u)
In [11]: db.session.add(u2)
In [13]: db.session.commit()

In [1]: f= User.query.filter_by(id='1').first()
In [15]: f
Out[15]: <User u'Kevin'>

In [9]: f.subscribed_mps.count()
Out[9]: 2

In [16]: f.subscribed_mps.all()[0].id
Out[16]: 2

In [23]: b= Mp.query.filter_by(id='2').first()

In [24]: b.articles
Out[24]: <sqlalchemy.orm.dynamic.AppenderBaseQuery at 0x6ba69e8>

In [25]: b.articles.
b.articles.add_column          b.articles.exists              b.articles.merge_result        b.articles.statement
b.articles.add_columns         b.articles.extend              b.articles.offset              b.articles.subquery
b.articles.add_entity          b.articles.filter              b.articles.one                 b.articles.suffix_with
b.articles.all                 b.articles.filter_by           b.articles.one_or_none         b.articles.union
b.articles.append              b.articles.first               b.articles.options             b.articles.union_all
b.articles.as_scalar           b.articles.first_or_404        b.articles.order_by            b.articles.update
b.articles.attr                b.articles.from_self           b.articles.outerjoin           b.articles.value
b.articles.autoflush           b.articles.from_statement      b.articles.paginate            b.articles.values
b.articles.column_descriptions b.articles.get                 b.articles.params              b.articles.whereclause
b.articles.correlate           b.articles.get_or_404          b.articles.populate_existing   b.articles.with_entities
b.articles.count               b.articles.group_by            b.articles.prefix_with         b.articles.with_for_update
b.articles.cte                 b.articles.having              b.articles.query_class         b.articles.with_hint
b.articles.delete              b.articles.instance            b.articles.remove              b.articles.with_labels
b.articles.dispatch            b.articles.instances           b.articles.reset_joinpoint     b.articles.with_lockmode
b.articles.distinct            b.articles.intersect           b.articles.scalar              b.articles.with_parent
b.articles.enable_assertions   b.articles.intersect_all       b.articles.select_entity_from  b.articles.with_polymorphic
b.articles.enable_eagerloads   b.articles.join                b.articles.select_from         b.articles.with_session
b.articles.except_             b.articles.label               b.articles.selectable          b.articles.with_statement_hint
b.articles.except_all          b.articles.limit               b.articles.session             b.articles.with_transformation
b.articles.execution_options   b.articles.logger              b.articles.slice               b.articles.yield_per
"""