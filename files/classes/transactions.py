from typing import Optional

from sqlalchemy.orm import Mapped
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.types import str_pk

class Transaction(Base):
	__tablename__ = "transactions"
	id: Mapped[str_pk]
	created_utc: Mapped[int]
	type: Mapped[str]
	amount: Mapped[int]
	email: Mapped[str]
	claimed: Mapped[Optional[bool]]

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"
