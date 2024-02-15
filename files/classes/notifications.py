import time
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

if TYPE_CHECKING:
	from files.classes import Comment, User


class Notification(Base):
	__tablename__ = "notifications"

	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"), primary_key=True)
	read: Mapped[bool] = mapped_column(default=False)
	created_utc: Mapped[int]

	comment: Mapped["Comment"] = relationship()
	user: Mapped["User"] = relationship()

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, comment_id={self.comment_id})>"
