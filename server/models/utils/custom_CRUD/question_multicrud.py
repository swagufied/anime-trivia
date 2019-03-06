from server.methods.serialize.models_serialize import QuestionSchema, QuestionTagSchema
from .multicrud_helper import *
from marshmallow import ValidationError
from server.models.CRUD.row import Row
from server.models.CRUD.errors import CRUDError, BaseCRUDError
from server import db

class QuestionMultiCRUD:

	@classmethod
	def create(self, format_output=True, **kwargs):
		schema = QuestionSchema()
		validated_schema = schema.load(kwargs)
		return self.update(question_id=None, format_output=format_output, **kwargs)

	@classmethod
	def read(self, question_id, format_output=True):

		row = Row('Question')
		question_row = row.read(int(question_id))[0]

		if format_output:
			schema = QuestionSchema()
			return schema.dump(question_row)
		else:
			return question_row

	@classmethod
	def update(self, question_id=None, format_output=True, **kwargs):

		db.session.rollback()
		schema = QuestionSchema(partial=True)
		validated_schema = schema.load(kwargs)
		print('schema',validated_schema)
		#create question
		question_row = None
		if question_id:
			question_row = row_update_helper('Question', question_id, **validated_schema)
		else:
			question_row = row_create_helper('Question', **validated_schema)

		# manage which shows question is associated with
		if 'shows' in validated_schema:
			show_ids = [show.id for show in question_row.shows]
			for show in validated_schema['shows']:
				show_row = m2m_update_helper('Show', question_row, show['id'], 'add_show')
				if show_row.id in show_ids:
					del show_ids[show_ids.index(show_row.id)]
			for show_id in show_ids:
				m2m_update_helper('Show', question_row, show_id, 'remove_show')

		# manage question links
		if 'question_links' in validated_schema:
			link_ids = [link.id for link in question_row.question_links]
			for link in validated_schema['question_links']:
				link['question_id'] = question_row.id
				if link.get('id'):
					link_row = row_update_helper('QuestionLink', link['id'], **link)
					if link_row.id in link_ids:
						del link_ids[link_ids.index(link_row.id)]
				else:
					link_row = row_create_helper('QuestionLink', **link)

			for link_id in link_ids:
				print('retrive', retrieve_row('QuestionLink', link_id))
				row_delete_helper('QuestionLink', link_id)

		# update tags
		if 'tags' in validated_schema:
			tag_ids = [ tag.id for tag in question_row.tags ]
			for tag in validated_schema['tags']:
				tag_row = m2m_update_helper('QuestionTag', question_row, tag['id'], 'add_tag')

				if tag_row.id in tag_ids:
					del tag_ids[tag_ids.index(tag_row.id)]

			for tag_id in tag_ids:
				m2m_update_helper('QuestionTag', question_row, tag_id, 'remove_tag')

		# update answers
		if 'answers' in validated_schema:
			answer_ids = [answer.id for answer in question_row.answers]

			for answer in validated_schema['answers']:

				# make sure that the answer is not part of a subset. It must be the parent
				answer_row = retrieve_row('Answer', answer['id'])
				if answer_row and answer_row.parent:
					raise BaseCRUDError(msg="Invalid answer ID. Only \"main answers\" can be assigned to questions.", key="answers")

				answer_row = m2m_update_helper('Answer', question_row, answer['id'], 'add_answer')
				if answer_row.id in answer_ids:
					del answer_ids[answer_ids.index(answer_row.id)]

			for answer_id in answer_ids:
				m2m_update_helper('Answer', question_row, answer_id, "remove_answer")



		# manage answer links
		if 'answer_links' in validated_schema:
			link_ids = [link.id for link in question_row.answer_links]
			for link in validated_schema['answer_links']:
				link['question_id'] = question_row.id
				if link.get('id'):
					link_row = row_update_helper('AnswerLink', link['id'], **link)
					if link_row.id in link_ids:
						del link_ids[link_ids.index(link_row.id)]
				else:
					link_row = row_create_helper('AnswerLink', **link)

			for link_id in link_ids:
				row_delete_helper('AnswerLink', link_id)

		


		# commit changes
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			raise e

		if format_output:
			return schema.dump(question_row)
		else:
			return question_row



	@classmethod
	def delete(self, question_id, **kwargs):

		row_delete_helper('Question', question_id)

		# commit changes
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			raise e

		return {"msg": "The question was successfully deleted."}



class QuestionTagMultiCRUD:

	@classmethod
	def create(self, format_output=True, **kwargs):
		return self.update(tag_id=None, format_output=format_output, **kwargs)

	@classmethod
	def read(self, question_id, format_output=True):

		row = Row('Question')
		question_row = row.read(int(question_id))[0]

		if format_output:
			schema = QuestionTagSchema()
			return schema.dump(tag_row)
		else:
			return tag_row

	@classmethod
	def update(self, tag_id=None, format_output=True, **kwargs):
		
		schema = QuestionTagSchema()
		validated_schema = schema.load(kwargs)
		
		print('schema', validated_schema)
		# create tag


		conflict_check = {
			'and':[
			{'eq':['type', validated_schema['type']]},
			{'eq':['name', validated_schema['name']]}
			]
		}

		tag_row = None
		if tag_id:
			tag_row = row_update_helper('QuestionTag', tag_id, conflict_check=conflict_check, **validated_schema)
		else:
			tag_row = row_create_helper('QuestionTag', conflict_check=conflict_check, **validated_schema)

		# commit changes
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			raise e

		if format_output:
			return schema.dump(tag_row)
		else:
			return tag_row

	@classmethod
	def delete(self, tag_id, **kwargs):
		row_delete_helper('QuestionTag', tag_id)

		# commit changes
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			raise e

		return {"msg": "The question tag was successfully deleted."}
