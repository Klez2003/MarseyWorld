import random
import time
import typing
from urllib.parse import urlparse

from sqlalchemy import Column, FetchedValue, ForeignKey
from sqlalchemy.orm import deferred, relationship, scoped_session
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
if typing.TYPE_CHECKING:
	from files.classes.user import User
from files.helpers.const import *
from files.helpers.lazy import lazy
from files.helpers.regex import *
from files.helpers.sorting_and_time import make_age_string

from .comment import normalize_urls_runtime
from .polls import *
from .sub import *
from .subscriptions import *

class ArchivedSubmission(Base):
	__tablename__ = "archived_submissions"

	id = Column(Integer, primary_key=True)
	author_id = Column(Integer)
	author_name = Column(String)
	created_utc = Column(Integer, nullable=False)
	edited_utc = Column(Integer, default=0, nullable=False)
	thumburl = Column(String)
	distinguish_level = Column(Integer, default=0)
	sub = Column(String, nullable=False)
	comment_count = Column(Integer, default=0, nullable=False)
	over_18 = Column(Boolean, default=False, nullable=False)
	score = Column(Integer, default=1, nullable=False)
	upvotes = Column(Integer, default=1)
	downvotes = Column(Integer, default=0)
	title = Column(String)
	url = Column(String)
	body = Column(String)
	body_html = Column(String)
	flair = Column(String)

	hidden_by = Column(Integer, ForeignKey("users.id")) # null if not hidden

	author = relationship("User", primaryjoin="ArchivedSubmission.author_id==User.id")
	flags = relationship("Flag", order_by="Flag.created_utc")
	comments = relationship("ArchivedComment", primaryjoin="ArchivedComment.parent_submission==ArchivedSubmission.id", back_populates="post")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<ArchivedSubmission(id={self.id})>"

	@property
	@lazy
	def created_datetime(self):
		return str(time.strftime("%d/%B/%Y %H:%M:%S UTC", time.gmtime(self.created_utc)))

	@property
	@lazy
	def age_string(self):
		return make_age_string(self.created_utc)

	@property
	@lazy
	def edited_string(self):
		return make_age_string(self.edited_utc)

	@lazy
	def realbody(self, v:Optional["User"]):
		if self.hidden_by and not v.admin_level >= PERMS['POST_COMMENT_MODERATION']: return "[removed]" # TODO: use v.can_see_content??
		body = self.body_html or ""
		if not body: return ""
		body = censor_slurs(body, v)
		body = normalize_urls_runtime(body, v)
		return body

	def plainbody(self, v:Optional["User"]):
		if self.hidden_by and not v.admin_level >= PERMS['POST_COMMENT_MODERATION']: return "[removed]" # TODO: use v.can_see_content??
		body = self.body or ""
		if not body: return ""
		body = censor_slurs(body, v)
		body = normalize_urls_runtime(body, v)
		return body

	@lazy
	def realtitle(self, v:Optional["User"]):
		if self.hidden_by and not v.admin_level >= PERMS['POST_COMMENT_MODERATION']: return "[removed]" # TODO: use v.can_see_content??
		return censor_slurs(self.title, v)

	
