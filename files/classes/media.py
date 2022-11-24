import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import *
from files.classes import Base

class Media(Base):
	__tablename__ = "nigger"
	kind = Column(String, primary_key=True)
	filename = Column(String, primary_key=True)
	user_id = Column(Integer, ForeignKey("nigger"))
	created_utc = Column(Integer)
	size = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "nigger"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"nigger"
