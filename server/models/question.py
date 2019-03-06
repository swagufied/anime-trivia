from server import db
from .utils.custom_CRUD.question_multicrud import QuestionMultiCRUD, QuestionTagMultiCRUD
from .utils.custom_CRUD.answer_multicrud import AnswerMultiCRUD


question_tag = db.Table('question_tag',
	db.Column('question_id',db.Integer(),db.ForeignKey('Question.id')),
	db.Column('tag_id',db.Integer(),db.ForeignKey('QuestionTag.id')),
	db.UniqueConstraint('question_id', 'tag_id', name='question_tag_constraint')
)

question_answer = db.Table('question_answer',
	db.Column('question_id',db.Integer(),db.ForeignKey('Question.id')),
	db.Column('answer_id',db.Integer(),db.ForeignKey('Answer.id')),
	db.UniqueConstraint('question_id', 'answer_id', name='question_answer_constraint')
)

show_question = db.Table('show_question',
	db.Column('show_id',db.Integer(),db.ForeignKey('Show.id')),
	db.Column('question_id',db.Integer(),db.ForeignKey('Question.id')),
	db.UniqueConstraint('question_id', 'show_id', name='question_show_constraint')
)

"""
QUESTIONS
"""
class Question(db.Model, QuestionMultiCRUD):
	__tablename__ = 'Question'
	id = db.Column(db.Integer, primary_key=True)
	text = db.Column(db.String(2000))
	difficulty = db.Column(db.Integer)
	autocomplete_answer = db.Column(db.Boolean, default=True)

	_difficulty_enum = {
		1: 'Easy',
		2: 'Difficult',
		3: 'Expert'
	}

	answers = db.relationship('Answer', secondary=question_answer, backref=db.backref('question', lazy='dynamic'), lazy='dynamic')
	tags = db.relationship('QuestionTag', secondary=question_tag, backref=db.backref('question', lazy='dynamic'), lazy='dynamic')
	question_links = db.relationship('QuestionLink', backref='question', cascade="all,delete")
	answer_links = db.relationship('AnswerLink', backref='question', cascade="all,delete")

	shows = db.relationship('Show', secondary=show_question, backref=db.backref('question', lazy='dynamic'), lazy='dynamic' )


	answers_static = db.relationship('Answer', secondary=question_answer, viewonly=True, backref=db.backref('question_static'))
	tags_static = db.relationship('QuestionTag', secondary=question_tag, viewonly=True, backref=db.backref('question_static'))

	def __repr__(self):
		return self.text

	#tag
	def add_tag(self, tag):
		if not self.has_tag(tag):
			self.tags.append(tag)

	def remove_tag(self, tag):
		if self.has_tag(tag):
			self.tags.remove(tag)

	def has_tag(self, tag):
		return self.tags.filter(QuestionTag.id == tag.id).count() > 0

	#answer
	def add_answer(self, answer):
		if not self.has_answer(answer):
			self.answers.append(answer)

	def remove_answer(self, answer):
		if self.has_answer(answer):
			self.answers.remove(answer)

	def has_answer(self, answer):
		return self.answers.filter(Answer.id == answer.id).first()

	#show
	def add_show(self, show):
		if not self.has_show(show):
			self.shows.append(show)

	def remove_show(self, show):
		if self.has_show(show):
			self.shows.remove(show)

	def has_show(self, show):
		return self.shows.filter_by(id = show.id).first()



class QuestionTag(db.Model, QuestionTagMultiCRUD):
	__tablename__ = 'QuestionTag'
	id = db.Column(db.Integer, primary_key=True)
	type = db.Column(db.Integer)
	name = db.Column(db.String(2000))

	_type_enum = {
		1: 'category'
	}

	search_cols = ["name"]

	def __repr__(self):
		return self.name

class QuestionLink(db.Model):
	__tablename__ = 'QuestionLink'
	id = db.Column(db.Integer, primary_key=True)
	question_id = db.Column(db.Integer, db.ForeignKey('Question.id'))
	type = db.Column(db.Integer)
	url = db.Column(db.String(2000))

	_type_enum = {
		1: 'picture',
		2: 'video'
	}

	def __repr__(self):
		return "<QuestionLink {} ({})> - {}".format(self.id, self._type_enum[self.type], self.url)

"""
ANSWERS
"""
# class Answer(db.Model):
# 	__tablename__ = 'Answer'
# 	id = db.Column(db.Integer, primary_key=True)
# 	question_id = db.Column(db.Integer, db.ForeignKey('Question.id'))
# 	text = db.Column(db.String(2000))

# 	def __repr__(self):
# 		return self.text


class Answer(db.Model, AnswerMultiCRUD):
	__tablename__ = 'Answer'

	id = db.Column(db.Integer, primary_key=True)
	parent_id = db.Column(db.Integer, db.ForeignKey('Answer.id'))
	text = db.Column(db.String(2000)) 

	children = db.relationship('Answer', backref = db.backref('parent',remote_side = id), cascade="all,delete")

	def __repr__(self):
		# if self.parent_id:
		# 	return "{} - child".format(self.text)
		# else:
		return self.text


		if self.parent_id:
			return "<Answer {} ({})> {}".format(self.id, self.text, self.parent.text)
		return "<Answer {} ({})>".format(self.id, self.text)


class AnswerLink(db.Model):
	__tablename__ = 'AnswerLink'
	id = db.Column(db.Integer, primary_key=True)
	question_id = db.Column(db.Integer, db.ForeignKey('Question.id'))
	type = db.Column(db.Integer)
	url = db.Column(db.String(2000))

	_type_enum = {
		1: 'picture',
		2: 'video'
	}

	def __repr__(self):
		return "<AnswerLink {} ({})> - {}".format(self.id, self._type_enum[self.type], self.url)
