
import os



BASEDIR = os.path.abspath(os.path.dirname(__file__))


# SECRET_KEY = 'secret'
# # SECRET_KEY = os.urandom(32)

# SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
# SECURITY_PASSWORD_SALT = 'qwerty'
# ITEMS_PER_PAGE = 100
# SQLALCHEMY_DATABASE_URI = 'postgres://postgres:2dover3d@localhost/jeopardy_trivia'
# SQLALCHEMY_TRACK_MODIFICATIONS = False

class Config:
	# SECRET_KEY = 'secret'
	# SECRET_KEY = os.urandom(32)

	SECURITY_PASSWORD_HASH = 'pbkdf2_sha512'
	SECURITY_PASSWORD_SALT = os.urandom(32)
	ITEMS_PER_PAGE = 100
	BASEDIR = os.path.abspath(os.path.dirname(__file__))
	ACCESS_TOKEN_DURATION = 30 # min


class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
	DEBUG=False
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SECRET_KEY = os.urandom(32)

class DevelopmentConfig(Config):
	# uncomment the line below to use postgres
	SQLALCHEMY_DATABASE_URI = 'postgres://postgres:2dover3d@localhost/jeopardy_trivia'
	DEBUG = True
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SECRET_KEY = 'secret'




class TestingConfig(Config):
	DEBUG = True
	TESTING = True
	SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'test.db')
	PRESERVE_CONTEXT_ON_EXCEPTION = False
	SQLALCHEMY_TRACK_MODIFICATIONS = False


config_by_name = dict(
	dev=DevelopmentConfig,
	test=TestingConfig,
	prod=ProductionConfig
)

