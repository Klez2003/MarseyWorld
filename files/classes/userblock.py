import time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class UserBlock(Base):
	__tablename__ = "userblocks"
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	target_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	created_utc: Mapped[int]

	user = relationship("User", primaryjoin="User.id==UserBlock.user_id", back_populates="blocking")
	target = relationship("User", primaryjoin="User.id==UserBlock.target_id", back_populates="blocked")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user={self.user_id}, target={self.target_id})>"
