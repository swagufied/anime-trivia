from flask import Blueprint, url_for
from server import app, db

from server.models.user import *
from server.models.show import *
from server.models.question import *

from flask_admin.contrib.sqla import ModelView
import warnings

from server.methods.flask_admin.model_views import *
from server.models.CRUD.errors import valid_crud_errors, CRUDError
from marshmallow import ValidationError

admin_views = Blueprint('admin_views', __name__)


# Flask Admin
import flask_login as login
import flask_admin as admin
from passlib.hash import sha256_crypt
from wtforms import form, fields, validators
from flask_admin import helpers, expose
from flask import Flask, url_for, redirect, render_template, request, flash
from server.models.user import User

login_manager = login.LoginManager()
login_manager.init_app(app)

# Create user loader function
@login_manager.user_loader
def load_user(user_id):
	return db.session.query(User).get(user_id)

class LoginForm(form.Form):
	username = fields.StringField(validators=[validators.required()])
	password = fields.PasswordField(validators=[validators.required()])

	def validate_login(self):
		user = self.get_user()

		if not user:
			self.errors['username'] = 'Invalid username or password'
			self.errors['password'] = 'Invalid username or password'
			return False
			# raise validators.ValidationError('Invalid username or password.')
		print('password', user.password)
		if not sha256_crypt.verify(self.password.data, user.password):
			self.errors['username'] = 'Invalid username or password'
			self.errors['password'] = 'Invalid username or password'
			return False
			# raise validators.ValidationError('Invalid username or password')
		return True

	def get_user(self):
		return db.session.query(User).filter_by(username=self.username.data).first()

class RegistrationForm(form.Form):
	username = fields.StringField(validators=[validators.required(), validators.Length(min=5, max=30)])
	email = fields.StringField(validators=[validators.Email(), validators.Length(max=100)])
	password = fields.PasswordField(validators=[validators.required(), validators.Length(min=8, max=50)])

	def validate_login(self, field):
		if db.session.query(User).filter_by(login=self.login.data).count() > 0:
			raise validators.ValidationError('Duplicate username')

# Create customized index view class that handles login & registration
class MyAdminIndexView(admin.AdminIndexView):

	@expose('/')
	def index(self):
		if not login.current_user.is_authenticated:
			return redirect(url_for('.login_view'))
		return super(MyAdminIndexView, self).index()

	@expose('/login/', methods=('GET', 'POST'))
	def login_view(self):
		form = LoginForm(request.form)

		if helpers.validate_form_on_submit(form):
			user = form.get_user()
			if form.validate_login():
				login.login_user(user)
			else:
				flash('Invalid username or password', 'error')

		if login.current_user.is_authenticated:
			return redirect(url_for('.index'))

		link = '<p>Don\'t have an account? <a href="' + url_for('.register_view') + '">Click here to register.</a></p>'
		self._template_args['form'] = form
		self._template_args['link'] = link


		return super(MyAdminIndexView, self).index()
	
	@expose('/register/', methods=('GET', 'POST'))
	def register_view(self):
		form = RegistrationForm(request.form)
		if helpers.validate_form_on_submit(form):

			try:
				result = User.create(**form.data)
			except CRUDError as e:
				result = e.messages
			except valid_crud_errors as e:
				result = CRUDError(e).messages
			except ValidationError as e:
				result = {'errors': e.messages}
			except Exception as e:
				print(e)
				result = {'errors': {'generic': 'Something went wrong...'}}

			if 'errors' in result:
				flash(result['errors'], 'error')
			else:
				user = User.query.filter_by(username=form.username.data).first()
				login.login_user(user)
			return redirect(url_for('.index'))
		link = '<p>Already have an account? <a href="' + url_for('.login_view') + '">Click here to log in.</a></p>'
		self._template_args['form'] = form
		self._template_args['link'] = link
		return super(MyAdminIndexView, self).index()

	@expose('/logout/')
	def logout_view(self):
		login.logout_user()
		return redirect(url_for('.index'))


admin = admin.Admin(app, 'Anime Trivia', index_view=MyAdminIndexView(), base_template='my_master.html')


with warnings.catch_warnings():
	warnings.filterwarnings('ignore', 'Fields missing from ruleset', UserWarning)

	# User
	admin.add_view(UserView(User, db.session, category="User"))
	admin.add_view(RoleView(Role, db.session, category="User"))
	

	# show
	admin.add_view(ShowView(Show, db.session))

	# question
	admin.add_view(QuestionView(Question, db.session))
	
	# answer
	admin.add_view(AnswerView(Answer, db.session))

	# question tag
	admin.add_view(QuestionTagView(QuestionTag, db.session))


	# misc
	admin.add_view(LinkView(QuestionLink, db.session, category="Misc"))
	admin.add_view(LinkView(AnswerLink, db.session, category="Misc"))
	admin.add_view(UserlistView(Userlist, db.session, category="Misc"))
	admin.add_view(UserShowView(UserShow, db.session, category="Misc"))
	admin.add_view(ShowTitleView(ShowTitle, db.session, category = "Misc"))

