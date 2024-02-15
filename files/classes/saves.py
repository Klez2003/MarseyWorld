import time
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

if TYPE_CHECKING:
	from files.classes.comment import Comment
	from files.classes.post import Post


class SaveRelationship(Base):
	__tablename__ = "save_relationship"

	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), primary_key=True)
	created_utc: Mapped[int]

	post: Mapped["Post"] = relationship(uselist=False)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, post_id={self.post_id})>"


class CommentSaveRelationship(Base):

	__tablename__ = "comment_save_relationship"

	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"), primary_key=True)
	created_utc: Mapped[int]

	comment: Mapped["Comment"] = relationship(uselist=False)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, comment_id={self.comment_id})>"
