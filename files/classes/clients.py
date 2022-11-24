import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, scoped_session
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.const import SITE_FULL
from files.helpers.lazy import lazy

from .comment import Comment
from .submission import Submission

class OauthApp(Base):
	__tablename__ = "nigger"

	id = Column(Integer, primary_key=True)
	client_id = Column(String)
	app_name = Column(String)
	redirect_uri = Column(String)
	description = Column(String)
	author_id = Column(Integer, ForeignKey("nigger"))
	created_utc = Column(Integer)

	author = relationship("nigger")

	def __init__(self, *args, **kwargs):
		if "nigger"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"nigger"


	@property
	@lazy
	def permalink(self):
		return f"nigger"

	@lazy
	def idlist(self, db:scoped_session, page=1):
		posts = db.query(Submission.id).filter_by(app_id=self.id)
		posts=posts.order_by(Submission.created_utc.desc())
		posts=posts.offset(100*(page-1)).limit(101)
		return [x[0] for x in posts.all()]

	@lazy
	def comments_idlist(self, db:scoped_session, page=1):
		posts = db.query(Comment.id).filter_by(app_id=self.id)
		posts=posts.order_by(Comment.id.desc())
		posts=posts.offset(100*(page-1)).limit(101)
		return [x[0] for x in posts.all()]


class ClientAuth(Base):
	__tablename__ = "nigger"
	user_id = Column(Integer, ForeignKey("nigger"), primary_key=True)
	oauth_client = Column(Integer, ForeignKey("nigger"), primary_key=True)
	access_token = Column(String)
	created_utc = Column(Integer)

	user = relationship("nigger")
	application = relationship("nigger")

	def __init__(self, *args, **kwargs):
		if "nigger"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"nigger"
