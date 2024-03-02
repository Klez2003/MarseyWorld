import time
from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.lazy import lazy
from files.helpers.sorting_and_time import make_age_string

class CurrencyLog(Base):
	__tablename__ = "currency_logs"
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"))
	created_utc = Column(Integer)
	currency = Column(String)
	amount = Column(Integer)
	reason = Column(String)
	balance = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def age_string(self):
		return make_age_string(self.created_utc)
