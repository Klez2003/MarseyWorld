import time
from typing import Optional, TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *
from flask import g

from files.classes import Base
from files.helpers.lazy import lazy
from files.helpers.slurs_and_profanities import censor_slurs_profanities
from files.helpers.types import int_pk, user_id_fk

if TYPE_CHECKING:
	from files.classes import User


class HatDef(Base):
	__tablename__ = "hat_defs"

	id: Mapped[int_pk]
	name: Mapped[str]
	description: Mapped[str]
	author_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
	price: Mapped[int]
	submitter_id: Mapped[Optional[user_id_fk]]
	created_utc: Mapped[int]

	author: Mapped["User"] = relationship(primaryjoin="HatDef.author_id == User.id", back_populates="designed_hats")
	submitter: Mapped["User"] = relationship(primaryjoin="HatDef.submitter_id == User.id")

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
	equipped: Mapped[Optional[bool]] = mapped_column(default=False)
	created_utc: Mapped[Optional[int]]

	hat_def: Mapped["HatDef"] = relationship()
	owners: Mapped[list["User"]] = relationship(back_populates="owned_hats")

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
