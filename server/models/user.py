from server import db
from .utils.custom_CRUD.user_multicrud import UserMultiCRUD
from server.methods.user_management.authorization import Authorization
from datetime import datetime
from sqlalchemy.ext.associationproxy import association_proxy

user_role = db.Table('user_role',
	db.Column('user_id',db.Integer(),db.ForeignKey('User.id')),
	db.Column('role_id',db.Integer(),db.ForeignKey('Role.id')),
	db.UniqueConstraint('user_id', 'role_id', name='user_role_constraint')
)


class Role(db.Model):
	__tablename__ = 'Role'
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(30), unique=True)
	rank = db.Column(db.Integer, unique=True)

	# TODO: columns for privileges
	_rank_enum = {
		1: 'master admin',
		10: 'admin'
	}

	def __repr__(self):
		return self.name

class User(db.Model, UserMultiCRUD, Authorization):
	__tablename__ = 'User'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(30), unique=True)
	password = db.Column(db.String(80))
	email = db.Column(db.String(100), unique=True)

	roles = db.relationship('Role', secondary=user_role, backref=db.backref('user'), lazy='dynamic')
	shows = association_proxy('user_shows', 'show')
	userlists = db.relationship('Userlist', backref='user')

	roles_static = db.relationship('Role', secondary=user_role, viewonly=True, backref=db.backref('user_static'))

	_immutable_columns = ['username', 'id']

	def __repr__(self):
		if len(self.roles.all()) >= 1:
			roles = [role.name for role in self.roles]
			return "{} ({})".format(self.username, ', '.join(roles))
		
		return self.username

	# role handler
	def add_role(self, role):
		if not self.has_role(role):
			self.roles.append(role)

	def remove_role(self, role):
		if self.has_role(role):
			self.roles.remove(role)

	def has_role(self, role, attr='id'):
		if isinstance(role, (str,int)):
			filters = {attr: role}
			return self.roles.filter_by(**filters).first()
		if isinstance(role,list):
			for r in role:
				filters = {attr: r}
				if self.roles.filter_by(**filters).first():
					return True
			return False
		return self.roles.filter(getattr(Role, attr) == getattr(role, attr)).first()


	# show handler
	def add_show(self, user_show):
		if not self.has_show(user_show):
			self.user_shows.append(user_show)

	def remove_show(self, user_show):
		if self.has_show(user_show):
			self.user_shows.remove(user_show)

	def has_show(self, new_user_show):
		for user_show in self.user_shows:
			if (new_user_show.id and user_show.id == new_user_show.id) or user_show.show_id == new_user_show.show_id: # if either the relation or show exists already
				return True
		return False

	@property
	def is_authenticated(self):
		return True

	@property
	def is_active(self):
		return True

	@property
	def is_anonymous(self):
		return False

	def get_id(self):
		return self.id

	# Required for administrative interface
	def __unicode__(self):
		return self.username

class Userlist(db.Model):

	__tablename__ = 'Userlist'

	id=db.Column(db.Integer, primary_key=True)
	user_id=db.Column(db.Integer, db.ForeignKey('User.id'))
	source = db.Column(db.Integer)
	username= db.Column(db.String(2000))
	last_edited = db.Column(db.DateTime(), onupdate=datetime.utcnow, default=datetime.utcnow)

	_source_enum = {
		1:'anilist',
		2:'mal'
	}


class UserShow(db.Model):

	__table_args__ = (db.UniqueConstraint('user_id', 'show_id', name='user_show_constaint'),)

	id = db.Column(db.Integer, primary_key=True)
	expertise = db.Column(db.Integer)
	user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
	show_id = db.Column(db.Integer, db.ForeignKey('Show.id'))
	is_removed = db.Column(db.Boolean, default=False)

	_expertise_enum = {
		1: 'casual',
		2: 'expert'
	}

	user=db.relationship(User, backref=db.backref('user_shows', cascade='all, delete-orphan'))
	show=db.relationship('Show')

	def __init__(self, user=None, show_id=None, show=None, expertise=1, is_removed=False):
		print('showid', show_id)
		self.user=user
		if show:
			self.show=show
		else:
			self.show_id = show_id
		self.expertise=expertise

	def __repr__(self):
		return "{} - {}".format(self.show, self._expertise_enum[self.expertise])