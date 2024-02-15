import time

from sqlalchemy.orm import Mapped
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.types import str_pk, user_id_fk_pk

class PushSubscription(Base):
	__tablename__ = "push_subscriptions"
	user_id: Mapped[user_id_fk_pk]
	subscription_json: Mapped[str_pk]
	created_utc: Mapped[int]

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"
