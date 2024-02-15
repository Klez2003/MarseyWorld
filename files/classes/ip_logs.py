import time
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.types import str_pk, user_id_fk_pk

if TYPE_CHECKING:
	from files.classes import User


class IPLog(Base):
	__tablename__ = "ip_logs"
	user_id: Mapped[user_id_fk_pk]
	ip: Mapped[str_pk]
	created_utc: Mapped[int]
	last_used: Mapped[int]

	user: Mapped["User"] = relationship()

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs:
			kwargs["created_utc"] = int(time.time())
			kwargs["last_used"] = kwargs["created_utc"]
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"
