import time
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.types import user_id_fk_pk

class Alt(Base):
	__tablename__ = "alts"

	user1: Mapped[user_id_fk_pk]
	user2: Mapped[user_id_fk_pk]
	is_manual: Mapped[bool] = mapped_column(default=False)
	created_utc: Mapped[Optional[int]]

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"
