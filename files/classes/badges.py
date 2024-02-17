import time
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.config.const import *
from files.helpers.lazy import lazy

if TYPE_CHECKING:
	from files.classes import User


class BadgeDef(Base):
	__tablename__ = "badge_defs"

	id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
	name: Mapped[str]
	description: Mapped[str]
	created_utc: Mapped[int]

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def path(self):
		return f"{SITE_FULL_IMAGES}/i/{SITE_NAME}/badges/{self.id}.webp?b=11"

class Badge(Base):

	__tablename__ = "badges"

	user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
	badge_id: Mapped[int] = mapped_column(ForeignKey('badge_defs.id'), primary_key=True)
	description: Mapped[str]
	url: Mapped[str]
	created_utc: Mapped[int]

	user: Mapped["User"] = relationship(back_populates="badges")
	badge: Mapped["BadgeDef"] = relationship(primaryjoin="Badge.badge_id == BadgeDef.id", lazy="joined", innerjoin=True)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs:
			kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, badge_id={self.badge_id})>"

	@property
	@lazy
	def until(self):
		if self.badge_id == 58 and self.user.chud != 1: return self.user.chud
		if self.badge_id == 94 and self.user.progressivestack != 1: return self.user.progressivestack
		if self.badge_id == 170 and self.user.marsify != 1: return self.user.marsify
		if self.badge_id == 179 and self.user.spider != 1: return self.user.spider

		if self.badge_id == 95: return self.user.bird
		if self.badge_id == 96: return self.user.flairchanged
		if self.badge_id == 97: return self.user.longpost
		if self.badge_id == 98: return self.user.hieroglyphs
		if self.badge_id == 109: return self.user.rehab
		if self.badge_id == 167: return self.user.owoify
		if self.badge_id == 168: return self.user.bite
		if self.badge_id == 169: return self.user.earlylife
		if self.badge_id == 171: return self.user.rainbow
		if self.badge_id == 281: return self.user.namechanged
		if self.badge_id == 285: return self.user.queen
		if self.badge_id == 289: return self.user.sharpen

		return None

	@property
	@lazy
	def text(self):
		if self.until:
			text = self.badge.description + " until"
		elif self.badge_id in {58, 94, 170, 179}:
			text = self.badge.description + " permanently"
		elif self.description:
			text = self.description
		elif self.badge.description:
			text = self.badge.description
		else:
			return self.name

		return f'{self.name} - {text}'

	@property
	@lazy
	def name(self):
		return self.badge.name

	@property
	@lazy
	def path(self):
		return self.badge.path

	@property
	@lazy
	def json(self):
		return {'text': self.text,
				'name': self.name,
				'url': self.url,
				'icon_url':self.path
				}
