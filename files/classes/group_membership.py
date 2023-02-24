import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String

from files.classes import Base

class GroupMembership(Base):
	__tablename__ = "group_memberships"
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	group_name = Column(String, ForeignKey("groups.name"), primary_key=True)
	created_utc = Column(Integer)
	approved_utc = Column(Integer)

	user = relationship("User", uselist=False)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, group={self.group})>"
