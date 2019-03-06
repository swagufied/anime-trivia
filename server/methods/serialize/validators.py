from marshmallow import Schema, fields, ValidationError
from server.models.CRUD.base_crud import CRUDHelpers
from server import db

class Length:
	def __init__(self, min, max, msg=None):
		assert(min or max), 'min or max must be specified'
		self.min = min
		self.max = max
		self.msg = msg

	def __call__(self, data):
		length = data and len(data) or 0

		if (self.min and length < self.min) or (self.max and length > self.max):
			msg = self.msg
			if msg is None:
				if self.min and self.max:
					msg = "Field must be between {} and {} character(s) long.".format(self.min, self.max)
				elif self.min:
					msg = "Field must be at least {} character(s) long.".format(self.min)
				else:
					msg = "Field must be less than {} character(s) long.".format(self.max)
				
			raise ValidationError(msg)

def validate_depth(value, child_attr="children", depth=0, limit=None):

	valid_depth = True

	if depth > limit:
		return False

	if child_attr in value and value[child_attr]:
		if isinstance(value[child_attr], list):
			for entry in value[child_attr]:
				valid_depth = validate_depth(entry, child_attr=child_attr, depth=depth+1, limit=limit)
				if not valid_depth:
					return valid_depth
		elif isinstance(value[child_attr], dict):
			valid_depth = validate_depth(value[child_attr], child_attr=child_attr, depth=depth+1, limit=limit)
			if not valid_depth:
				return valid_depth
 
		

	return valid_depth





class validate_enum:
	def __init__(self, table, enum, display_name):
		self.table = table
		self.enum = enum
		self.display_name = display_name
	def __call__(self, value):
		table = CRUDHelpers.get_table(None, self.table, db=db)
		if not value in getattr(table, self.enum).keys():
			raise ValidationError('Invalid {} type'.format(self.display_name))

class validate_table_row:
	def __init__(self, table):
		self.table = table
	def __call__(self, value):
		table = CRUDHelpers.get_table(None, self.table, db=db)
		if not isinstance(value, table):
			raise ValidationError('Invalid table provided.')

# (mix, max)
class Range:
	def __init__(self, min, max, msg=None):
		# assert(min or max), 'min or max must be specified'
		self.min = min
		self.max = max
		self.msg = msg

	def __call__(self, data):

		if data and ((self.min and data < self.min) or (self.max and data > self.max)):
			msg = self.msg
			if msg is None:
				if self.min and self.max:
					msg = "Field value must be between {} and {}.".format(self.min, self.max)
				elif self.min:
					msg = "Field value must be at least {}.".format(self.min)
				else:
					msg = "Field value must be less than {}.".format(self.max)
				
			raise ValidationError(msg)

class PositiveInt:
	def __init__(self, msg=None):
		self.msg=msg
	def __call__(self, value):
		if not isinstance(value, int):
			raise ValidationError('Invalid integer.')
		if value < 1:
			if self.msg:
				raise ValidationError(self.msg)
			else:
				raise ValidationError('Field must be a positive integer.')
