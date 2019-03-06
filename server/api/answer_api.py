from flask import Blueprint, request, jsonify, render_template
from server.models.question import Answer
import json
from server.models.CRUD.query import Query
from server.methods.serialize.models_serialize import AnswerSchema
from server.methods.user_management.token_management import token_required
from server.methods.user_management.authorization import verify_admin
from server.models.CRUD.errors import valid_crud_errors, CRUDError
from marshmallow import ValidationError
# from urllib import unquote

mod = Blueprint('answer_api', __name__)


@mod.route('/',  methods=['GET'])
def get_answer_tags():
    print('accessed!')

    parameters = request.get_json()
    print(parameters)

    schema = AnswerSchema(many=True)
    result = Query.get_list(Answer, schema, **parameters)

    
    return jsonify({'answers':result})

@mod.route('/', methods=['POST'])
@token_required
@verify_admin
def create(user_row):
    data = request.get_json()

    try:
        result = Answer.create(**data)
    except CRUDError as e:
        result = e.messages
    except valid_crud_errors as e:
        result = CRUDError(e).messages
    except ValidationError as e:
        result = {'errors': e.messages}

    return jsonify(result)

@mod.route('/<int:answer_id>', methods=['GET'])
def read(answer_id):

    try:
        result = Answer.read(answer_id)
    except CRUDError as e:
        result = e.messages
    except valid_crud_errors as e:
        result = CRUDError(e).messages
    except ValidationError as e:
        result = {'errors': e.messages}
    
    return jsonify(result)

@mod.route('/<int:answer_id>', methods=['PUT'])
@token_required
@verify_admin
def update(user_row, answer_id):

    data = request.get_json()

    try:
        result = Answer.update(answer_id = answer_id, **data)
    except CRUDError as e:
        result = e.messages
    except valid_crud_errors as e:
        result = CRUDError(e).messages
    except ValidationError as e:
        result = {'errors': e.messages}

    return jsonify(result)
    

@mod.route('/<int:answer_id>', methods=['DELETE'])
@token_required
@verify_admin
def delete(user_row, answer_id):
    try:
        result = Answer.delete(answer_id)
    except CRUDError as e:
        result = e.messages
    except valid_crud_errors as e:
        result = CRUDError(e).messages
    except ValidationError as e:
        result = {'errors': e.messages}
    return jsonify(result)
