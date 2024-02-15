import time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *
from flask import g

from files.classes import Base
from files.helpers.lazy import lazy
from files.helpers.slurs_and_profanities import censor_slurs_profanities

class HatDef(Base):
	__tablename__ = "hat_defs"

	id: Mapped[int] = mapped_column(primary_key=True)
	name: Mapped[str]
	description: Mapped[str]
	author_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
	price: Mapped[int]
	submitter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	created_utc: Mapped[int]

	author = relationship("User", primaryjoin="HatDef.author_id == User.id", back_populates="designed_hats")
	submitter = relationship("User", primaryjoin="HatDef.submitter_id == User.id")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def number_sold(self):
		return g.db.query(Hat).filter_by(hat_id=self.id).count()

	@lazy
	def censored_description(self, v):
		return censor_slurs_profanities(self.description, v, True)

	@property
	@lazy
	def is_purchasable(self):
		return self.price > 0


class Hat(Base):
	__tablename__ = "hats"

	user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
	hat_id: Mapped[int] = mapped_column(ForeignKey('hat_defs.id'), primary_key=True)
	equipped: Mapped[bool] = mapped_column(default=False)
	created_utc: Mapped[int]

	hat_def = relationship("HatDef")
	owners = relationship("User", back_populates="owned_hats")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, hat_id={self.hat_id})>"

	@property
	@lazy
	def name(self):
		return self.hat_def.name

	@lazy
	def censored_description(self, v):
		return self.hat_def.censored_description(v)
