from flask import Blueprint, request, jsonify, render_template
from server.models.question import QuestionTag
import json
from server.models.CRUD.query import Query
from server.methods.serialize.models_serialize import QuestionTagSchema
from server.models.CRUD.errors import valid_crud_errors, CRUDError
from marshmallow import ValidationError
from server.methods.user_management.token_management import token_required
from server.methods.user_management.authorization import verify_admin
# from urllib import unquote

mod = Blueprint('question_tag_api', __name__)


@mod.route('/',  methods=['GET'])
def get_question_tags():
    print('accessed!')

    parameters = request.get_json()
    print(parameters)

    schema = QuestionTagSchema(many=True)
    result = Query.get_list(QuestionTag, schema, **parameters)

    
    return jsonify({'question_tags':result})

@mod.route('/', methods=['POST'])
@token_required
@verify_admin
def create(user_row):
    data = request.get_json()

    try:
        result = QuestionTag.create(**data)
    except CRUDError as e:
        result = e.messages
    except valid_crud_errors as e:
        result = CRUDError(e).messages
    except ValidationError as e:
        result = {'errors': e.messages}

    return jsonify(result)

@mod.route('/<int:question_tag_id>', methods=['GET'])
def read(question_tag_id):
    try:
        result = QuestionTag.read(question_tag_id)
    except CRUDError as e:
        result = e.messages
    except valid_crud_errors as e:
        result = CRUDError(e).messages
    except ValidationError as e:
        result = {'errors': e.messages}
   
    return jsonify(result)

@mod.route('/<int:question_tag_id>', methods=['PUT'])
@token_required
@verify_admin
def update(user_row, question_tag_id):

    data = request.get_json()
    try:
        result = QuestionTag.update(tag_id = question_tag_id, **data)
    except CRUDError as e:
        result = e.messages
    except valid_crud_errors as e:
        result = CRUDError(e).messages
    except ValidationError as e:
        result = {'errors': e.messages}
   

    return jsonify(result)
    

@mod.route('/<int:question_tag_id>', methods=['DELETE'])
@token_required
@verify_admin
def delete(user_row, question_tag_id):
    try:
        result = QuestionTag.delete(tag_id = question_tag_id, **data)
    except CRUDError as e:
        result = e.messages
    except valid_crud_errors as e:
        result = CRUDError(e).messages
    except ValidationError as e:
        result = {'errors': e.messages}
   
    return jsonify(result)
