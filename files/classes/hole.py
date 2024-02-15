import random
import time
from typing import Annotated, Optional

from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import DynamicMapped, Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import ARRAY

from files.classes import Base
from files.helpers.lazy import lazy
from files.helpers.config.const import *

from .hole_relationship import *

class Hole(Base):
	__tablename__ = "holes"
	name: Mapped[str] = mapped_column(primary_key=True)
	sidebar: Mapped[Optional[str]]
	sidebar_html: Mapped[Optional[str]]
	sidebarurls: Mapped[list[str]] = mapped_column(MutableList.as_mutable(ARRAY(String)), default=MutableList([]))
	bannerurls: Mapped[list[str]] = mapped_column(MutableList.as_mutable(ARRAY(String)), default=MutableList([]))
	marseyurl: Mapped[Optional[str]]
	css: Mapped[Optional[str]] = mapped_column(deferred=True)
	stealth: Mapped[Optional[bool]] = mapped_column(default=False)
	public_use: Mapped[bool] = mapped_column(default=False)
	created_utc: Mapped[Optional[int]]
	if SITE_NAME == 'WPD':
		snappy_quotes = None
	else:
		snappy_quotes: Mapped[Optional[Annotated[str, HOLE_SNAPPY_QUOTES_LENGTH]]] = mapped_column(deferred=True)

	blocks: Mapped[list["HoleBlock"]] = relationship(primaryjoin="HoleBlock.hole==Hole.name")
	followers: Mapped[list["HoleFollow"]] = relationship(primaryjoin="HoleFollow.hole==Hole.name")
	stealth_hole_unblocks: DynamicMapped["StealthHoleUnblock"] = relationship(primaryjoin="StealthHoleUnblock.hole==Hole.name")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return self.name

	@property
	@lazy
	def random_sidebar(self):
		if not self.sidebarurls: return None
		return random.choice(self.sidebarurls)

	@property
	@lazy
	def random_banner(self):
		if not self.bannerurls: return None
		return random.choice(self.bannerurls)

	@property
	@lazy
	def marsey_url(self):
		if self.marseyurl: return self.marseyurl
		return f'{SITE_FULL_IMAGES}/i/{SITE_NAME}/headericon.webp?x=7'

	@property
	@lazy
	def stealth_hole_unblock_num(self):
		return self.stealth_hole_unblocks.count()

	@property
	@lazy
	def block_num(self):
		return len(self.blocks)

	@property
	@lazy
	def follow_num(self):
		return len(self.followers)
