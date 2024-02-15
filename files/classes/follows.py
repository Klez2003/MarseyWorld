import time
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.types import user_id_fk_pk

if TYPE_CHECKING:
	from files.classes import User


class Follow(Base):
	__tablename__ = "follows"
	target_id: Mapped[user_id_fk_pk]
	user_id: Mapped[user_id_fk_pk]
	created_utc: Mapped[int]

	user: Mapped["User"] = relationship(uselist=False, primaryjoin="User.id==Follow.user_id", back_populates="following")
	target: Mapped["User"] = relationship(uselist=False, primaryjoin="User.id==Follow.target_id", back_populates="followers")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"
