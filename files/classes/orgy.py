import time
from flask import g, abort

from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class Orgy(Base):
	__tablename__ = "orgies"

	type = Column(String, primary_key=True)
	data = Column(String)
	title = Column(String)
	created_utc = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(type={self.type}, data={self.data} title={self.title})>"

def get_orgy():
	return g.db.query(Orgy).one_or_none()
