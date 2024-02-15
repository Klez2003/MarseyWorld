import time
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.lazy import lazy
from files.helpers.types import comment_id_fk, int_pk, post_id_fk, user_id_fk_pk

if TYPE_CHECKING:
	from files.classes import Comment, Post, User


class PostOption(Base):
	__tablename__ = "post_options"

	id: Mapped[int_pk]
	parent_id: Mapped[post_id_fk]
	body_html: Mapped[str] = mapped_column(Text)
	exclusive: Mapped[int]
	created_utc: Mapped[Optional[int]]

	votes: Mapped[list["PostOptionVote"]] = relationship()
	parent: Mapped["Post"] = relationship(back_populates="options")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def upvotes(self):
		return len(self.votes)

	@lazy
	def voted(self, v):
		if not v: return False
		return v.id in [x.user_id for x in self.votes]

class PostOptionVote(Base):

	__tablename__ = "post_option_votes"

	option_id: Mapped[int] = mapped_column(ForeignKey("post_options.id"), primary_key=True)
	user_id: Mapped[user_id_fk_pk]
	created_utc: Mapped[int]
	post_id: Mapped[Optional[post_id_fk]]

	user: Mapped["User"] = relationship()

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(option_id={self.option_id}, user_id={self.user_id})>"


class CommentOption(Base):

	__tablename__ = "comment_options"

	id: Mapped[int_pk]
	parent_id: Mapped[comment_id_fk]
	body_html: Mapped[str] = mapped_column(Text)
	exclusive: Mapped[int]
	created_utc: Mapped[Optional[int]]

	votes: Mapped[list["CommentOptionVote"]] = relationship()
	parent: Mapped["Comment"] = relationship(back_populates="options")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def upvotes(self):
		return len(self.votes)

	@lazy
	def voted(self, v):
		if not v: return False
		return v.id in [x.user_id for x in self.votes]

class CommentOptionVote(Base):

	__tablename__ = "comment_option_votes"

	option_id: Mapped[int] = mapped_column(ForeignKey("comment_options.id"), primary_key=True)
	user_id: Mapped[user_id_fk_pk]
	created_utc: Mapped[int]
	comment_id: Mapped[Optional[comment_id_fk]]

	user: Mapped["User"] = relationship()

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(option_id={self.option_id}, user_id={self.user_id})>"
