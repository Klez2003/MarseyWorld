import time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *
from flask import g

from files.classes import Base
from files.helpers.config.const import *
from files.helpers.lazy import lazy
from files.helpers.slurs_and_profanities import censor_slurs_profanities
from files.helpers.sorting_and_time import make_age_string

class ModAction(Base):
	__tablename__ = "modactions"
	id: Mapped[int] = mapped_column(primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	kind: Mapped[str]
	target_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	target_post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
	target_comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"))
	_note: Mapped[str]
	created_utc: Mapped[int]

	user = relationship("User", primaryjoin="User.id==ModAction.user_id")
	target_user = relationship("User", primaryjoin="User.id==ModAction.target_user_id")
	target_post = relationship("Post")
	target_comment = relationship("Comment")

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
	def note(self):
		if self.kind == "ban_user":
			if self.target_post_id:
				return f'for <a href="{self.target_post.permalink}">post</a>'
			elif self.target_comment_id:
				return f'for <a href="{self.target_comment.permalink}">comment</a>'
			else:
				return self._note
		else:
			return self._note or ""

	@property
	@lazy
	def string(self):
		output = MODACTION_TYPES[self.kind]["str"].format(self=self)
		if self.note: output += f" <i>({self.note})</i>"
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
		return MODACTION_TYPES[self.kind]['icon']

	@property
	@lazy
	def color(self):
		return MODACTION_TYPES[self.kind]['color']

	@property
	@lazy
	def permalink(self):
		return f"{SITE_FULL}/log/{self.id}"

from files.helpers.config.modaction_types import MODACTION_TYPES, MODACTION_TYPES_FILTERED
