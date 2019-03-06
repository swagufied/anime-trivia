from flask import Blueprint, request, jsonify
from server.models.question import Question
from server.models.CRUD.query import Query
from server.methods.user_management.token_management import token_required
from server.methods.user_management.authorization import verify_admin
from server.methods.serialize.models_serialize import QuestionSchema
from server.models.CRUD.errors import valid_crud_errors, CRUDError
from marshmallow import ValidationError
from server.models.CRUD.query import Query


mod = Blueprint('question_api', __name__)


@mod.route('/',  methods=['GET'])
def get_questions():
    print('accessed!')

    parameters = request.get_json()
    print(parameters)

    schema = QuestionSchema(many=True)
    result = Query.get_list(Question, schema, **parameters)

    
    return jsonify(result)

@mod.route('', methods=['POST'])
@mod.route('/', methods=['POST'])
@token_required
@verify_admin
def create(user_row):
	data = request.get_json()
	
	try:
		result = Question.create(**data)
	except CRUDError as e:
		result = e.messages
	except valid_crud_errors as e:
		result = CRUDError(e).messages
	except ValidationError as e:
		result = {'errors': e.messages}
	

	return jsonify(result)


@mod.route('/<int:question_id>', methods=['GET'])
def read(question_id):
	print('read question')
	
	try:
		result = Question.read(question_id)
		print('success')
	except CRUDError as e:
		result = e.messages
	except valid_crud_errors as e:
		result = CRUDError(e).messages
	except ValidationError as e:
		result = {'errors': e.messages}
	
	return jsonify(result)

@mod.route('/<int:question_id>', methods=['PUT'])
@token_required
@verify_admin
def update(user_row, question_id):
	data = request.get_json()
	
	try:
		result = Question.update(question_id=question_id, **data)
		print('success')
	except CRUDError as e:
		result = e.messages
	except valid_crud_errors as e:
		result = CRUDError(e).messages
	except ValidationError as e:
		result = {'errors': e.messages}
	

	return jsonify(result)

@mod.route('/<int:question_id>', methods=['DELETE'])
@token_required
@verify_admin
def delete(user_row, question_id):
	try:
		result = Question.delete(question_id)
		print('success')
	except CRUDError as e:
		result = e.messages
	except valid_crud_errors as e:
		result = CRUDError(e).messages
	except ValidationError as e:
		result = {'errors': e.messages}
	

	return jsonify(result)
