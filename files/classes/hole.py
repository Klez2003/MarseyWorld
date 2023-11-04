import random
import time

from sqlalchemy import Column
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import relationship
from sqlalchemy.types import VARCHAR, Boolean, Integer
from sqlalchemy.dialects.postgresql import ARRAY

from files.classes import Base
from files.helpers.lazy import lazy
from files.helpers.config.const import *

from .hole_relationship import *

class Hole(Base):
	__tablename__ = "holes"
	name = Column(VARCHAR(HOLE_NAME_COLUMN_LENGTH), primary_key=True)
	sidebar = Column(VARCHAR(HOLE_SIDEBAR_COLUMN_LENGTH))
	sidebar_html = Column(VARCHAR(HOLE_SIDEBAR_HTML_COLUMN_LENGTH))
	sidebarurl = Column(VARCHAR(HOLE_SIDEBAR_URL_COLUMN_LENGTH))
	bannerurls = Column(MutableList.as_mutable(ARRAY(VARCHAR(HOLE_BANNER_URL_COLUMN_LENGTH))), default=MutableList([]), nullable=False)
	marseyurl = Column(VARCHAR(HOLE_MARSEY_URL_LENGTH))
	css = Column(VARCHAR(HOLE_CSS_COLUMN_LENGTH))
	stealth = Column(Boolean)
	created_utc = Column(Integer)

	blocks = relationship("HoleBlock", primaryjoin="HoleBlock.hole==Hole.name")
	followers = relationship("HoleFollow", primaryjoin="HoleFollow.hole==Hole.name")
	joins = relationship("StealthHoleUnblock", lazy="dynamic", primaryjoin="StealthHoleUnblock.hole==Hole.name")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return self.name

	@property
	@lazy
	def sidebar_url(self):
		if self.sidebarurl: return self.sidebarurl
		return f'{SITE_FULL_IMAGES}/i/{SITE_NAME}/sidebar.webp?x=6'

	@property
	@lazy
	def random_banner(self):
		if not self.bannerurls: return None
		return random.choice(self.bannerurls)

	@property
	@lazy
	def marsey_url(self):
		if self.marseyurl: return self.marseyurl
		return f'{SITE_FULL_IMAGES}/i/{SITE_NAME}/headericon.webp?x=6'

	@property
	@lazy
	def join_num(self):
		return self.joins.count()

	@property
	@lazy
	def block_num(self):
		return len(self.blocks)

	@property
	@lazy
	def follow_num(self):
		return len(self.followers)
