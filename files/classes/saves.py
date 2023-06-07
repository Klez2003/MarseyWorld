import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class SaveRelationship(Base):
	__tablename__="save_relationship"

	user_id=Column(Integer, ForeignKey("users.id"), primary_key=True)
	post_id=Column(Integer, ForeignKey("posts.id"), primary_key=True)
	created_utc = Column(Integer)

	post = relationship("Post", uselist=False)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, post_id={self.post_id})>"


class CommentSaveRelationship(Base):

	__tablename__="comment_save_relationship"

	user_id=Column(Integer, ForeignKey("users.id"), primary_key=True)
	comment_id=Column(Integer, ForeignKey("comments.id"), primary_key=True)
	created_utc = Column(Integer)

	comment = relationship("Comment", uselist=False)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, comment_id={self.comment_id})>"
