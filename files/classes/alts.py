import time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class Alt(Base):
	__tablename__ = "alts"

	user1: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	user2: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	is_manual: Mapped[bool] = mapped_column(default=False)
	created_utc: Mapped[int]

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"
