import time
from typing import Optional, TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

from files.classes import Base
from files.helpers.lazy import lazy
from files.helpers.config.const import *
from files.helpers.types import str_pk, user_id_fk

from .group_membership import *

if TYPE_CHECKING:
	from files.classes import User


class Group(Base):
	__tablename__ = "groups"
	name: Mapped[str_pk]
	created_utc: Mapped[int]
	owner_id: Mapped[Optional[user_id_fk]]
	description: Mapped[Optional[str]]
	description_html: Mapped[Optional[str]]

	memberships: Mapped[list["GroupMembership"]] = relationship(primaryjoin="GroupMembership.group_name==Group.name", order_by="GroupMembership.approved_utc")
	owner: Mapped["User"] = relationship(primaryjoin="Group.owner_id==User.id")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return self.name

	@property
	@lazy
	def membership_user_ids(self):
		return [x.user_id for x in self.memberships]

	@property
	@lazy
	def member_ids(self):
		return set(x.user_id for x in self.memberships if x.approved_utc)

	@property
	@lazy
	def applied_ids(self):
		return [x.user_id for x in self.memberships if not x.approved_utc]
