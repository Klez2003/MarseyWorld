import time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class UserMute(Base):
	__tablename__ = "usermutes"
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	target_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	created_utc: Mapped[int]

	user = relationship("User", primaryjoin="User.id==UserMute.user_id")
	target = relationship("User", primaryjoin="User.id==UserMute.target_id")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user={self.user_id}, target={self.target_id})>"
