import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *
from flask import g

from files.classes import Base
from files.classes.mod_logs import bleach_log_note

from files.helpers.config.const import *
from files.helpers.lazy import lazy
from files.helpers.slurs_and_profanities import censor_slurs_profanities
from files.helpers.sorting_and_time import make_age_string

class HoleAction(Base):
	__tablename__ = "hole_actions"
	id = Column(Integer, primary_key=True)
	hole = Column(String, ForeignKey("holes.name"))
	user_id = Column(Integer, ForeignKey("users.id"))
	kind = Column(String)
	target_user_id = Column(Integer, ForeignKey("users.id"))
	target_post_id = Column(Integer, ForeignKey("posts.id"))
	target_comment_id = Column(Integer, ForeignKey("comments.id"))
	_note = Column(String)
	created_utc = Column(Integer)

	user = relationship("User", primaryjoin="User.id==HoleAction.user_id")
	target_user = relationship("User", primaryjoin="User.id==HoleAction.target_user_id")
	target_post = relationship("Post")
	target_comment = relationship("Comment")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs:
			kwargs["created_utc"] = int(time.time())

		if "_note" in kwargs:
			kwargs["_note"] = bleach_log_note(kwargs["_note"])

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
