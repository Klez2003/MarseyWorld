import time
from typing import Optional, TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.types import user_id_fk_pk

if TYPE_CHECKING:
	from files.classes import User


class UserBlock(Base):
	__tablename__ = "userblocks"
	user_id: Mapped[user_id_fk_pk]
	target_id: Mapped[user_id_fk_pk]
	created_utc: Mapped[Optional[int]]

	user: Mapped["User"] = relationship(primaryjoin="User.id==UserBlock.user_id", back_populates="blocking")
	target: Mapped["User"] = relationship(primaryjoin="User.id==UserBlock.target_id", back_populates="blocked")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user={self.user_id}, target={self.target_id})>"
