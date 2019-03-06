from .multicrud_helper import *
from server.methods.serialize.models_serialize import UserSchema, ShowSchema, ShowListUpdateSchema, ShowListSchema, UserListSchema
from server.methods.test_print import tprint
from passlib.hash import sha256_crypt
from server import db, app
from marshmallow import ValidationError
from server.models.CRUD.sql_handler import SQLHandler
from server.models.CRUD.query import Query

from server.models.show import Show
from server.methods.user_management.token_management import generate_access_token
from server.models.CRUD.errors import CRUDError, BaseCRUDError
from server.methods.userlist_request.anilist import request_anilist_userlist
from server.methods.userlist_request.mal import request_mal_userlist

"""
USER FUNCTIONS
"""
class UserMultiCRUD:

	# logs in user and returns tokens if successful
	@classmethod
	def login(self, username="", password=""):

		errors = {'errors': {}}
		if not username:
			errors['errors']['username'] = ['Invalid username.']
		if not password:
			errors['errors']['password'] = ['Invalid password.']
		if errors['errors']:
			return errors

		# pull user from db
		conflict_check = {'eq':['username', username]}
		sql_filter = SQLHandler.sqlize_filter(self, conflict_check)
		user = self.read(sql_filter)
		
		# verify user exists
		if 'errors' in user:
			if 'missing' in user['errors']:
				return {'errors':{
					'username': ['Invalid username or password.'],
					'password': ['Invalid username or password.']
					}}
			else:
				return user
		
		# verify password is correct
		if not sha256_crypt.verify(password, user['password']):
			return {'errors':{
				'username': ['Invalid username or password.'],
				'password': ['Invalid username or password.']
				}}

		return_obj = {}
		return_obj['access_token'] = generate_access_token(user['id']).decode('utf-8')

		return return_obj

	# confirm handled by frontend
	@classmethod
	def create(self, **kwargs):

		# check that confirm and password exist
		errors = {'errors':{}}
		if not kwargs.get('password'):
			errors['errors']['password'] = ["Password is required."]
		# if not kwargs.get('confirm'):
		# 	errors['errors']['confirm'] = ["You must confirm your password."]
		if errors['errors']:
			return errors

		# # confirm that passwords match
		# if kwargs['password'] != kwargs['confirm']:
		# 	return {'errors': {
		# 			'password': ["Passwords don't match."],
		# 			"confirm": ["Passwords don't match."]
		# 		}
		# 	}

		# validate user info
		schema = UserSchema()
		validated_schema = schema.load(kwargs)
		

		# hash password
		validated_schema['password'] = sha256_crypt.hash(validated_schema['password'])
		# print('pass', validated_schema['password'])

		# create the category
		try:
			user_row = row_create_helper('User', **validated_schema)
		except Exception as e:
			db.session.rollback()
			raise e

		# commit changes
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			raise e

		print('User create', schema.dump(user_row))

		return {'msg': 'User was successfully registered.'}
	
	@classmethod
	def read(self, user_id, format_output=True):
		try:
			row=Row('User')
			user_row = row.read(user_id)[0]
		except CRUDError as e:
			error = e.messages
			if 'errors' in error and 'missing' in error['errors']:
				error = {'errors':{'missing':['No such user exists.']}}
				return error
			return e.messages
		except Exception as e:
			print(e)
			raise e

		if format_output:
			schema = UserSchema()
			return schema.dump(user_row)
		else:
			return user_row

	# make sure you login before you can update. user check will happen in api route
	@classmethod
	def update(self, user_id, format_output=True, **kwargs):
		
		# check if password is being changed
		if 'confirm' in kwargs:
			if not kwargs.get('password'):
				return {'errors': {
						'password': ["Password is required."]
					}
				}
			# confirm that passwords match
			if kwargs['password'] != kwargs['confirm']:
				return {'errors': {
						'password': ["Passwords don't match."],
						"confirm": ["Passwords don't match."]
					}
				}
				
		# validate user info
		schema = UserSchema(partial=True)
		validated_schema = schema.load(kwargs)
		
		# hash password
		if 'password' in validated_schema:
			validated_schema['password'] = sha256_crypt.hash(validated_schema['password'])

		# create the category
		try:
			user_row = row_update_helper('User',user_id, **validated_schema)
		except Exception as e:
			db.session.rollback()
			raise e

		# update roles
		if 'roles' in validated_schema:
			role_ids = [role.id for role in user_row.roles]
			for role in validated_schema['roles']:
				try:
					role_row = m2m_update_helper('Role', user_row, role['id'], "add_role")
				except Exception as e:
					db.session.rollback()
					raise e

				if role_row.id in role_ids:
					del role_ids[role_ids.index(role_row.id)]

			for role_id in role_ids:
				m2m_update_helper('Role', user_row, role_id, "remove_role")


		# commit changes
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			raise e

		print('User update', schema.dump(user_row))

		return {'msg': 'User was successfully updated.'}

	@classmethod
	def delete(self, user_id):
		row_delete_helper('User', user_id)

		# commit changes
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			raise e

		print('User delete', user_id)

		return {'msg': 'User was successfully deleted.'}










	"""
	ANIMELIST HELPER FUNCTION
	"""
	@classmethod
	def update_showlist_helper(self, user_row, showlist):
		usershow_ids = [usershow.id for usershow in user_row.user_shows]
		usershow_show_ids = [usershow.show_id for usershow in user_row.user_shows]

		print('showlist', showlist)
		for showlist_row in showlist:
			print('showlist round', showlist_row)
			user_show_row = None

			


			# if the relation already exists for the user
			if showlist_row.get('id'):
				if 'show_id' in showlist_row:
					del showlist_row['show_id'] # make sure you cannot edit the relation. just info about it
				if 'user_id' in showlist_row:
					del showlist_row['user_id']
				user_show_row = row_update_helper('user_show', showlist_row['id'], **showlist_row)
			
			# if new relation must be created
			else:
				print('no id found')
				show=None
				if not showlist_row.get('raw_show'):
					show = Show.read(showlist_row.get('show_id'), format_output=False)
				else:
					show=showlist_row.get('raw_show') # if the data is coming from create, dont bother retreiving rows
				if not show:
					continue
				print('show id', show.id)

				


				data = {'show_id': show.id}
				if 'expertise' in showlist_row:
					data['expertise'] = showlist_row['expertise']
				if 'is_removed' in showlist_row:
					data['is_removed'] = showlist_row['is_removed']
	
				
				# check if show exists (might need to rework this method later)
				if show.id in usershow_show_ids:
					user_show_id = [usershow.id for usershow in user_row.user_shows if show.id == usershow.show_id][0]
					user_show_row = row_update_helper('user_show', user_show_id, **data)

				else:

					print('data', data)
					user_show_row = association_proxy_create_helper('user_show', user_row, 'add_show', **data)
					print('done else')

			if user_show_row.id in usershow_ids:
				del usershow_ids[usershow_ids.index(user_show_row.id)]

		for usershow_id in usershow_ids:
			print('sdsd', usershow_id)
			association_proxy_update_helper('user_show', user_row, usershow_id, 'remove_show')

		print(user_row.user_shows)
		print('finishing')




	"""
	SHOWLIST FUNCTIONS
	"""
	@classmethod
	def read_showlist(self, user_id, format_output=True, **kwargs):

		user_row = self.read(user_id, format_output=False)

		if format_output: 
			schema = ShowListSchema(many=True)
			return schema.dump(user_row.user_shows)
		else:
			return user_row.user_shows	

	@classmethod
	def update_showlist(self, user_id, showlist, format_output=True, **kwargs):

		schema = ShowListSchema(many=True)
		validated_schema = schema.load(showlist)
		print('validated schema',validated_schema)
		user_row = self.read(user_id, format_output=False)

		self.update_showlist_helper(user_row, validated_schema)

		
		# commit changes
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			raise e


		if format_output:
			schema = ShowListSchema(many=True)
			return schema.dump(user_row.user_shows)
		else:
			return user_row.user_shows

	@classmethod
	def delete_showlist(self, user_id, user_row=None, **kwargs):

		user_row = self.read(user_id, format_output=False)

		for user_show in user_row.user_shows:
			association_proxy_update_helper('user_show', user_row, user_show.id, 'remove_show')

		# commit changes
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			raise e

		return {"msg": "All internal showlists have been successfully deleted."}




	"""
	USERLIST FUNCTIONS
	"""
	@classmethod
	def read_userlist(self, user_id, format_output=True, **kwargs):

		user_row = self.read(user_id, format_output=False)

		if format_output: 
			schema = UserListSchema(many=True)
			return schema.dump(user_row.userlists)
		else:
			return user_row.user_shows

	@classmethod
	def update_userlist(self, user_id, userlist, format_output=True):

		schema = UserListSchema(many=True)
		validated_schema = schema.load(userlist)
		user_row = self.read(user_id, format_output=False)

		for account in validated_schema:
			# retrieve anime ids of anime user has watched
			username = account.get('username')
			if not username:
				raise BaseCRUDError(key='username', msg='Enter a valid username')

			anime_ids=None
			source=account.get('source')
			if not source:
				raise BaseCRUDError(key='source', msg='You must provide which source the username is associated with.')
			elif source == 1:
				anime_ids = request_anilist_userlist(username)
			elif source == 2:
				anime_ids = request_mal_userlist(username)
			else:
				raise BaseCRUDError(key='source', msg='Unsupported anime database host.')


			if isinstance(anime_ids, dict) and 'error' in anime_ids:
				raise BaseCRUDError(key='username', msg='Either the username is invalid or the host database is down and the animelist cannot be read.')
			elif isinstance(anime_ids, list) and len(anime_ids) >= 1:
				
				# add userlist to db
				userlist_exists = False
				for userlist in user_row.userlists:
					if userlist.username == username and userlist.source == source:
						userlist_exists = True
						userlist_row = row_update_helper('Userlist', userlist.id, **{"username": username, "source":source})
				if not userlist_exists:
					userlist_row = row_create_helper('Userlist', **{"username": username, "source":source, "user_id": user_row.id})

				# retrieve show rows to add to user_show relation
				id_conditionals={'or':[]}
				for anime_id in anime_ids:
					if source==1:
						id_conditionals['or'].append({'eq':['anilist_id', anime_id]})
					elif source==2:
						id_conditionals['or'].append({'eq':['mal_id', anime_id]})

				valid_shows = Query.get_list(Show, None, **{'filters':id_conditionals})

				showlist=[]
				for show in valid_shows:
					showlist.append({
						'raw_show': show,
						'expertise':1,
						'is_removed': False
						})

				self.update_showlist_helper(user_row, showlist)

		
				

			else:
				raise BaseCRUDError(key='generic', msg='Something went wrong requesting userlist data...')
		# commit changes
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			raise e

		if format_output:
			schema = UserListSchema(many=True)
			return schema.dump(user_row.userlists)
		else:
			return user_row.user_shows

	@classmethod
	def delete_userlist(self, user_id, user_row=None, **kwargs):

		user_row = self.read(user_id, format_output=False)
		for userlist in user_row.userlists:
			row_delete_helper('Userlist', userlist.id)

		# commit changes
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			raise e

		return {"msg": "All external showlists have been successfully deleted."}


def read_showlists(user_ids):

	showlists = {}
	for user_id in user_ids:
		user_row = retrieve_row('User', user_id)

		user_showlist = user_row.read_showlist(user_row.id)
		showlists[user_id] = user_showlist
	return showlists