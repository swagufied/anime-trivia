# from server.models.show import *
from server.models.CRUD.errors import *
from server.models.CRUD.sql_handler import SQLHandler
from difflib import SequenceMatcher


# manages parent
def automatic_parent_handler(cls, show_data):

	if not show_data.get('related_shows'):
		base_err = BaseCRUDError(key="related_shows", msg="You must include related shows to automatically handle show groupings.")
		raise CRUDError(base_err)

	else:
		raise_error=False
		if not isinstance(show_data['related_shows'], dict):
			raise_error=True

		for key in show_data['related_shows']:
			if not isinstance(show_data['related_shows'][key], list):
				raise_error=True
			elif not isinstance(show_data['related_shows'][key][0],int):
				raise_error=True
		
		if raise_error:
			base_err = BaseCRUDError(key='related_shows', msg='Related shows must be in format {relation_type:[{"mal_id":int}, ]}')
			raise CRUDError(base_err)


	if show_data.get('parent_id'):
		return show_data

	related_titles = show_data['titles']
	related_shows = []
	parent_set=False
	for relation_type in show_data['related_shows']:
		for mal_id in show_data['related_shows'][relation_type]:

			filter = SQLHandler.sqlize_filter(cls, {
				'eq': ['mal_id', mal_id]
				})

			try:
				related_show = cls.read(filter, format_output=False, raise_error=True)
			except MissingError as e:
				continue

			if related_show.parent and not parent_set:
				show_data['parent_id'] = related_show.parent.id
				parent_set=True
			
			related_titles.extend([title.title for title in related_show.titles])
			related_shows.append(related_show)


	parent_title = autogenerate_show_title(related_titles)

	# create new parent
	new_parent = {
		'titles': [parent_title]
	}
	
	try:
		new_parent_row = cls.create(**new_parent, format_output=False, raise_error=True)
	except CRUDError as e:
		return e.messages
	except Exception as e:
		print(e)
		raise e

	# update children

	for show in related_shows:
		if show. 

		try:
			cls.update(related_show.id, **{'parent_id': new_parent_row.id})
		except CRUDError as e:
			return e.messages
		except Exception as e:
			print(e)
			raise e
	


	show_data['parent_id'] = new_parent_row.id

	return show_data

	
# input list of titles. will try to generate a title that connects all together
def autogenerate_show_title(titles):

	if not titles:
		return None
	elif len(titles) == 1:
		return titles[0]

	titl1 = titles[0]
	for title2 in titles[1:]:
		match = SequenceMatcher(None, title1, title2).find_longest_match(0, len(title1), 0, len(title2))
		title1 = match

	return title1
