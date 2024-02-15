import time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import *
from files.classes import Base

class Media(Base):
	__tablename__ = "media"
	kind: Mapped[str] = mapped_column(primary_key=True)
	filename: Mapped[str] = mapped_column(primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	created_utc: Mapped[int]
	size: Mapped[int]

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(kind={self.kind}, filename={self.filename})>"
