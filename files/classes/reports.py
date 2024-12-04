import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.lazy import lazy
from files.helpers.slurs_and_profanities import censor_slurs_profanities

class Report(Base):
	__tablename__ = "reports"

	post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	reason = Column(String)
	created_utc = Column(Integer)

	user = relationship("User", primaryjoin="Report.user_id == User.id", uselist=False)
	post = relationship("Post", uselist=False)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, post_id={self.post_id})>"

	@lazy
	def realreason(self, v):
		return censor_slurs_profanities(self.reason, v)

	#lazy hack to avoid having to rename the comment_id column and causing potential new bugs
	@property
	@lazy
	def parent_id(self):
		return self.post_id


class CommentReport(Base):
	__tablename__ = "commentreports"

	comment_id = Column(Integer, ForeignKey("comments.id"), primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	reason = Column(String)
	created_utc = Column(Integer)

	user = relationship("User", primaryjoin="CommentReport.user_id == User.id", uselist=False)
	comment = relationship("Comment", uselist=False)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, comment_id={self.comment_id})>"

	@lazy
	def realreason(self, v):
		return censor_slurs_profanities(self.reason, v)

	#lazy hack to avoid having to rename the comment_id column and causing potential new bugs
	@property
	@lazy
	def parent_id(self):
		return self.comment_id
