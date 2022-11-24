import time

from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class BannedDomain(Base):
	__tablename__ = "nigger"
	domain = Column(String, primary_key=True)
	reason = Column(String)
	created_utc = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "nigger"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"nigger"
