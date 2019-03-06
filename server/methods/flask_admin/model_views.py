from flask import flash
from server import db

from server.models.user import *
from server.models.show import *
from server.models.question import *
from flask_admin.form import rules

from flask_admin.contrib.sqla import ModelView
import warnings
from flask_login import current_user
from wtforms import form, fields, validators
from server.models.CRUD.errors import valid_crud_errors, CRUDError
from marshmallow import ValidationError


class UserView(ModelView):
	column_searchable_list = ['username', 'email', 'roles.name']
	column_exclude_list = ['password']
	column_list = ['id', 'username', 'email', 'roles_static']

	column_labels = {'roles_static': 'roles'}


	form_rules = [
		rules.Header('Personal'),
		rules.Field('username'),
		rules.Field('email'),
		rules.Field('password'),

		rules.Header('Authorization'),
		rules.Field('roles'),

		rules.Header('Show Lists'),
		rules.Field('user_shows'),
		rules.Field('userlists')
	]



	form_widget_args = {
		'username': {
			'readonly': True
		},
		'password': {
			'readonly': True
		},
		'email': {
			'readonly': True
		},}

	expertise_choices = {
		'expertise':[
			(1, 'Casual'),
			(2, 'Expert')
		]
	}
	expertise_args = {
		'expertise':{
			'coerce':int
		}
	}
	source_choices = {
		'source':[
			(1, 'Anilist'),
			(2, 'MAL')
		]
	}
	source_args = {
		'source': {
			'coerce':int
		}
	}
	userlist_widget_args = {
		'last_edited': {
			'disabled': True
		}
	}

	inline_models = [
		(UserShow, dict(form_choices=expertise_choices, form_args=expertise_args) ),
		(Userlist, dict(form_choices=source_choices, form_args=source_args, form_widget_args=userlist_widget_args))
		]

	def is_accessible(self):
		if current_user.is_authenticated:
			return current_user.has_role([1,10], attr='rank') 

	def on_model_change(self, form, model, is_created):
		db.session.rollback()
		# if end date before start date or end date in the past, flag them invalid
		if current_user.is_authenticated and current_user.has_role(1, attr='rank'):
			# set formdata to dicts
			data = form.data
			# print(data)
			roles = []
			for role in data['roles']:
				roles.append({'id': role.id})
			data['roles'] = roles

			result=None
			try:
				if is_created:
					result = User.create(**data)
				else:
					if 'password' in data:
						del data['password']
					result = User.update(model.id, **data)
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
				db.session.rollback()
				raise validators.ValidationError(result['errors'])
			else:
				return True

		else:
			raise validators.ValidationError('You are not authorized to make these changes')
	
	def on_model_delete(model):
		if current_user.is_authenticated and current_user.has_role(1, attr='rank'):
			super().on_model_delete(model)
		else:
			raise validators.ValidationError('You are not authorized to make these changes')


class RoleView(ModelView):
	can_edit = False
	can_delete = False
	def is_accessible(self):
		if current_user.is_authenticated:
			return current_user.has_role(1, attr='rank')

	def on_model_change(self, form, model, is_created):
		if current_user.is_authenticated and current_user.has_role(1, attr='rank'):
			super().on_model_change(form, model, is_created)
		else:
			raise validators.ValidationError('You are not authorized to make these changes')
	
	def on_model_delete(model):
		if current_user.is_authenticated and current_user.has_role(1, attr='rank'):
			super().on_model_delete(model)
		else:
			raise validators.ValidationError('You are not authorized to make these changes')

 


class ShowView(ModelView):
	column_list = ['id', 'mal_id', 'anilist_id', 'titles']

	column_filters = ['mal_id', 'anilist_id', 'titles']
	column_searchable_list = ['titles.title']

	form_widget_args = {
		'question': {
			'disabled': True
		}
	}
	form_rules = [
		rules.Header('Properties'),
		rules.Field('mal_id'),
		rules.Field('anilist_id'),
		rules.Field('titles'),

		rules.Header('Categorization'),
		rules.Field('parent'),
		rules.Field('children'),

		rules.Header('Other'),
		rules.Field('question')
	]
	showtitle_rules = {
		rules.Field('title')
	}

	inline_models = [
		(ShowTitle, dict(form_rules=showtitle_rules)), 
		]

	def is_accessible(self):
		if current_user.is_authenticated:
			return current_user.has_role([1,10], attr='rank')

	def on_model_change(self, form, model, is_created):
		db.session.rollback()
		if current_user.is_authenticated and current_user.has_role([1,10], attr='rank'):
			# set formdata to dicts
			data = form.data
			# print(data)
			children = []
			for child in data['children']:
				children.append({'id': child.id})
			data['children'] = children

			titles = []
			for title in form.titles:
				if not title._should_delete:
					title = title.data
					if 'id' in title and not title['id']:
						del title['id']
					titles.append(title)
			data['titles'] = titles
			
			if 'parent' in data and data['parent']:
				data['parent'] = {'id': data['parent'].id}

			model_id = None
			if not is_created:
				model_id = model.id

			try:
				result = Show.update(show_id=model_id, **data)
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
				db.session.rollback()
				raise validators.ValidationError(result['errors'])
			else:
				return True
		else:
			raise validators.ValidationError('You are not authorized to make these changes')
	
	def on_model_delete(model):
		if current_user.is_authenticated and current_user.has_role([1,10], attr='rank'):
			super().on_model_delete(model)
		else:
			raise validators.ValidationError('You are not authorized to make these changes')



class QuestionView(ModelView):
	column_list = ['id', 'text', 'tags_static', 'answers_static']
	column_filters = ['difficulty', 'shows.titles']
	column_labels = {'tags_static': 'tags', 'answers_static': 'answers', 'text': 'Text (question)'}

	type_choices = {
		'type': [
			(1, 'Picture'),
			(2, 'Video')
		]
	}
	type_args = {
		'type': {
			'coerce': int
		}
	}
	inline_models = [
		(QuestionLink, dict(form_choices=type_choices, form_args=type_args)), 
		(AnswerLink, dict(form_choices=type_choices, form_args=type_args))
		]

	form_rules = [
		rules.Header('Question'),
		rules.Field('text'),
		rules.Field('question_links'),
		rules.Header('Answer'),
		rules.Field('answers'),
		rules.Field('answer_links'),
		rules.Field('autocomplete_answer'),
		rules.Header('Properties'),
		rules.Field('difficulty'),
		rules.Field('shows'),
	]
	form_choices = {
		'difficulty': [
			(1, 'Easy'), 
			(2, 'Difficult'), 
			(3, 'Expert')
			]
		}
	form_widget_args = {
		'id': {
			'readonly': True
		}
	}
	form_overrides = dict(text=fields.TextAreaField)
	form_args = {
		'answers': {
			'query_factory': lambda: Answer.query.filter_by(
				parent_id=None
			)
		},
		'difficulty':{
			'coerce': int
		}
	}


	def is_accessible(self):
		if current_user.is_authenticated:
			return current_user.has_role([1,10], attr='rank') 

	def on_model_change(self, form, model, is_created):
		db.session.rollback()
		if current_user.is_authenticated and current_user.has_role([1,10], attr='rank'):
			data = form.data

			answers = []
			for answer in data['answers']:
				answers.append({'id': answer.id})
			data['answers'] = answers

			shows = []
			for show in data['shows']:
				shows.append({'id': show.id})
			data['shows'] = shows

			question_links = []
			for question_link in form.question_links:
				if not question_link._should_delete:
					question_link = question_link.data
					if 'id' in question_link and not question_link['id']:
						del question_link['id']
					question_links.append(question_link)
			data['question_links'] = question_links

			answer_links = []
			for answer_link in form.answer_links:
				if not answer_link._should_delete:
					answer_link = answer_link.data
					if 'id' in answer_link and not answer_link['id']:
						del answer_link['id']
					answer_links.append(answer_link)
			data['answer_links'] = answer_links

			model_id = None
			if not is_created:
				model_id = model.id

			try:
				result = Question.update(question_id=model_id, **data)
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
				db.session.rollback()
				raise validators.ValidationError(result['errors'])
			else:
				return True
		else:
			raise validators.ValidationError('You are not authorized to make these changes')
	
	def on_model_delete(model):
		if current_user.is_authenticated and current_user.has_role([1,10], attr='rank'):
			super().on_model_delete(model)
		else:
			raise validators.ValidationError('You are not authorized to make these changes')


class AnswerView(ModelView):
	column_list = ['id', 'text', 'children']
	column_searchable_list = ['text']

	form_rules = [
		rules.Header('Main Answer'),
		rules.Field('text'),
		rules.Header('Similar Acceptable Answers'),
		rules.Field('children')
	]

	form_overrides = dict(text=fields.TextAreaField)
	inline_models = [(Answer, dict(form_rules=[rules.Field('text')], form_overrides=form_overrides))]

	def get_query(self):
		return self.session.query(self.model).filter(self.model.parent_id == None)

	def is_accessible(self):
		if current_user.is_authenticated:
			return current_user.has_role([1,10], attr='rank')

	def on_model_change(self, form, model, is_created):
		db.session.rollback()
		if current_user.is_authenticated and current_user.has_role([1,10], attr='rank'):
			data = form.data

			children = []
			for child in form.children:
				if not child._should_delete:
					child = child.data
					if 'id' in child and not child['id']:
						del child['id']
					children.append(child)
			data['children'] = children

			model_id = None
			if not is_created:
				model_id = model.id

			try:
				result = Answer.update(answer_id=model_id, **data)
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
				raise validators.ValidationError(result['errors'])
			else:
				return True
		else:
			raise validators.ValidationError('You are not authorized to make these changes')

	def on_model_delete(model):
		if current_user.is_authenticated and current_user.has_role([1,10], attr='rank'):
			super().on_model_delete(model)
		else:
			raise validators.ValidationError('You are not authorized to make these changes')


class QuestionTagView(ModelView):
	column_list = ['id', 'type', 'name']
	column_searchable_list = ['name']
	column_filters = ['type']


	form_rules = [

		rules.Header('Question Tag'),
		rules.Field('type'),
		rules.Field('name')
	]

	form_choices = {
		'type': [
			(1, 'Category')
			]
		}

	form_args = {
		'type':{
			'coerce': int
		}
	}

	def is_accessible(self):
		if current_user.is_authenticated:
			return current_user.has_role([1,10], attr='rank')

	def on_model_change(self, form, model, is_created):
		db.session.rollback()
		# if end date before start date or end date in the past, flag them invalid
		if current_user.is_authenticated and current_user.has_role([1,10], attr='rank'):

			data = form.data
			# print(data)
			model_id = None
			if not is_created:
				model_id = model.id

			try:
				# result = {} 		
				result = QuestionTag.update(tag_id=model_id, **data)
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
				
				raise validators.ValidationError(result['errors'])
			else:
				return True


			super().on_model_change(form, model, is_created)
		else:
			raise validators.ValidationError('You are not authorized to make these changes')
	
	def on_model_delete(model):
		# if end date before start date or end date in the past, flag them invalid
		if current_user.is_authenticated and current_user.has_role([1,10], attr='rank'):
			super().on_model_delete(model)
		else:
			raise validators.ValidationError('You are not authorized to make these changes')


"""
GENERIC VIEWS
"""

class AdminView(ModelView):
	def is_accessible(self):
		if current_user.is_authenticated:
			return current_user.has_role([1,10], attr='rank')


	def on_model_change(self, form, model, is_created):
		# if end date before start date or end date in the past, flag them invalid
		if current_user.is_authenticated and current_user.has_role([1,10], attr='rank'):
			super().on_model_change(form, model, is_created)
		else:
			raise validators.ValidationError('You are not authorized to make these changes')
	
	def on_model_delete(model):
		# if end date before start date or end date in the past, flag them invalid
		if current_user.is_authenticated and current_user.has_role([1,10], attr='rank'):
			super().on_model_delete(model)
		else:
			raise validators.ValidationError('You are not authorized to make these changes')

"""
MISC VIEWS
"""

class ShowTitleView(AdminView):
	column_list = ['id', 'title', 'show', 'parent']
	column_searchable_list = ['title']
	column_filters = ['title', 'show']

class LinkView(AdminView):
	column_filters = ['type', 'url', 'question']
	column_searchable_list = ['url']


class UserShowView(AdminView):
	# column_searchable_list = ['user', 'email']
	column_filters = ['user', 'show', 'is_removed', 'expertise']


class UserlistView(AdminView):
	column_filters = ['user', 'source', 'username', 'last_edited']