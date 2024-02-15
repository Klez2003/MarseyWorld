import time
from typing import Annotated, Optional, TYPE_CHECKING

from flask import g
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, load_only, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.config.const import *
from files.helpers.lazy import lazy
from files.helpers.types import int_pk, user_id_fk, user_id_fk_pk

from .comment import Comment
from .post import Post

if TYPE_CHECKING:
	from files.classes import User


class OauthApp(Base):
	__tablename__ = "oauth_apps"

	id: Mapped[int_pk]
	client_id: Mapped[Optional[Annotated[str, 64]]]
	app_name: Mapped[str]
	redirect_uri: Mapped[str]
	description: Mapped[str]
	author_id: Mapped[user_id_fk]
	created_utc: Mapped[Optional[int]]

	author: Mapped["User"] = relationship(back_populates="apps")

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
		items = g.db.query(cls).options(load_only(cls.id)).filter_by(app_id=self.id)
		total = items.count()

		items = items.order_by(cls.created_utc.desc())
		items = items.offset(100*(page-1)).limit(100)
		items = [x.id for x in items]

		return items, total


class ClientAuth(Base):
	__tablename__ = "client_auths"
	user_id: Mapped[user_id_fk_pk]
	oauth_client: Mapped[int] = mapped_column(ForeignKey("oauth_apps.id"), primary_key=True)
	access_token: Mapped[str]
	created_utc: Mapped[Optional[int]]

	user: Mapped["User"] = relationship()
	application: Mapped["OauthApp"] = relationship()

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<ClientAuth(user_id={self.user_id}, oauth_client={self.oauth_client})>"
