import time
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.types import comment_id_fk_pk, user_id_fk_pk

if TYPE_CHECKING:
	from files.classes import Comment, User


class Notification(Base):
	__tablename__ = "notifications"

	user_id: Mapped[user_id_fk_pk]
	comment_id: Mapped[comment_id_fk_pk]
	read: Mapped[bool] = mapped_column(default=False)
	created_utc: Mapped[int]

	comment: Mapped["Comment"] = relationship()
	user: Mapped["User"] = relationship()

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, comment_id={self.comment_id})>"
