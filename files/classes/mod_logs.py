import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *
from flask import g
import bleach
from bleach.linkifier import LinkifyFilter
import functools

from files.classes import Base
from files.helpers.config.const import *
from files.helpers.lazy import lazy
from files.helpers.slurs_and_profanities import censor_slurs_profanities
from files.helpers.sorting_and_time import make_age_string
from files.helpers.regex import sanitize_url_regex

def allowed_attributes_notes(tag, name, value):
	if tag == 'a':
		if name == 'href' and '\\' not in value and 'xn--' not in value:
			return True
		if name == 'rel' and value == 'nofollow noopener': return True

	if tag == 'img':
		if name == 'src':
			if '\\' in value: return False
			if value.startswith('/') : return True
			if value.startswith(f'{SITE_FULL_IMAGES}/') : return True
		if name == 'loading' and value == 'lazy': return True
		if name == 'data-bs-toggle' and value == 'tooltip': return True
		if name in {'alt','title'}: return True
	return False

def bleach_log_note(note):
	note = note.replace("\n", "").replace("\r", "").replace("\t", "")

	note = bleach.Cleaner(
		tags=['a','img'],
		attributes=allowed_attributes_notes,
		protocols=['http','https'],
		filters=[
				functools.partial(
					LinkifyFilter,
					skip_tags=["pre","code"],
					parse_email=False, 
					url_re=sanitize_url_regex
				)
			]
	).clean(note)

	note = note.replace('\n','').strip()

	return note

class ModAction(Base):
	__tablename__ = "modactions"
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"))
	kind = Column(String)
	target_user_id = Column(Integer, ForeignKey("users.id"))
	target_post_id = Column(Integer, ForeignKey("posts.id"))
	target_comment_id = Column(Integer, ForeignKey("comments.id"))
	_note = Column(String)
	created_utc = Column(Integer)

	user = relationship("User", primaryjoin="User.id==ModAction.user_id")
	target_user = relationship("User", primaryjoin="User.id==ModAction.target_user_id")
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
		output = MODACTION_KINDS[self.kind]["str"].format(self=self)
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
		return MODACTION_KINDS[self.kind]['icon']

	@property
	@lazy
	def color(self):
		return MODACTION_KINDS[self.kind]['color']

	@property
	@lazy
	def permalink(self):
		return f"{SITE_FULL}/log/{self.id}"

from files.helpers.config.modaction_kinds import MODACTION_KINDS, MODACTION_KINDS_FILTERED
