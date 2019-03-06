from datetime import date
from marshmallow import Schema, fields, pprint, pre_load, post_load, EXCLUDE, pre_dump,post_dump
from .validators import *

"""
SHOW SERIALIZATION
"""
class ShowTitleSchema(Schema):
	class Meta:
		unknown = EXCLUDE
	id        = fields.Integer(validate=PositiveInt('Invalid ID.'))
	show_id   = fields.Integer(validate=PositiveInt('Invalid ID.'))
	parent_id = fields.Integer(validate=PositiveInt('Invalid ID.'))
	title     = fields.Str(validate=Length(1,2000), required=True)
	children  = fields.Nested('self', many=True, exclude=['children'])

	@pre_load
	def format_title(schema, in_data):
		if 'title' in in_data:
			if not in_data['title']:
				raise ValidationError('Title is a required field.', 'title')
			in_data['title'] = in_data['title'].strip().lower()
		return in_data



class ShowSchema(Schema):
	class Meta:
		unknown = EXCLUDE

	id         = fields.Integer(validate=PositiveInt('Invalid ID.'))
	mal_id     = fields.Integer(validate=PositiveInt('Invalid ID.'), allow_none=True)
	anilist_id = fields.Integer(validate=PositiveInt('Invalid ID.'), allow_none=True)
	parent_id  = fields.Integer(validate=PositiveInt('Invalid ID.'), allow_none=True)
	titles     = fields.Nested(ShowTitleSchema, many=True, missing=[], default=[])
	parent     = fields.Nested('self', exclude=['parent', 'children'], missing={}, dump_only=True)
	children   = fields.Nested('self', many=True, exclude=['parent'], missing=[], default=[])

	@pre_load
	def validation_check(schema, in_data):
		if 'titles' in in_data:
			for title in in_data['titles']:
				if not validate_depth(title, limit=1):
					raise ValidationError('Depth limit exceeded. Limit is 1.', 'titles')

		return in_data

	@post_load
	def deformat_show(schema, in_data):

		if 'titles' in in_data:
			if len(in_data['titles']) <= 0:
				raise ValidationError('At least 1 valid title must be provided.', 'titles')

		return in_data



"""
QUESITON SERIALIZATION
"""
class QuestionTagSchema(Schema):
	class Meta:
		unknown = EXCLUDE
	id   = fields.Integer(validate=PositiveInt('Invalid ID.'))
	type = fields.Integer(validate=validate_enum('QuestionTag', "_type_enum", "category"), required=True)
	name = fields.Str(validate=Length(1,2000), required=True)

	@pre_load
	def format_tag(schema, in_data):
		if 'name' in in_data:
			in_data['name'] = in_data['name'].strip().lower()
		return in_data

class QuestionLinkSchema(Schema):
	class Meta:
		unknown = EXCLUDE
	id          = fields.Integer(validate=PositiveInt('Invalid ID.'))
	question_id = fields.Integer(validate=PositiveInt('Invalid ID.'))
	type        = fields.Integer(validate=validate_enum('QuestionLink', "_type_enum", "link"), required=True)
	url         = fields.URL(validate=Length(1,2000), required=True)

class AnswerLinkSchema(Schema):
	class Meta:
		unknown = EXCLUDE
	id          = fields.Integer(validate=PositiveInt('Invalid ID.'))
	question_id = fields.Integer(validate=PositiveInt('Invalid ID.'))
	type        = fields.Integer(validate=validate_enum('AnswerLink', "_type_enum", "link"), required=True)
	url         = fields.URL(validate=Length(1,2000), required=True)

class AnswerSchema(Schema):
	class Meta:
		unknown = EXCLUDE
	id        = fields.Integer(validate=PositiveInt('Invalid ID.'))
	parent_id = fields.Integer(validate=PositiveInt('Invalid ID.'), allow_none=True)
	text      = fields.Str(validate=Length(1,2000))
	children  = fields.Nested('self', many=True, exclude=['parent', 'children'])
	parent    = fields.Nested('self', exclude=['parent', 'children'], default={}, missing={}, allow_none=True)

	@pre_load
	def format(schema, in_data):
		if 'text' in in_data:
			in_data['text'] = in_data['text'].strip()

		elif 'id' in in_data:
			pass
		else:
			raise ValidationError('Either an id or text must be provided.')

		return in_data

class QuestionSchema(Schema):
	class Meta:
		unknown = EXCLUDE

	id            = fields.Integer(validate=PositiveInt('Invalid ID.'), allow_none=True)
	text          = fields.Str(validate=Length(1,2000), required=True)
	difficulty    = fields.Integer(validate=validate_enum('Question', "_difficulty_enum", "difficulty"), required=True)
	provide_hints = fields.Boolean(missing=True, default=True)
	answers       = fields.Nested(AnswerSchema, many=True, required=True)
	tags          = fields.Nested(QuestionTagSchema, many=True, default=[], missing=[])

	shows         = fields.Nested(ShowSchema, many=True, only=['id'])
	question_links = fields.Nested(QuestionLinkSchema, many=True, default=[], missing=[])
	answer_links   = fields.Nested(AnswerLinkSchema, many=True, default=[], missing=[])

	@pre_load
	def validation_check(schema, in_data):
		if 'answers' in in_data:
			for answer in in_data['answers']:
				if not validate_depth(answer, limit=1):
					raise ValidationError('Depth limit exceeded. Limit is 1.', 'answers')

		return in_data




"""
USER
"""
class RoleSchema(Schema):
	class Meta:
		unknown = EXCLUDE
	id = fields.Integer(validate=PositiveInt('Invalid role ID.'))
	name = fields.Str(validate=[validate_enum('Role', '_rank_enum', 'role'), Length(1,30)], required=True)
	rank = fields.Integer(required=True)

	@pre_load
	def strip_whitespaces(schema, in_data):
		if 'name' in in_data:
			in_data['name'] = in_data['name'].strip().lower()
		return in_data

class UserSchema(Schema):
	class Meta:
		unknown = EXCLUDE

	id = fields.Integer(validate=PositiveInt('Invalid user ID.'))
	username = fields.Str(validate=Length(5,30), required=True)
	email = fields.Email(validate=Length(None,100))
	password = fields.Str(validate=Length(8,50), required=True)
	roles = fields.Nested(RoleSchema, many=True)

	@pre_load
	def strip_whitespaces(schema, in_data):
		if 'username' in in_data:
			in_data['username'] = in_data['username'].strip()
		if 'email' in in_data:
			in_data['email'] = in_data['email'].strip()
		return in_data

class UserListSchema(Schema):
	id          = fields.Integer(validate=PositiveInt('Invalid showlist ID.'))
	source      = fields.Integer(validate=validate_enum('Userlist', '_source_enum', 'animelist source'))
	username    = fields.Str()
	last_edited = fields.DateTime(dump_only=True)

	@pre_load
	def format_input(schema, in_data):

		if 'username' in in_data:
			if not 'source' in in_data or not in_data['source']:
				raise ValidationError("If you wish to update a show list with an external list, you must provide the source as well.", "source")
			in_data['username'] = in_data['username'].strip()

		return in_data

class ShowListSchema(Schema):
	class Meta:
		unknown = EXCLUDE
	id = fields.Integer(validate=PositiveInt('Invalid showlist ID.'), allow_none=True)
	show_id = fields.Integer(validate=PositiveInt('Invalid show ID.'), allow_none=True, load_only=True)
	# user = fields.Nested(UserSchema)
	raw_user = fields.Raw(validate=validate_table_row('User'), allow_none=True, load_only=True)
	show = fields.Nested(ShowSchema)
	raw_show = fields.Raw(validate=validate_table_row('Show'), allow_none=True, load_only=True)
	expertise = fields.Integer(validate=validate_enum('user_show', '_expertise_enum', 'expertise'))
	is_removed = fields.Boolean(missing=False, default=False)
	@pre_load
	def check_input(schema, in_data):

		if in_data.get('id'):
			pass
		elif not in_data.get('raw_show') and not in_data.get('show_id'):
			raise ValidationError('You must provide a show database row or show id')
		return in_data

class ShowListUpdateSchema(Schema):
	class Meta:
		unknown = EXCLUDE
	showlist = fields.Nested(ShowListSchema, many=True)
	userlist = fields.Nested(UserListSchema, many=True)
	
	@pre_load
	def format_input(schema, in_data):

		
		if 'userlist' in in_data and 'showlist' in in_data:
			raise ValidationError("Only a username or showlist can be updated at a time. Provide only one.", "username")

		return in_data
	# {
	# "username":"swagu",
	# "source":2
	# }

