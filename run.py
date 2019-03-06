# from server import create_app, db
# from flask_script import Manager
# import unittest
# import os

# app = create_app(os.getenv('ENV') or 'test')
# app.app_context().push()
# manager = Manager(app)



# @manager.command
# def run():
# 	app.run()

# @manager.command
# def test():
# 	print('testing server starting...')
# 	db.drop_all()
# 	db.create_all()
# 	app.app_context().push()

# 	# """Runs the unit tests."""
# 	# tests = unittest.TestLoader().discover('tests', pattern='test*.py')
# 	# result = unittest.TextTestRunner(verbosity=2).run(tests)
# 	# if result.wasSuccessful():
# 	# 	return 0
# 	# return 1
	
# 	app.run()

# if __name__ == '__main__':
# 	manager.run()


from server import app
if __name__ == '__main__':
	app.run(debug=True, port=5001)