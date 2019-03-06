from flask import Flask, Blueprint, session
from datetime import timedelta

from flask_sqlalchemy import SQLAlchemy
# from flask_admin import Admin
from flask_cors import CORS

from config import config_by_name

# db = SQLAlchemy()
# admin = Admin()

# def create_app(config_name):
# 	app = Flask(__name__)
# 	app.config.from_object(config_by_name[config_name])
# 	db.init_app(app)
# 	admin.init_app(app)
# 	CORS(app)



# 	from server.views.admin import admin_views

# 	# API
# 	from server.api import user_api
# 	# from server.api import question_category_api
# 	# from server.api import question_api
# 	# from server.api import search_api

# 	app.register_blueprint(user_api.mod, url_prefix='/api/user')
# 	# app.register_blueprint(question_category_api.mod, url_prefix='/api/question-category')
# 	# app.register_blueprint(question_api.mod, url_prefix='/api/question')
# 	# app.register_blueprint(search_api.mod, url_prefix='/api/search')

# 	return app


app = Flask(__name__)
app.config.from_object(config_by_name['prod'])
db = SQLAlchemy(app)
# admin = Admin(app)
CORS(app)



@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1440)

from server.views import admin
app.register_blueprint(admin.admin_views)



# other views
from server.views import general
app.register_blueprint(general.mod)




# API
from server.api import user_api
from server.api import show_api
from server.api import question_api
from server.api import question_tag_api
from server.api import answer_api
# from server.api import search_api

app.register_blueprint(user_api.mod, url_prefix='/api/user')
app.register_blueprint(show_api.mod, url_prefix='/api/show')
app.register_blueprint(question_api.mod, url_prefix='/api/question')
app.register_blueprint(question_tag_api.mod, url_prefix='/api/question_tag')
app.register_blueprint(answer_api.mod, url_prefix='/api/answer')
# app.register_blueprint(search_api.mod, url_prefix='/api/search')







from server.models.user import User, Role
from passlib.hash import sha256_crypt


@app.errorhandler(Exception)
def all_exception_handler(error):
	print(error)
	return 'Something went wrong...', 500

