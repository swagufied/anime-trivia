# from flask import Blueprint, request, jsonify, abort
# from server.models.show import Character
# from server.methods.user_management.token_management import token_required
# from server.methods.user_management.authorization import verify_admin
# from server.models.CRUD.errors import valid_crud_errors, CRUDError
# from marshmallow import ValidationError
# from server.methods.serialize.models_serialize import CharacterSchema
# from server.models.CRUD.query import Query


# mod = Blueprint('character_api', __name__)

# @mod.route('/',  methods=['GET'])
# def get_characters():
#     print('accessed!')

#     parameters = request.get_json()
#     print(parameters)

#     schema = CharacterSchema(many=True)
#     result = Query.get_list(Character, schema, **parameters)

    
#     return jsonify({'characters': result})


# @mod.route('/create', methods=['POST'])
# # @token_required
# def create():
#     print('creating')
#     print('request', request)
#     data = request.get_json()
#     print('raw data', data)

#     try:
#         result = Character.create(**data)
#         print('success')
#     except CRUDError as e:
#         result = e.messages
#     except valid_crud_errors as e:
#         result = CRUDError(e).messages
#     except ValidationError as e:
#         result = {'errors': e.messages}
#     else:
#         result = {'character':result}

#     return jsonify(result)

# @mod.route('/<int:show_id>', methods=['GET'])
# def read(show_id):
    
#     try:
#         result = Character.read(show_id)
#     except CRUDError as e:
#         result = e.messages
#     except valid_crud_errors as e:
#         result = CRUDError(e).messages
#     else:
#         result = {'character':result}
#     print(result)
#     return jsonify(result)

# @mod.route('/<int:character_id>', methods=['PUT'])
# # @token_required
# # @verify_admin
# def update(character_id):
#     print('updating')
#     print('request', request)
#     data = request.get_json()
#     print('raw data', data)

#     try:
#         result = Character.update(character_id, **data)
#         print('success')
#     except CRUDError as e:
#         result = e.messages
#     except valid_crud_errors as e:
#         result = CRUDError(e).messages
#     except ValidationError as e:
#         result = {'errors': e.messages}
#     else:
#         result = {'character':result}

#     return jsonify(result)

# @mod.route('/<int:user_id>', methods=['DELETE'])
# @token_required
# @verify_admin
# def delete(question_id):
#     return



# """
# USERLIST
# """

# @mod.route('/showlist')
# def create_list():
#     # make request to anilist
#     return

# @mod.route('/showlist', methods=['PUT'])
# def update_list():
#     return

# @mod.route('/showlist', methods=['GET'])
# def read_list():
#     return