from server.models.CRUD.errors import CRUDError, OverwriteError, BaseCRUDError
from server.models.CRUD.row import Row
from server import db
from server.models.CRUD.base_crud import CRUDHelpers
# from server.methods.test_print import tprint

def retrieve_row(table, row_id):
	row = Row(table)
	return row.read(row_id)[0]

def row_create_helper(table, conflict_check={}, check_conflict=True, **validated_schema):
	try:
		row = Row(table)
		return row.create(conflict_check=conflict_check,check_conflict=check_conflict, **validated_schema)
	except Exception as e:
		db.session.rollback()
		raise e

def row_update_helper(table, row_id,  conflict_check={},check_conflict=True, **validated_schema):
	try:
		row = Row(table)
		return row.update(row_id, conflict_check=conflict_check,check_conflict=check_conflict, **validated_schema)
	except Exception as e:
		db.session.rollback()
		raise e

def row_delete_helper(table, row_id):
	try:
		row = Row(table)
		child_row = row.delete(row_id)
	except Exception as e:
		db.session.rollback()
		raise e
		
def m2m_update_helper(table, parent, row_id, fxn):
	try:
		row = Row(table)
		child_row = row.read(row_id)[0]
		getattr(parent, fxn)(child_row)
		return child_row
	except Exception as e:
		db.session.rollback()
		raise e

def tiered_parent_helper(table, child_list, parent=None, child_attr="children", depth_limit=None):

	child_ids = []
	if parent:
		child_ids = [child.id for child in getattr(parent, child_attr)]
	# print(child_ids)
	child_rows = []
	for child in child_list:

		child_row = None
		if parent:
			child['parent_id'] = parent.id
		if child.get('id'):
			child_row = row_update_helper(table, child['id'], **child)
		else:
			child_row = row_create_helper(table, **child)
		child_rows.append(child_row)
		if child_attr in child:
			tiered_parent_helper(table, child[child_attr], parent=child_row, child_attr=child_attr)
			

	for child_id in child_ids:
		row_delete_helper(table, child_id)

	return child_rows

def association_proxy_create_helper(table, parent, fxn, **values):

	table = CRUDHelpers.get_table(None, table, db=db)

	try:
		child_row = table(**values)
		getattr(parent, fxn)(child_row)
		return child_row
	except Exception as e:
		db.session.rollback()
		raise e

def association_proxy_update_helper(table, parent, row_id, fxn):
	try:
		row = Row(table)
		child_row = row.read(row_id)[0]
		getattr(parent, fxn)(child_row)
		return child_row
	except Exception as e:
		db.session.rollback()
		raise e


# def o2m_update_helper(table, parent, new_children, children="titles", child_attr="title", foreign_key="show_id", **kwargs):


# 	current_children = { getattr(child, child_attr): child for child in getattr(parent, children)}
# 	new_children = { child[child_attr]: child for child in new_children }
# 	update_children = set(current_children.keys()) ^ set(new_children.keys())
	
# 	for child in update_children:
# 		if not child in current_children.keys() and child in new_children.keys():
# 			new_children[child][foreign_key] = parent.id
# 			row_create_helper(table, new_children[child])	
# 		elif not child in new_children.keys() and child in current_children.keys():
# 			try:
# 				row = Row(table)
# 				row.delete(current_children[child].id)
# 			except CRUDError as e:
# 				raise e
# 		elif not child in new_children.keys() and not child in current_children:
# 			raise Exception('A child that isnt a new child or current child was found')
# 		elif child in new_children.keys() and child in current_children:
# 			raise Exception('A child that is both a new child and current child')
# 		else:
# 			raise Exception('Something went wrong...')


# def m2m_update_helper(table, parent, new_children, children="tags", child_attr="name", has_fxn="has_tag", remove_fxn="remove_tag"):

# 	current_children = [getattr(child, child_attr) for child in getattr(parent, children)]


# 	if isinstance(new_children, list) and len(new_children) >= 1 and isinstance(new_children[0], dict) :
# 		new_children = { child[child_attr]: child for child in new_children}
# 	else:
# 		new_children = { getattr(child, child_attr): child for child in new_children}
	
# 	update_children = set(current_children) ^ set(new_children.keys())


# 	out_children = []
# 	for child in update_children: # handle tags that need to be deleted
# 		if not child in current_children and child in new_children.keys():
# 			child_row = m2m_create_helper(table, parent, [ new_children[child] ])[0] # add tag
# 			out_children.append(child_row)
# 		elif not child in new_children.keys() and child in current_children:
# 			child_row = getattr(parent, children).filter_by(**{child_attr: child}).first()
# 			getattr(parent, remove_fxn)(child_row)
# 		elif not child in new_children.keys() and not child in current_children:
# 			raise Exception('A child that isnt a new child or current child was found')
# 		elif child in new_children.keys() and child in current_children:
# 			raise Exception('A child that is both a new child and current child')
# 		else:
# 			raise Exception('Something went wrong...')

# 	for child in current_children: # get remaining tags
# 		if not child in update_children and child in new_children.keys():
# 			child_row = getattr(parent, children).filter_by(**{child_attr: child}).first()
# 			out_children.append(child_row)

# 	return out_children

# def tag_update_helper(table, parent, new_tags):

# 	current_tags = [tag.name for tag in parent.tags]
# 	if 'name' in new_tags[0]:
# 		new_tags = [tag['name'] for tag in new_tags]
# 	update_tags = set(current_tags) ^ set(new_tags)


# 	out_tags = []
# 	for tag in update_tags: # handle tags that need to be deleted
# 		if not tag in current_tags and tag in new_tags:
# 			tag_row = tag_create_helper(table, parent, [{'name':tag}])[0] # add tag
# 			out_tags.append(tag_row)
# 		elif not tag in new_tags and tag in current_tags:
# 			tag = parent.tags.filter_by(name = tag).first()
# 			parent.remove_tag(tag)
# 		elif not tag in new_tags and not tag in current_tags:
# 			raise Exception('A tag that isnt a new tag or current tag was found')
# 		elif tag in new_tags and tag in current_tags:
# 			raise Exception('A tag that is both a new tag and current tag')
# 		else:
# 			raise Exception('Something went wrong...')

# 	for tag in current_tags: # get remaining tags
# 		if not tag in update_tags and tag in new_tags:
# 			tag_row = parent.tags.filter_by(name = tag).first()
# 			out_tags.append(tag_row)


# 	return out_tags

