import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class UserMute(Base):
	__tablename__ = "usermutes"
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	target_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	created_utc = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user={self.user_id}, target={self.target_id})>"
