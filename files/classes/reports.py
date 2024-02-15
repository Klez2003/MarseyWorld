import time
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.lazy import lazy
from files.helpers.slurs_and_profanities import censor_slurs_profanities

if TYPE_CHECKING:
	from files.classes import User


class Report(Base):
	__tablename__ = "reports"

	post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	reason: Mapped[str]
	created_utc: Mapped[int]

	user: Mapped["User"] = relationship(primaryjoin = "Report.user_id == User.id", uselist = False)

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

	comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"), primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	reason: Mapped[str]
	created_utc: Mapped[int]

	user: Mapped["User"] = relationship(primaryjoin = "CommentReport.user_id == User.id", uselist = False)

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
