import time
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.lazy import lazy
from files.helpers.types import comment_id_fk_pk, post_id_fk_pk, user_id_fk_pk

if TYPE_CHECKING:
	from files.classes import User


class Vote(Base):
	__tablename__ = "votes"

	post_id: Mapped[post_id_fk_pk]
	user_id: Mapped[user_id_fk_pk]
	vote_type: Mapped[int]
	real: Mapped[bool] = mapped_column(default=True)
	coins: Mapped[int] = mapped_column(default=1)
	created_utc: Mapped[int]

	user: Mapped["User"] = relationship()

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

	comment_id: Mapped[comment_id_fk_pk]
	user_id: Mapped[user_id_fk_pk]
	vote_type: Mapped[int]
	real: Mapped[bool] = mapped_column(default=True)
	coins: Mapped[int] = mapped_column(default=1)
	created_utc: Mapped[int]

	user: Mapped["User"] = relationship()

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
