import time
from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *
from flask import request, has_request_context
from files.classes import Base

class Media(Base):
	__tablename__ = "media"
	filename = Column(String, primary_key=True)
	kind = Column(String)
	user_id = Column(Integer, ForeignKey("users.id"))
	created_utc = Column(Integer)
	size = Column(Integer)
	posterurl = Column(String)
	referrer = Column(String)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs:
			kwargs["created_utc"] = int(time.time())
		if has_request_context():
			kwargs["referrer"] = request.referrer
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(kind={self.kind}, filename={self.filename})>"

class MediaUsage(Base):
	__tablename__ = "media_usages"
	filename = Column(String, ForeignKey("media.filename"), primary_key=True)
	post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
	comment_id = Column(Integer, ForeignKey("comments.id"), primary_key=True)
	created_utc = Column(Integer)
	deleted_utc = Column(Integer)
	removed_utc = Column(Integer)

	media = relationship("Media")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs:
			kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"
