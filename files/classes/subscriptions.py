import time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class Subscription(Base):
	__tablename__ = "subscriptions"
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), primary_key=True)
	created_utc: Mapped[int]

	user = relationship("User", uselist=False)
	post = relationship("Post", uselist=False)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"
