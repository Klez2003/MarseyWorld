import time

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class BannedDomain(Base):
	__tablename__ = "banneddomains"
	domain: Mapped[str] = mapped_column(primary_key=True)
	reason: Mapped[str]
	created_utc: Mapped[int]

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(domain={self.domain})>"
