from flask import Blueprint, request, jsonify, abort
from server.models.show import Show
from server.methods.user_management.token_management import token_required
from server.methods.user_management.authorization import verify_admin
from server.models.CRUD.errors import valid_crud_errors, CRUDError
from marshmallow import ValidationError
from server.methods.serialize.models_serialize import ShowSchema
from server.models.CRUD.query import Query

mod = Blueprint('show_api', __name__)


@mod.route('/',  methods=['GET'])
def get_shows():
    print('accessed!')

    parameters = request.get_json()
    print(parameters)

    schema = ShowSchema(many=True)
    result = Query.get_list(Show, schema, **parameters)

    return jsonify(result)


@mod.route('', methods=['POST'])
@mod.route('/', methods=['POST'])
@token_required
@verify_admin
def create(user_row):
    # print('request', request)
    data = request.get_json()
    # print(data)
    try:
        result = Show.create(**data)
        # print('success')
    except CRUDError as e:
        result = e.messages
    except valid_crud_errors as e:
        result = CRUDError(e).messages
    except ValidationError as e:
        result = {'errors': e.messages}
    

    return jsonify(result)


@mod.route('/<int:show_id>', methods=['GET'])
def read(show_id):
    try:
        result = Show.read(show_id)
    except CRUDError as e:
        result = e.messages
    except valid_crud_errors as e:
        result = CRUDError(e).messages
    
    print(result)
    return jsonify(result)

@mod.route('/<int:show_id>', methods=['PUT'])
@token_required
@verify_admin
def update(user_row, show_id):
    print('updating')
    data = request.get_json()
    try:
        result = Show.update(show_id=show_id, **data)
        print('success')
    except CRUDError as e:
        result = e.messages
    except valid_crud_errors as e:
        result = CRUDError(e).messages
    except ValidationError as e:
        result = {'errors': e.messages}
    

    return jsonify(result)

@mod.route('/<int:show_id>', methods=['DELETE'])
@token_required
@verify_admin
def delete(user_row, show_id):

    try:
        result = Show.delete(show_id)
    except CRUDError as e:
        result = e.messages
    except valid_crud_errors as e:
        result = CRUDError(e).messages
    except ValidationError as e:
        result = {'errors': e.messages}
    

    return jsonify(result)


