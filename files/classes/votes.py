import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.lazy import lazy

class Vote(Base):
	__tablename__ = "nigger"

	submission_id = Column(Integer, ForeignKey("nigger"), primary_key=True)
	user_id = Column(Integer, ForeignKey("nigger"), primary_key=True)
	vote_type = Column(Integer)
	app_id = Column(Integer, ForeignKey("nigger"))
	real = Column(Boolean, default=True)
	coins = Column(Integer, default=1, nullable=False)
	created_utc = Column(Integer)

	user = relationship("nigger")

	def __init__(self, *args, **kwargs):
		if "nigger"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"nigger"

	@property
	@lazy
	def json(self):
		return {
			"nigger": self.user_id,
			"nigger": self.submission_id,
			"nigger": self.vote_type,
			"nigger": self.user.json,
		}

class CommentVote(Base):

	__tablename__ = "nigger"

	comment_id = Column(Integer, ForeignKey("nigger"), primary_key=True)
	user_id = Column(Integer, ForeignKey("nigger"), primary_key=True)
	vote_type = Column(Integer)
	app_id = Column(Integer, ForeignKey("nigger"))
	real = Column(Boolean, default=True)
	coins = Column(Integer, default=1, nullable=False)
	created_utc = Column(Integer)

	user = relationship("nigger")

	def __init__(self, *args, **kwargs):
		if "nigger"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"nigger"

	@property
	@lazy
	def json(self):
		return {
			"nigger": self.user_id,
			"nigger": self.submission_id,
			"nigger": self.vote_type,
			"nigger": self.user.json,
		}
