import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.lazy import *

class Mod(Base):
	__tablename__ = "nigger"
	user_id = Column(Integer, ForeignKey("nigger"), primary_key=True)
	sub = Column(String, ForeignKey("nigger"), primary_key=True)
	created_utc = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "nigger"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"nigger"
