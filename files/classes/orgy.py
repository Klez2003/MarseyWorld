import time
from flask import g, abort
import requests
from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.types import int_pk

from files.helpers.lazy import lazy
from files.helpers.config.const import *

class Orgy(Base):
	__tablename__ = "orgies"

	created_utc: Mapped[int_pk]
	type: Mapped[str]
	data: Mapped[str]
	title: Mapped[str]
	start_utc: Mapped[int]
	end_utc: Mapped[Optional[int]]
	started: Mapped[bool] = mapped_column(default=False)

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
