from .multicrud_helper import *
from server.methods.serialize.models_serialize import ShowSchema
from server import db, app
from marshmallow import ValidationError
import time
from server.models.CRUD.base_crud import CRUDHelpers
from server.models.CRUD.errors import BaseCRUDError

import sys

class ShowMultiCRUD:

	@classmethod
	def create(self, format_output=True, handle_parent=False, **kwargs):
		schema = ShowSchema()
		validated_schema = schema.load(kwargs)
		print('passing data')
		return self.update(show_id = None, format_output=format_output, **kwargs)
	
	@classmethod
	def read(self, show_id, format_output=True, raise_errors=False):
		try:
			row=Row('Show')
			show_row = row.read(show_id)[0]
		except CRUDError as e:

			if raise_errors:
				raise e

			error = e.messages
			if 'errors' in error and 'missing' in error['errors']:
				error = {'errors':{'missing':['No such show exists.']}}
				return error
			return e.messages
		except Exception as e:
			print(e)
			raise e

		if format_output:
			schema = ShowSchema()
			return schema.dump(show_row)
		else:
			return show_row

	# make sure you login before you can update. user check will happen in api route
	@classmethod
	def update(self, show_id=None, format_output=True, **kwargs):
		

		schema = ShowSchema(partial=True)
		validated_schema = schema.load(kwargs)

		check_conflict=True
		if not validated_schema.get('mal_id') and not validated_schema.get('anilist_id'):
			print('sdsd')
			check_conflict=False

		# update show
		show_row = None
		if show_id:
			show_row = row_update_helper('Show', show_id, check_conflict=check_conflict, **validated_schema)
		else:
			show_row = row_create_helper('Show', check_conflict=check_conflict, **validated_schema)

		# update parent


		# manage titles
		if 'titles' in validated_schema:

			title_ids = [title_row.id for title_row in show_row.titles]
			for title in validated_schema['titles']:

				title_row=None
				title['show_id'] = show_row.id
				if title.get('id'):

					title_row = retrieve_row('ShowTitle', title['id'])
					if title_row and title_row.parent:
						raise BaseCRUDError(msg="Invalid title ID. Only \"main title\" can be assigned to a show.", key="answers")


					title_row = row_update_helper('ShowTitle', title['id'], **title)
					
					if title_row.id in title_ids:
						del title_ids[title_ids.index(title_row.id)]
				else:
					title_row = row_create_helper('ShowTitle', **title)

				if 'children' in title:
					title_rows = tiered_parent_helper('ShowTitle', title['children'], parent=title_row)
				
			for title_id in title_ids:
				row_delete_helper('ShowTitle', title_id)
	
		# # manage characters
		# if validated_schema.get('characters'):
		# 	character_ids = [character.id for character in show_row.characters]
		# 	for character in validated_schema['characters']:
		# 		character_row = m2m_update_helper('Character', show_row, character['id'], 'add_character')

		# 		if character_row.id in character_ids:
		# 			del character_ids[character_ids.index(character_row.id)]

		# 	for character_id in character_ids:
		# 		m2m_update_helper('Character', show_row, character_id, 'remove_character')


		# commit changes
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			raise e

		# format
		if format_output:
			schema = ShowSchema()
			return schema.dump(show_row)
		else:
			return show_row


	@classmethod
	def delete(self, show_id, **kwargs):

		row_delete_helper('Show', show_id)
		# commit changes
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			raise e

		return {"msg": "The show was successfully deleted."}



# class CharacterMultiCRUD:


# 	@classmethod
# 	def create(self, format_output=True, handle_parent=False, **kwargs):
# 		return self.update(character_id = None, format_output=format_output, **kwargs)
	
# 	@classmethod
# 	def read(self, character_id, format_output=True, raise_errors=False):
# 		try:
# 			row=Row('Character')
# 			character_row = row.read(character_id)[0]
# 		except CRUDError as e:

# 			if raise_errors:
# 				raise e

# 			error = e.messages
# 			if 'errors' in error and 'missing' in error['errors']:
# 				error = {'errors':{'missing':['No such character exists.']}}
# 				return error
# 			return e.messages
# 		except Exception as e:
# 			print(e)
# 			raise e

# 		if format_output:
# 			schema = CharacterSchema()
# 			return schema.dump(character_row)
# 		else:
# 			return character_row

# 	# make sure you login before you can update. user check will happen in api route
# 	@classmethod
# 	def update(self, character_id=None, format_output=True, **kwargs):
		
# 		schema = CharacterSchema()
# 		validated_schema = schema.load(kwargs)


# 		# update character
# 		character_row = None
# 		if character_id:
# 			character_row = row_update_helper('Character', character_id, **validated_schema)
# 		else:
# 			character_row = row_create_helper('Character', **validated_schema)
# 		print(character_row)
# 		# manage names
# 		name_ids = [name.id for name in character_row.names]
# 		for name in validated_schema['names']:
# 			name['character_id'] = character_row.id
# 			if name.get('id'):
# 				name_row = row_update_helper('CharacterName', name['id'], **name)
# 				del name_ids[name_ids.index(name_row.id)]
# 			else:
# 				name_row = row_create_helper('CharacterName', **name)

# 		for name_id in name_ids:
# 			row_delete_helper('CharacterName', name_id)


# 		if validated_schema.get('shows'):
# 			show_ids = [show.id for show in character_row.shows]
# 			for show in validated_schema['shows']:
# 				show_row = m2m_update_helper('Show', character_row, show['id'], 'add_show')

# 				if show_row.id in show_ids:
# 					del show_ids[show_ids.index(show_row.id)]
# 			for show_id in show_ids:
# 				m2m_update_helper('Show', character_row, show_id, 'remove_show')

		

# 		# commit changes
# 		try:
# 			db.session.commit()
# 		except Exception as e:
# 			db.session.rollback()
# 			raise e

# 		# format
# 		if format_output:
# 			return schema.dump(character_row)
# 		else:
# 			return character_row
