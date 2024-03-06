import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.sql.sqltypes import *
from files.classes import Base
from files.helpers.lazy import lazy

sidebar_hashes = {}
banner_hashes = {}

class ArtSubmission(Base):
	__tablename__ = "art_submissions"
	id = Column(Integer, primary_key=True)
	kind = Column(String)
	author_id = Column(Integer, ForeignKey("users.id"))
	submitter_id = Column(Integer, ForeignKey("users.id"))
	created_utc = Column(Integer)
	approved = Column(Boolean, default=False)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def badge_id_1(self):
		return 99 if self.kind == "sidebar" else 101

	@property
	@lazy
	def badge_id_10(self):
		return 331 if self.kind == "sidebar" else 333

	@property
	@lazy
	def badge_id_100(self):
		return 332 if self.kind == "sidebar" else 334

	@property
	@lazy
	def resize(self):
		return 600 if self.kind == "sidebar" else 1600

	@property
	@lazy
	def location_kind(self):
		return 'sidebar' if self.kind == "sidebar" else 'banners'

	@property
	@lazy
	def formatted_kind(self):
		return 'sidebar image' if self.kind == "sidebar" else 'banner'

	@property
	@lazy
	def msg_kind(self):
		return 'Sidebar image' if self.kind == "sidebar" else 'Banner'

	@property
	@lazy
	def hashes(self):
		return sidebar_hashes if self.kind == "sidebar" else banner_hashes
