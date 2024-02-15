import time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class IPLog(Base):
	__tablename__ = "ip_logs"
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	ip: Mapped[str] = mapped_column(primary_key=True)
	created_utc: Mapped[int]
	last_used: Mapped[int]

	user = relationship("User")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs:
			kwargs["created_utc"] = int(time.time())
			kwargs["last_used"] = kwargs["created_utc"]
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"
