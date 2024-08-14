import time

from sqlalchemy import Column
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer

from files.classes import Base
from files.helpers.lazy import lazy
from files.helpers.config.const import *

from .group_membership import *

class Group(Base):
	__tablename__ = "groups"
	name = Column(String, primary_key=True)
	created_utc = Column(Integer)
	owner_id = Column(Integer, ForeignKey("users.id"))
	description = Column(String)
	description_html = Column(String)

	memberships = relationship("GroupMembership", primaryjoin="GroupMembership.group_name==Group.name", order_by="GroupMembership.approved_utc")
	owner = relationship("User", primaryjoin="Group.owner_id==User.id")

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
		return {x.user_id for x in self.memberships if x.approved_utc}

	@property
	@lazy
	def applied_ids(self):
		return [x.user_id for x in self.memberships if not x.approved_utc]

	@property
	@lazy
	def permalink(self):
		return f"{SITE_FULL}/!{self.name}"
