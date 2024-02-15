import time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class PushSubscription(Base):
	__tablename__ = "push_subscriptions"
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	subscription_json: Mapped[str] = mapped_column(primary_key=True)
	created_utc: Mapped[int]

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"
