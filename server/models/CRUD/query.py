from .sql_handler import SQLHandler
from .base_crud import CRUDHelpers
from server import app, db

"""
parameters:

filters
order_by - NOT TESTED
list_type
search_term - if a specific string is searched for

if list_type = paginate
page
items_per_page

else all items are returned
"""


class Query:



	@staticmethod
	def get_list(table, schema,  **parameters):

		table = CRUDHelpers.get_table(None, table, db=db)
		# print(table)
		#search
		return_query = table.query

		if parameters.get('search_term'):
			filter_criteria = ()
			for col in table.search_cols:
				filter_criteria += (self.col.ilike('%{}%'.format(parameters['search_term'])), )

			return_query = self.query.filter(or_(*filter_criteria))

		if parameters.get('filters'):
			# print('filters')
			# print(parameters['filters'])
			filters = SQLHandler.sqlize_filter(table, parameters['filters'])
			return_query = return_query.filter(*filters)

		if parameters.get('order_by'):
			return_query = return_query.order_by(parameters['order_by'])

		if parameters.get('list_type') == 'paginate':
			return_query = Query.paginate(return_query, **parameters)
		else:
			return_query = return_query.all()
		
		# print('sdsd')
		if schema:
			return schema.dump(return_query)
		else:
			return return_query

	@classmethod
	def paginate(self, query, **parameters):

		page = parameters.get('page') or 1
		ipp = parameters.get('items_per_page') or app.config['ITEMS_PER_PAGE']
		print('ipp', ipp)
		paginate_query = query.paginate(page, ipp, False) 
		return paginate_query.items

