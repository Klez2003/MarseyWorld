import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class IPLog(Base):
	__tablename__ = "ip_logs"
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	ip = Column(String, primary_key=True)
	created_utc = Column(Integer)
	last_used = Column(Integer)

	user = relationship("User")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs:
			kwargs["created_utc"] = int(time.time())
			kwargs["last_used"] = kwargs["created_utc"]
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"
