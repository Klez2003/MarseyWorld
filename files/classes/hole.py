import random
import time

from sqlalchemy import Column
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship, deferred
from sqlalchemy.types import *
from sqlalchemy.dialects.postgresql import ARRAY

from files.classes import Base
from files.helpers.lazy import lazy
from files.helpers.config.const import *

from .hole_relationship import *

class Hole(Base):
	__tablename__ = "holes"
	name = Column(String, primary_key=True)
	sidebar = deferred(Column(String))
	sidebar_html = deferred(Column(String))
	sidebarurls = Column(MutableList.as_mutable(ARRAY(String)), default=MutableList([]))
	bannerurls = Column(MutableList.as_mutable(ARRAY(String)), default=MutableList([]))
	marseyurl = Column(String)
	css = deferred(Column(String))
	stealth = Column(Boolean, default=False)
	public_use = Column(Boolean, default=False)
	created_utc = Column(Integer)
	dead_utc = Column(Integer)

	if SITE_NAME == 'WPD' and not IS_LOCALHOST:
		snappy_quotes = None
	else:
		snappy_quotes = deferred(Column(String))

	blocks = relationship("HoleBlock", primaryjoin="HoleBlock.hole==Hole.name")
	followers = relationship("HoleFollow", primaryjoin="HoleFollow.hole==Hole.name")
	stealth_hole_unblocks = relationship("StealthHoleUnblock", lazy="dynamic", primaryjoin="StealthHoleUnblock.hole==Hole.name")

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
		return f'{SITE_FULL_IMAGES}/i/{SITE_NAME}/headericon.webp?x=16'

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
