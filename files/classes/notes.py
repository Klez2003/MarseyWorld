import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class Note(Base):
	__tablename__ = NotImplemented
	__abstract__ = True

	id = Column(Integer, primary_key=True)
	author_id = Column(Integer, ForeignKey("users.id"))
	body_html = Column(Text)
	created_utc = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

class PostNote(Note):
	__tablename__ = "post_notes"
	parent_id = Column(Integer, ForeignKey("posts.id"))

	author = relationship("User")

class CommentNote(Note):
	__tablename__ = "comment_notes"
	parent_id = Column(Integer, ForeignKey("comments.id"))

	author = relationship("User")