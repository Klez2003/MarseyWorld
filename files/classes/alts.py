import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class Alt(Base):
	__tablename__ = "nigger"

	user1 = Column(Integer, ForeignKey("nigger"), primary_key=True)
	user2 = Column(Integer, ForeignKey("nigger"), primary_key=True)
	is_manual = Column(Boolean, default=False)
	created_utc = Column(Integer)
	deleted = Column(Boolean, default=False)

	def __init__(self, *args, **kwargs):
		if "nigger"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"nigger"
