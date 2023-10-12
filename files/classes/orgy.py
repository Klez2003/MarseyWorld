import time
from flask import g, abort
import requests

from sqlalchemy import Column, or_
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

from files.helpers.lazy import lazy
from files.helpers.config.const import *

class Orgy(Base):
	__tablename__ = "orgies"

	type = Column(String, primary_key=True)
	data = Column(String)
	title = Column(String)
	created_utc = Column(Integer)
	start_utc = Column(Integer)
	end_utc = Column(Integer)
	started = Column(Boolean, default=False)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(type={self.type}, data={self.data} title={self.title})>"

	@property
	@lazy
	def real_start_utc(self):
		t = self.start_utc
		if int(time.time()) - t > 3000:
			t += 303
		return t

def get_orgy(v):
	if not (v and v.allowed_in_chat): return None

	expired_orgies = g.db.query(Orgy).filter(Orgy.end_utc != None, Orgy.end_utc < time.time()).all()
	for x in expired_orgies:
		g.db.delete(x)

	if expired_orgies:
		requests.post('http://localhost:5001/refresh_chat', headers={"Host": SITE})

	orgy = g.db.query(Orgy).filter(Orgy.start_utc < time.time()).order_by(Orgy.start_utc).first()
	if orgy and not orgy.started:
		orgy.started = True
		g.db.add(orgy)
		requests.post('http://localhost:5001/refresh_chat', headers={"Host": SITE})

	return orgy
