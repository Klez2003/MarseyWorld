import time
from flask import g, abort

from sqlalchemy import Column, or_
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

from files.helpers.lazy import lazy

class Orgy(Base):
	__tablename__ = "orgies"

	type = Column(String, primary_key=True)
	data = Column(String)
	title = Column(String)
	created_utc = Column(Integer)
	end_utc = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(type={self.type}, data={self.data} title={self.title})>"

	@property
	@lazy
	def real_created_utc(self):
		t = self.created_utc + 10
		if int(time.time()) - t > 3000:
			t += 303
		return t

def get_orgy(v):
	if not (v and v.allowed_in_chat): return None

	orgy = g.db.query(Orgy).one_or_none()
	if not orgy: return False

	if orgy.end_utc and orgy.end_utc < time.time():
		g.db.delete(orgy)
		return False

	return True
