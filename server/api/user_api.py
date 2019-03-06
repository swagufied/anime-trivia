from flask import Blueprint, request, jsonify, abort
from server.models.user import User
from server.methods.user_management.token_management import token_required
from server.methods.user_management.authorization import AuthorizationError
from server.models.CRUD.errors import valid_crud_errors, CRUDError
from marshmallow import ValidationError
from server.models.utils.custom_CRUD.user_multicrud import read_showlists

mod = Blueprint('user_api', __name__)


@mod.route('/login', methods=['POST'])
def login():
	data = request.get_json()
	result = User.login(**data)
	return jsonify(result)

@mod.route('/create', methods=['POST'])
def create():

	data = request.get_json()

	try:
		result = User.create(**data)
	except CRUDError as e:
		result = e.messages
	except valid_crud_errors as e:
		result = CRUDError(e).messages
	except ValidationError as e:
		result = {'errors': e.messages}
   
	return jsonify(result)

@mod.route('/<int:user_id>', methods=['GET'])
def read(user_id):
	# print('reading user')

	try:
		result = User.read(user_id)
	except CRUDError as e:
		result = e.messages
	except valid_crud_errors as e:
		result = CRUDError(e).messages
	except ValidationError as e:
		result = {'errors': e.messages}
	else:
		if 'password' in result:
			del result['password']

		if not 'errors' in result:
			result = {'user':result}
   
	return jsonify(result)

	

@mod.route('/<int:user_id>', methods=['PUT'])
@token_required
def update(user_row, user_id):
	data = request.get_json()

	try:
		user_row.verify_authorization('edit_user', user_id, **data)
	except CRUDError as e:
		result = e.messages
	except valid_crud_errors as e:
		result = CRUDError(e).messages
	except AuthorizationError as e:
		result = e.messages
	
	else:
		try:
			result = User.update(user_id, **data)
		except CRUDError as e:
			result = e.messages
		except valid_crud_errors as e:
			result = CRUDError(e).messages
		except ValidationError as e:
			result = {'errors': e.messages}

	return jsonify(result)

@mod.route('/<int:user_id>', methods=['DELETE'])
@token_required
def delete(user_row, user_id):

	try:
		user_row.verify_authorization('delete_user', user_id)
	except CRUDError as e:
		result = e.messages
	except valid_crud_errors as e:
		result = CRUDError(e).messages
	except AuthorizationError as e:
		result = e.messages
	else:
		try:
			result = User.delete(user_id)
		except CRUDError as e:
			result = e.messages
		except valid_crud_errors as e:
			result = CRUDError(e).messages
		except ValidationError as e:
			result = {'errors': e.messages}

	return jsonify(result)


"""
USERLIST
"""
@mod.route('/<int:user_id>/userlist', methods=['GET'])
def read_userlist(user_id):

	try:
		result = User.read_userlist(user_id)
	except CRUDError as e:
		result = e.messages
	except valid_crud_errors as e:
		result = CRUDError(e).messages
	except ValidationError as e:
		result = {'errors': e.messages}
	
	return jsonify(result)

@mod.route('/<int:user_id>/userlist', methods=['POST', 'PUT'])
@token_required
def update_userlist(user_row, user_id):
	data = request.get_json()

	try:
		user_row.verify_authorization('verify_self', user_id)
	except CRUDError as e:
		result = e.messages
	except valid_crud_errors as e:
		result = CRUDError(e).messages
	except AuthorizationError as e:
		result = e.messages
	else:
		try:
			result = User.update_userlist(user_id, data)
		except CRUDError as e:
			result = e.messages
		except valid_crud_errors as e:
			result = CRUDError(e).messages
		except ValidationError as e:
			result = {'errors': e.messages}

	return jsonify(result)

@mod.route('/<int:user_id>/userlist', methods=['DELETE'])
@token_required
def delete_userlist(user_row, user_id):
	try:
		user_row.verify_authorization('verify_self', user_id)
	except CRUDError as e:
		result = e.messages
	except valid_crud_errors as e:
		result = CRUDError(e).messages
	except AuthorizationError as e:
		result = e.messages
	else:
		try:
			result = User.delete_userlist(user_id, user_row=user_row)
		except CRUDError as e:
			result = e.messages
		except valid_crud_errors as e:
			result = CRUDError(e).messages
		except ValidationError as e:
			result = {'errors': e.messages}
		
	return jsonify(result)



"""
SHOWLIST
"""
@mod.route('/<int:user_id>/showlist', methods=['GET'])
def read_showlist(user_id):

	try:
		result = User.read_showlist(user_id)
	except CRUDError as e:
		result = e.messages
	except valid_crud_errors as e:
		result = CRUDError(e).messages
	except ValidationError as e:
		result = {'errors': e.messages}
	
	return jsonify(result)

# for getting multiple users for the game
@mod.route('/showlist', methods=['POST'])
# @token_required
def read_multiple_showlist():
	data = request.get_json()
	try:
		result = read_showlists(data)
	except CRUDError as e:
		result = e.messages
	except valid_crud_errors as e:
		result = CRUDError(e).messages
	except ValidationError as e:
		result = {'errors': e.messages}
	
	return jsonify(result)


@mod.route('/<int:user_id>/showlist', methods=['POST', 'PUT'])
@token_required
def update_showlist(user_row, user_id):
	data = request.get_json()
	
	try:
		user_row.verify_authorization('verify_self', user_id)
	except CRUDError as e:
		result = e.messages
	except valid_crud_errors as e:
		result = CRUDError(e).messages
	except AuthorizationError as e:
		result = e.messages
	else:
		try:
			result = User.update_showlist(user_id, data)
		except CRUDError as e:
			result = e.messages
		except valid_crud_errors as e:
			result = CRUDError(e).messages
		except ValidationError as e:
			result = {'errors': e.messages}

	return jsonify(result)

@mod.route('/<int:user_id>/showlist', methods=['DELETE'])
@token_required
def delete_showlist(user_row, user_id):
	try:
		user_row.verify_authorization('verify_self', user_id)
	except CRUDError as e:
		result = e.messages
	except valid_crud_errors as e:
		result = CRUDError(e).messages
	except AuthorizationError as e:
		result = e.messages
	else:
		try:
			result = User.delete_showlist(user_id, user_row=user_row)
		except CRUDError as e:
			result = e.messages
		except valid_crud_errors as e:
			result = CRUDError(e).messages
		except ValidationError as e:
			result = {'errors': e.messages}
		

	return jsonify(result)