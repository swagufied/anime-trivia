from server.models.CRUD.errors import CRUDError, ImmutableError, MissingError, valid_crud_errors
from functools import wraps
from flask import jsonify

class AuthorizationError(Exception):
	_default_msg = "You do not have permission to make these changes."

	def __init__(self, msg=""):
		self.msg=msg or self._default_msg

	@property
	def messages(self):
		err_msg = self.msg
		if not isinstance(err_msg, list):
			err_msg = [err_msg]
		return {'errors': {'authorization':err_msg}}


def verify_admin(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		
		# 1st args must be user (ie token verified)
		verified=False
		for role in args[0].roles:
			if role.rank <= 10:
				verified=True

		if not verified:
			return jsonify(AuthorizationError().messages)

		# if not args[0].has_role(['admin', 'master admin'], attr='name'):
		# 	return jsonify(AuthorizationError().messages)

		print(args, kwargs)
		return f(*args, **kwargs)
	return decorated


# parent of user table
class Authorization:

	@staticmethod
	def check_immutable(target_row, values):

		errors = []
		if hasattr(target_row, '_immutable_columns'):
			for col in getattr(target_row, '_immutable_columns'):
				if col in values and getattr(target_row, col) != values[col]:
					print_columns={}
					if hasattr(target_row, '_print_columns'):
						print_columns = target_row._print_columns
					errors.append(ImmutableError(col, print_columns=print_columns))
		if errors:
			raise CRUDError(errors)

	def verify_authorization(self, fxn, target_id, **values):
		getattr(self, fxn)(target_id, **values)



	# only master admin, self, and admin(if target isnt master admin or admin)
	# only master admin can assign roles
	def edit_user(self, target_id, **values):
		target_row = self.read(target_id, format_output=False)
		# make sure immutable columns
		Authorization.check_immutable(target_row, values)	

		if self.id == target_id: # if you are editing your own information
			
			if 'roles' in values: # you cannot edit your own role
				self_role_ids = [role.id for role in self.roles]
				value_role_ids = []
				for role in values['roles']:
					if 'id' in role:
						value_role_ids.append(role['id'])
					else:
						raise AuthorizationError(msg="You cannot edit your own roles.")

				if set(self_role_ids) != set(value_role_ids):
					raise AuthorizationError(msg="You cannot edit your own roles.")


		else: # if you are editing someone else's information
			
			for column in target_row.__table__.columns: # others cannot edit personal info
				if column.name in values:
					if getattr(target_row, column.name) != values[column.name]:
						raise AuthorizationError(msg="You do not have the authority to change personal user information that is not your own.")

			# (the lower the rank number, the higher the position)
			self_rank = float("inf")
			for role in self.roles:
				if role.rank <= self_rank:
					self_rank = role.rank

			target_rank = float("inf")
			for role in target_row.roles:
				if role.rank <= target_rank:
					target_rank = role.rank

			if self_rank >= target_rank:
				raise AuthorizationError()

		return True

	def delete_user(self, target_id, **values):
		if self.id == target_id or self.has_role(1,attr='rank'):
			return True
		else:
			raise AuthorizationError()

	def verify_self(self, target_id):
		if self.id != target_id:
			raise AuthorizationError()