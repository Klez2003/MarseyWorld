import time
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Integer, String, Boolean

from files.classes import Base

if TYPE_CHECKING:
	from files.classes.user import User


class GroupMembership(Base):
	__tablename__ = "group_memberships"
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
	group_name: Mapped[str] = mapped_column(ForeignKey("groups.name"), primary_key=True)
	created_utc: Mapped[int]
	approved_utc: Mapped[int]
	is_mod: Mapped[bool] = mapped_column(default=False)

	user: Mapped["User"] = relationship(uselist=False)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, group_name={self.group_name})>"
