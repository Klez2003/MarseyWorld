import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.lazy import lazy

class PostOption(Base):
	__tablename__ = "post_options"

	id = Column(Integer, primary_key=True)
	parent_id = Column(Integer, ForeignKey("posts.id"))
	body_html = Column(Text)
	exclusive = Column(Integer)
	created_utc = Column(Integer)

	votes = relationship("PostOptionVote")
	parent = relationship("Post", back_populates="options")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def upvotes(self):
		return len(self.votes)

	@lazy
	def voted(self, v):
		if not v: return False
		return v.id in [x.user_id for x in self.votes]

class PostOptionVote(Base):

	__tablename__ = "post_option_votes"

	option_id = Column(Integer, ForeignKey("post_options.id"), primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	created_utc = Column(Integer)
	post_id = Column(Integer, ForeignKey("posts.id"))

	user = relationship("User")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(option_id={self.option_id}, user_id={self.user_id})>"


class CommentOption(Base):

	__tablename__ = "comment_options"

	id = Column(Integer, primary_key=True)
	parent_id = Column(Integer, ForeignKey("comments.id"))
	body_html = Column(Text)
	exclusive = Column(Integer)
	created_utc = Column(Integer)

	votes = relationship("CommentOptionVote")
	parent = relationship("Comment", back_populates="options")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def upvotes(self):
		return len(self.votes)

	@lazy
	def voted(self, v):
		if not v: return False
		return v.id in [x.user_id for x in self.votes]

class CommentOptionVote(Base):

	__tablename__ = "comment_option_votes"

	option_id = Column(Integer, ForeignKey("comment_options.id"), primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	created_utc = Column(Integer)
	comment_id = Column(Integer, ForeignKey("comments.id"))

	user = relationship("User")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(option_id={self.option_id}, user_id={self.user_id})>"
