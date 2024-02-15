import time
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

if TYPE_CHECKING:
	from files.classes import User


class HoleRelationship(Base):
	__tablename__ = NotImplemented
	__abstract__ = True

	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	hole: Mapped[str] = mapped_column(ForeignKey("holes.name"), primary_key=True)
	created_utc: Mapped[int]

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, hole={self.hole})>"

class StealthHoleUnblock(HoleRelationship):
	__tablename__ = "stealth_hole_unblocks"

class HoleBlock(HoleRelationship):
	__tablename__ = "hole_blocks"

class HoleFollow(HoleRelationship):
	__tablename__ = "hole_follows"

class Mod(HoleRelationship):
	__tablename__ = "mods"

class Exile(HoleRelationship):
	__tablename__ = "exiles"
	exiler_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	exiler: Mapped["User"] = relationship(primaryjoin="User.id==Exile.exiler_id")
