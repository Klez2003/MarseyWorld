import time
from typing import Optional, TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.types import post_id_fk_pk, user_id_fk_pk

if TYPE_CHECKING:
	from files.classes import Post, User


class Subscription(Base):
	__tablename__ = "subscriptions"
	user_id: Mapped[user_id_fk_pk]
	post_id: Mapped[post_id_fk_pk]
	created_utc: Mapped[Optional[int]]

	user: Mapped["User"] = relationship(uselist=False)
	post: Mapped["Post"] = relationship(uselist=False)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"
