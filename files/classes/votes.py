import time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.lazy import lazy

class Vote(Base):
	__tablename__ = "votes"

	post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	vote_type: Mapped[int]
	real: Mapped[bool] = mapped_column(default=True)
	coins: Mapped[int] = mapped_column(default=1)
	created_utc: Mapped[int]

	user = relationship("User")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id}, vote_type={self.vote_type})>"

	@property
	@lazy
	def json(self):
		return {
			"user_id": self.user_id,
			"post_id": self.post_id,
			"vote_type": self.vote_type,
			"user": self.user.json,
		}

class CommentVote(Base):

	__tablename__ = "commentvotes"

	comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"), primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	vote_type: Mapped[int]
	real: Mapped[bool] = mapped_column(default=True)
	coins: Mapped[int] = mapped_column(default=1)
	created_utc: Mapped[int]

	user = relationship("User")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id}, vote_type={self.vote_type})>"

	@property
	@lazy
	def json(self):
		return {
			"user_id": self.user_id,
			"post_id": self.post_id,
			"vote_type": self.vote_type,
			"user": self.user.json,
		}
