from .multicrud_helper import *
from server.methods.serialize.models_serialize import AnswerSchema
from server import db, app
from marshmallow import ValidationError
import time
from server.models.CRUD.base_crud import CRUDHelpers

import sys

class AnswerMultiCRUD:

	@classmethod
	def create(self, format_output=True, handle_parent=False, **kwargs):
		schema = AnswerSchema()
		validated_schema = schema.load(kwargs)
		return self.update(answer_id = None, format_output=format_output, **kwargs)
	
	@classmethod
	def read(self, answer_id, format_output=True, raise_errors=False):
		try:
			row=Row('Answer')
			answer_row = row.read(answer_id)[0]
		except CRUDError as e:

			if raise_errors:
				raise e

			error = e.messages
			if 'errors' in error and 'missing' in error['errors']:
				error = {'errors':{'missing':['No such answer exists.']}}
				return error
			return e.messages
		except Exception as e:
			print(e)
			raise e

		if format_output:
			schema = AnswerSchema()
			return schema.dump(answer_row)
		else:
			return answer_row

	@classmethod
	def update(self, answer_id=None, format_output=True, **kwargs):
		# db.session.row_delete_helperback()
		schema = AnswerSchema(partial=True)
		validated_schema = schema.load(kwargs)

		conflict_check = {
			'and':[
			{'eq': ['text', validated_schema['text']]},
			{'eq': ['parent_id', None]}
			]
		}

		# update answer
		answer_row = None
		if answer_id:
			answer_row = row_update_helper('Answer', answer_id, conflict_check=conflict_check, **validated_schema)
		else:
			answer_row = row_create_helper('Answer', conflict_check=conflict_check, **validated_schema)

		
		# update answers
		if 'children' in validated_schema:
			answer_children = tiered_parent_helper('Answer', validated_schema['children'], parent=answer_row)


		# commit changes
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			raise e

		# format
		if format_output:
			return schema.dump(answer_row)
		else:
			return answer_row

	@classmethod
	def delete(self, answer_id):

		row_delete_helper('Answer', answer_id)

		# commit changes
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			raise e

		return {"msg": "The answer was successfully deleted."}
