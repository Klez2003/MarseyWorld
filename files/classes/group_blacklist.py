import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Integer, String, Boolean

from files.classes import Base

class GroupBlacklist(Base):
	__tablename__ = "group_blacklists"
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	group_name = Column(String, ForeignKey("groups.name"), primary_key=True)
	created_utc = Column(Integer)
	blacklister_id = Column(Integer, ForeignKey("users.id"))

	user = relationship("User", primaryjoin="User.id==GroupBlacklist.user_id", uselist=False)
	blacklister = relationship("User", primaryjoin="User.id==GroupBlacklist.blacklister_id", uselist=False)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, group_name={self.group_name})>"
