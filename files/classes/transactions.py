from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class Transaction(Base):
	__tablename__ = "transactions"
	id: Mapped[str] = mapped_column(primary_key=True)
	created_utc: Mapped[int]
	type: Mapped[str]
	amount: Mapped[int]
	email: Mapped[str]
	claimed: Mapped[Optional[bool]]

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"
