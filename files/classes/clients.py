import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship, scoped_session
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.config.const import *
from files.helpers.lazy import lazy

from .comment import Comment
from .post import Post

class OauthApp(Base):
	__tablename__ = "oauth_apps"

	id = Column(Integer, primary_key=True)
	client_id = Column(String)
	app_name = Column(String)
	redirect_uri = Column(String)
	description = Column(String)
	author_id = Column(Integer, ForeignKey("users.id"))
	created_utc = Column(Integer)

	author = relationship("User", back_populates="apps")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def permalink(self):
		return f"{SITE_FULL}/admin/app/{self.id}"

	@lazy
	def idlist(self, cls, page=1):
		items = db.query(cls).options(load_only(cls.id)).filter_by(app_id=self.id)
		total = items.count()

		items = items.order_by(cls.created_utc.desc())
		items = items.offset(100*(page-1)).limit(100)
		items = [x.id for x in items.all()]

		return items, total


class ClientAuth(Base):
	__tablename__ = "client_auths"
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	oauth_client = Column(Integer, ForeignKey("oauth_apps.id"), primary_key=True)
	access_token = Column(String)
	created_utc = Column(Integer)

	user = relationship("User")
	application = relationship("OauthApp")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<ClientAuth(user_id={self.user_id}, oauth_client={self.oauth_client})>"
