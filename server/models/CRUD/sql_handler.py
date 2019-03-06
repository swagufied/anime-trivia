import re
import operator
import sqlalchemy
import sys


class SQLHandler:

	"""
	SEE sqlize_

	is_deleted - (False) if True, the filter will only search for
	"""

	

	def sqlize_filter(table, filter_dict, **values):
		"""
		returns sql filter expression
		table - table on which expression is to be generated
		filter_dict: and,or must be list of single key dicts. key is operator and value is column name
		values: kwargs of values where key is column name and value is the value to be used in the operator

		EX:
		input: {'and': [
					{'eq':'mal_id'},
					{'or':[
						{'gt': 'mal_id'},
						{'eq': 'add_date'}
					]},
					{'eq': ['modify_date', False]}
					]
				}

		output:
		print(*input)
		"MalEntry".mal_id = :mal_id_1 AND ("MalEntry".mal_id > :mal_id_2 OR "MalEntry".add_date = :add_date_1) AND "MalEntry".modify_date = false		"""

		statement = ()
		for k in filter_dict:
			if k in ['and', 'or']:
				ops = () # initialize list of operators
				for v in filter_dict[k]: # list of single dicts [{operator:col_name}, {operator:col_name}]
					if isinstance(v, dict) and len(v.keys()) == 1:
						ops += (*SQLHandler.sqlize_filter(table, v, **values),)
					else:
						print('invalid list value in sqlize_filter: {}'.format(v))
						sys.exit()
				statement += (getattr(sqlalchemy, '{}_'.format(k))(*ops), )
			else:

				a,b = None, None
				if isinstance(filter_dict[k], list): # {operator: [col_name, value]}
					if filter_dict[k][0] in table.__table__.columns: # should be value
						a = getattr(table, filter_dict[k][0])
						b = filter_dict[k][1]
					else:
						raise Exception('Column "{}" doesnt exist in table "{}"'.format(filter_dict[k][0], table.__tablename__))

				elif isinstance(filter_dict[k], str): # {operator: col_name}
					if filter_dict[k] in table.__table__.columns: # should be value
						a = getattr(table, filter_dict[k])
						b = values[filter_dict[k]]
					else:
						raise Exception('Column "{}" doesnt exist in table "{}"'.format(filter_dict[k], table.__tablename__))
				else:
					print('Invalid value for operator: {}'.format(filter_dict[k]))
					sys.exit()
				statement += (getattr(operator, k)(a,b),)
		return statement
