import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class PostEdit(Base):
	__tablename__ = "post_edits"
	id = Column(Integer, primary_key=True)
	post_id = Column(Integer, ForeignKey("posts.id"))
	old_body = Column(String)
	old_body_html = Column(String)
	old_title = Column(String)
	old_title_html = Column(String)
	old_url = Column(String)
	created_utc = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

class CommentEdit(Base):
	__tablename__ = "comment_edits"
	id = Column(Integer, primary_key=True)
	comment_id = Column(Integer, ForeignKey("comments.id"))
	old_body = Column(String)
	old_body_html = Column(String)
	created_utc = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"
