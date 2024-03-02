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

	created_utc = Column(Integer, primary_key=True)
	type = Column(String)
	data = Column(String)
	title = Column(String)
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

	@property
	@lazy
	def seconds_since_starts(self):
		return int(time.time() - self.start_utc)

def get_running_orgy(v):
	if not (v and v.allowed_in_chat): return None

	refresh = False

	ended_orgies = g.db.query(Orgy).filter(Orgy.end_utc != None, Orgy.end_utc < time.time()).all()
	for orgy in ended_orgies:
		if orgy.started:
			refresh = True
		g.db.delete(orgy)

	orgy = g.db.query(Orgy).filter(Orgy.start_utc < time.time()).order_by(Orgy.start_utc).first()
	if orgy and not orgy.started:
		orgy.started = True
		g.db.add(orgy)
		refresh = True

	if refresh:
		requests.post('http://localhost:5001/refresh_chat', headers={"Host": SITE})

	return orgy
