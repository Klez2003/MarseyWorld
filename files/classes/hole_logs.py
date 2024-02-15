import time
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *
from flask import g

from files.classes import Base
from files.helpers.config.const import *
from files.helpers.lazy import lazy
from files.helpers.slurs_and_profanities import censor_slurs_profanities
from files.helpers.sorting_and_time import make_age_string
from files.helpers.types import comment_id_fk, int_pk, post_id_fk, user_id_fk

if TYPE_CHECKING:
	from files.classes import Comment, Post, User


class HoleAction(Base):
	__tablename__ = "hole_actions"
	id: Mapped[int_pk]
	hole: Mapped[str] = mapped_column(ForeignKey("holes.name"))
	user_id: Mapped[Optional[user_id_fk]]
	kind: Mapped[Optional[str]]
	target_user_id: Mapped[Optional[user_id_fk]]
	target_post_id: Mapped[Optional[post_id_fk]]
	target_comment_id: Mapped[Optional[comment_id_fk]]
	_note: Mapped[Optional[str]]
	created_utc: Mapped[int]

	user: Mapped["User"] = relationship(primaryjoin="User.id==HoleAction.user_id")
	target_user: Mapped["User"] = relationship(primaryjoin="User.id==HoleAction.target_user_id")
	target_post: Mapped["Post"] = relationship()
	target_comment: Mapped["Comment"] = relationship()

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def age_string(self):
		return make_age_string(self.created_utc)

	@property
	@lazy
	def string(self):
		output = HOLEACTION_TYPES[self.kind]["str"].format(self=self)
		if self._note: output += f" <i>({self._note})</i>"
		return output

	@property
	@lazy
	def target_link(self):
		if self.target_user_id:
			return f'<a href="{self.target_user.url}">@{self.target_user.username}</a>'
		elif self.target_post_id:
			return censor_slurs_profanities(f'<a href="{self.target_post.permalink}">{self.target_post.title_html}</a>', g.v)
		elif self.target_comment_id:
			return f'<a href="{self.target_comment.permalink}">comment</a>'

	@property
	@lazy
	def icon(self):
		return HOLEACTION_TYPES[self.kind]['icon']

	@property
	@lazy
	def color(self):
		return HOLEACTION_TYPES[self.kind]['color']

	@property
	@lazy
	def permalink(self):
		return f"{SITE_FULL}/h/{self.hole}/log/{self.id}"

from files.helpers.config.holeaction_types import HOLEACTION_TYPES
