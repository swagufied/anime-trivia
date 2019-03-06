from server import db
from .base_crud import BaseCRUD
from .errors import CRUDError, valid_crud_errors

class Row(BaseCRUD):

	db_session = db.session
	_db = db

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)


	"""
	BASECRUD METHOD WRAPPERS
	"""
	def create(self, *args, **kwargs):
		try:
			return super().create(*args, **kwargs)
		except valid_crud_errors as e:
			raise CRUDError(e)

	def read(self, *args, **kwargs):
		try:
			return super().read(*args, **kwargs)
		except valid_crud_errors as e:
			raise CRUDError(e)

	def update(self, *args, **kwargs):
		try:
			return super().update(*args, **kwargs)
		except valid_crud_errors as e:
			raise CRUDError(e)

	def delete(self, *args, **kwargs):
		try:
			return super().delete(*args, **kwargs)
		except valid_crud_errors as e:
			raise CRUDError(e)

	def commit(self, *args, **kwargs):
		try:
			super().commit(*args, **kwargs)
			return True
		except valid_crud_errors as e:
			raise CRUDError(e)


	def flush(self, *args, **kwargs):
		try:
			super().flush(*args, **kwargs)
			return True
		except valid_crud_errors as e:
			raise CRUDError(e)

