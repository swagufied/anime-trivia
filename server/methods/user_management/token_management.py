from functools import wraps
from flask import request, jsonify
import jwt
from server import app, db
import operator
from server.models.CRUD.base_crud import CRUDHelpers
from server.models.CRUD.sql_handler import SQLHandler

import datetime

def generate_access_token(public_id, minutes=app.config['ACCESS_TOKEN_DURATION']):
	token = jwt.encode({'public_id': public_id, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)}, app.config['SECRET_KEY'])
	return token

def generate_refresh_token():
	return

# refer to read method of User MultiCRUD - circular import so cannot import User class
def verify_access_token(token):
	data = jwt.decode(token, app.config['SECRET_KEY'])

	# verify valid user
	user_table = CRUDHelpers.get_table(None, 'User', db=db)
	conflict_check = {'eq':['id', data['public_id']]}
	sql_filter = SQLHandler.sqlize_filter(user_table, conflict_check)
	user_row = user_table.read(sql_filter, format_output=False)

	if hasattr(user_row, 'errors'):
		raise Exception('INVALID ACCESS TOKEN')
	elif isinstance(user_row, dict) and 'errors' in user_row:
		raise Exception('INVALID ACCESS TOKEN')

	return user_row


def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		access_token=request.headers.get('access_token')

		if not access_token:
			return jsonify({'errors': {
				'token': ['Token is invalid.']
				}}), 401

		try:
			user_row = verify_access_token(access_token)
		except jwt.exceptions.ExpiredSignatureError as e:
			return jsonify({'errors': {
				'token': ['Token is invalid.']
				}}), 401
		except Exception as e:
			if isinstance(e, Exception) and e.__str__() == 'INVALID ACCESS TOKEN':
				return jsonify({'errors': {
					'token': ['Token is invalid.']
					}}), 401
			else:
				raise e


		return f(user_row, *args, **kwargs)
	return decorated