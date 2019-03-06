from sqlalchemy.sql.elements import BooleanClauseList, BinaryExpression
from .errors import MissingError, OverwriteError, CRUDError
from .sql_handler import SQLHandler

class CRUDHelpers:
	
	def primary_key(self):
		for column in self._table.__table__.columns:
			if column.primary_key:
				return column.name

	def unique_columns(self):
			unique_columns = []
			for column in self._table.__table__.columns:
				# print(dir(column))
				# print(column.unique_params)
				if column.unique:
					unique_columns.append(column.name)
			return unique_columns

	def filter_column_values(self, edit_primary=False,**kwargs):
		#pulls all valid values after ensuring - cannot edit primary key
		values={}
		for col in self._columns:
			if col.name in kwargs and (not col.primary_key or edit_primary):
				values[col.name] = kwargs[col.name]
		return values

	def build_default_filter(self, **values):
		out_data = {'or':[]}
		for k in self.unique_columns():
			if k in values:
				v = values[k]
				out_data['or'].append({'eq': [k, v]})
		if not out_data['or']:
			return None
		return out_data

	"""
	ROW METHODS
	"""
	def get_table(self, table, db=None):
		if hasattr(self, '_db'):
			if isinstance(table, str):
				table = [cls for cls in self._db.Model._decl_class_registry.values()
				if isinstance(cls, type) and issubclass(cls, self._db.Model) and cls.__tablename__ == table][0]
		else:
			if isinstance(table, str):
				table = [cls for cls in db.Model._decl_class_registry.values()
				if isinstance(cls, type) and issubclass(cls, db.Model) and cls.__tablename__ == table][0]

		return table

	


"""
this is the base CRUD for each Row object.
"""
class BaseCRUD(CRUDHelpers):


	list_filters = (BooleanClauseList, tuple) # if filters is beyond simple single operator.eq(...)
	single_filters = (BinaryExpression, )

	def __init__(self, table, db=None, session=None):
		self._table = self.get_table(table)
		self._columns = self._table.__table__.columns
		self._session = session or self.db_session
		self._db = db

		if hasattr(self._table, 'print_columns'):
			self._print_columns = self._table.print_columns
		else:
			self._print_columns = {}


	"""
	This method creates a new row in the db. It will automatically check for equality to unique constraints before initializing creation. If 
	you wish to modify the constraints checked the edit the conflict_check input.
	This method does NOT commit or flush

	conflict_check - a filter to catch values that violate unique constraint. see SQLHandler.sqlize_filter for formatting variable input
					if set as None, no conflict check will occur and a create will directly be instigated
	edit_primary - if you wish to designate the primary key's value
	values - the values of the columns
	"""
	def create(self, conflict_check={}, edit_primary=False, check_conflict=True,  **values):
		values = self.filter_column_values(edit_primary=edit_primary,**values)

		# check for possible conflicts, especially in unique columns
		if check_conflict:
			tuple_conflict_check, conflict_check = self.conflict_check_clean(conflict_check, **values)
			if tuple_conflict_check:
				self.conflict_check_method(tuple_conflict_check, conflict_check=conflict_check, **values)
		# start creating
		row = self._table(**values)
		self._session.add(row)
		self.flush()
		return row

	"""
	This method reads rows in the db according to filters provided.

	arg - must be of type int (will be assumed to be primary key), BooleanClauseList, BinaryExpression, or an output of SQLHandler.sqlize_filter
	query_limit - if arg of type int is not provided, this designates how many rows will be returned. if None, all rows will be returned
	"""
	def read(self, arg, query_limit=1, **kwargs):

		return_data = []

		if not arg:

			pass
		elif isinstance(arg, self.list_filters):

			# print('READ: {}'.format(*arg))
			if not query_limit:
				return_data = self._table.query.filter(*arg).all()
			else:
				return_data = self._table.query.filter(*arg).limit(query_limit).all()

		elif isinstance(arg, self.single_filters):

			# print('READ: {}'.format(arg))
			if not query_limit:
				return_data = self._table.query.filter(arg).all()
			else:
				return_data = self._table.query.filter(arg).limit(query_limit).all()

		else:
			# print('READ: {}.primary_key = {}'.format(self._table.__tablename__, arg))
			return_data = [self._table.query.get(arg)]
		return_data = [row for row in return_data if row]

		if not return_data:
			raise MissingError(tablename=self._table.__tablename__, data=arg)

		return return_data

	"""
	This method updates a row. Will automatically check changed columns that are unique based on equality. If unique checks should be implemented
	use modify conflict_check input

	check_conflicts - if True, changed unique columns will be checked. If false, this step is skipped
	edit_primary - if you wish to designate the primary key's value
	conflict_check - a filter to catch values that violate unique constraint. see SQLHandler.sqlize_filter for formatting variable input
					if set as None, no conflict check will occur and a create will directly be instigated
	"""
	def update(self, row_id, edit_primary=False, check_conflicts=True, conflict_check={}, **values):
		values = self.filter_column_values(edit_primary=edit_primary, **values)
		row = self._table.query.get(row_id)
		
		if not row:
			raise MissingError(tablename=self._table.__tablename__, data=row_id)

		#make sure none of the updating values conflict
		if check_conflicts:
			if not conflict_check:

				unique_columns = self.unique_columns()
				or_check = {'or': []}
				for col,val in values.items():
					if col in unique_columns:
						if val != getattr(row, col):
							or_check['or'].append({'eq': [col, val]})
				if or_check['or']:
					conflict_check = {
						'and':[
							{'ne': [self.primary_key(), row_id]}, 
							or_check
							]}

					tuple_conflict_check, conflict_check = self.conflict_check_clean(conflict_check)
					self.conflict_check_method(tuple_conflict_check, conflict_check=conflict_check, **values) 

			else:
				conflict_check = {
					'and':[
						conflict_check, 
						{'ne': [self.primary_key(), row_id]}
						]
					}
				tuple_conflict_check, conflict_check = self.conflict_check_clean(conflict_check)
				self.conflict_check_method(tuple_conflict_check, conflict_check=conflict_check, **values) 
			# print('conflict check',conflict_check)
		# print(values)
		for key in values:
			setattr(row, key, values[key])

		self.flush()
		return row

	"""
	this method deletes a row.

	row_id - this must be the primary key of the row you wish to delete. this is no commit or flush in this method
	"""
	def delete(self, row_id):
		row = self._table.query.get(row_id)
		if not row:
			raise MissingError(tablename=self._table.__tablename__, data=row_id)
		self._session.delete(row)
		self.flush()
		return row

	def commit(self):
		try:
			self._session.commit()
		except:
			self._session.rollback()
			raise
	
	def flush(self):
		try:
			self._session.flush()
		except:
			self._session.rollback()
			raise

	def rollback(self):
		self._session.rollback()


	"""
	FILTER HELPED METHODS
	"""
	# returns a filter in format for sqlalchemy
	def conflict_check_clean(self, conflict_check, **values):
		tuple_conflict_check = None
		if isinstance(conflict_check, dict):
			if not conflict_check: # if conflict check is empty, use default
				conflict_check = self.build_default_filter(**values)

				if not conflict_check:
					return None, conflict_check
			tuple_conflict_check = SQLHandler.sqlize_filter(self._table, conflict_check, **values)
			
		else: # if a personalized check is input
			tuple_conflict_check = conflict_check

		return tuple_conflict_check, conflict_check

	# checks for conflict. raises overwrite error if conflict exists
	def conflict_check_method(self, tuple_conflict_check, conflict_check={}, **values):
		if tuple_conflict_check and (isinstance(tuple_conflict_check, self.list_filters + self.single_filters) or\
			(isinstance(tuple_conflict_check, tuple) and isinstance(*tuple_conflict_check, self.list_filters + self.single_filters))):

			try:
				result = self.read(tuple_conflict_check)
			except MissingError as e:
				pass
			except CRUDError as e:
				if isinstance(e._error, MissingError):
					pass
				else:
					raise e
			except Exception as e:
				raise e
			else:
				if result: # if result is returned, it means that a row that violates the constraints exists
					raise OverwriteError(out_data=result[0], in_data = values, conflict_check=conflict_check, print_columns=self._print_columns)
		else:
			raise Exception('Invalid filter type given to CRUD.')

	