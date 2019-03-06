from server import db
from .utils.custom_CRUD.show_multicrud import ShowMultiCRUD
from sqlalchemy.ext.associationproxy import association_proxy







class Show(db.Model, ShowMultiCRUD):
	__tablename__ = 'Show'
	# __table_args__ = (
	# 	db.Index(
	# 		'anime_db_id_constraint',  # Index name
	# 		'mal_id', 'anilist_id',  # Columns which are part of the index
	# 	unique=True,
	# 	postgresql_where=('parent_id == 0')),  # The condition
	# )

	id = db.Column(db.Integer, primary_key=True)
	mal_id = db.Column(db.Integer, unique=True, nullable=True)
	anilist_id = db.Column(db.Integer, unique=True, nullable=True)
	parent_id = db.Column(db.Integer, db.ForeignKey('Show.id'))

	titles = db.relationship('ShowTitle', backref='show', cascade="all,delete")

	children = db.relationship('Show', backref = db.backref('parent',remote_side = id))



	# characters = association_proxy('showcharacter', 'character')
	# characters = db.relationship('Character', secondary=show_character, back_populates="shows", lazy='dynamic')

	def __repr__(self):
		if not self.parent_id:
			return "{} - {}".format(self.id, self.titles[0])
		return "{} - {} ({})".format(self.id, self.titles[0], self.parent.titles[0])



class ShowTitle(db.Model):
	__tablename__ = 'ShowTitle'

	id = db.Column(db.Integer, primary_key=True)
	show_id = db.Column(db.Integer, db.ForeignKey('Show.id'))
	parent_id = db.Column(db.Integer, db.ForeignKey('ShowTitle.id'))
	title = db.Column(db.String(2000))

	# title synonyms
	children = db.relationship('ShowTitle', backref = db.backref('parent',remote_side = id, cascade="all,delete"), cascade="all,delete")

	def __repr__(self):
		if not self.parent_id:
			return self.title
		else:
			return "{} - child".format(self.title)


# class Character(db.Model, CharacterMultiCRUD):
# 	__tablename__ = 'Character'
# 	# __table_args__ = (
# 	# 	db.Index(
# 	# 		'char_malid_constraint',  # Index name
# 	# 		'mal_id',  # Columns which are part of the index
# 	# 	unique=True,
# 	# 	postgresql_where=('mal_id >= 1')),  # The condition
# 	# )


# 	id = db.Column(db.Integer, primary_key=True)
# 	mal_id = db.Column(db.Integer, unique=True)
# 	names=db.relationship('CharacterName', backref='character')

# 	shows =  db.relationship('Show', secondary=show_character, back_populates="characters", lazy='dynamic')

# 	def __repr__(self):
# 		if len(self.names) >= 1:
# 			return "<Character {}> - {}".format(self.id, self.names[0].name)
# 		return "<Character {}>".format(self.id)

# 	# character handler
# 	def add_show(self, show):
# 		if not self.has_show(show):
# 			self.shows.append(show)

# 	def remove_show(self, show):
# 		if self.has_show(show):
# 			self.shows.remove(show)

# 	def has_show(self, show):
# 		return self.shows.filter(Show.id == show.id).first()



# class CharacterName(db.Model):
# 	__tablename__ = 'CharacterName'
# 	id = db.Column(db.Integer, primary_key=True)
# 	character_id = db.Column(db.Integer, db.ForeignKey('Character.id'))
# 	name = db.Column(db.String(2000))

# 	def __repr__(self):
# 		return self.name

# show_character = db.Table('show_character',
# 	db.Column('show_id',db.Integer(),db.ForeignKey('Show.id')),
# 	db.Column('character_id',db.Integer(),db.ForeignKey('Character.id')),
# 	db.UniqueConstraint('show_id', 'character_id', name='show_character_constraint')
# )
