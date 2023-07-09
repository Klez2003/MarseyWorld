import time
from math import floor
from random import randint
from urllib.parse import parse_qs, urlencode, urlparse
from flask import g

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship
from sqlalchemy.schema import FetchedValue
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.config.const import *
from files.helpers.lazy import lazy
from files.helpers.regex import *
from files.helpers.sorting_and_time import *
from files.helpers.sanitize import normalize_url, get_youtube_id_and_t

class Orgy(Base):
	__tablename__ = "orgies"

	id = Column(Integer, primary_key = True)
	type = Column(Integer, primary_key = True)
	data = Column(String)
	title = Column(String)

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	def is_youtube(self):
		return self.type == OrgyTypes.YOUTUBE
	def is_rumble(self):
		return self.type == OrgyTypes.RUMBLE
	
	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id}, type={self.type}, data={self.data} title={self.title})>"


def get_orgy():
	orgy = g.db.query(Orgy).one_or_none()
	return orgy

def create_orgy(link, title):
	assert not get_orgy()
	normalized_link = normalize_url(link)
	data = None
	orgy_type = -1
	if re.match(bare_youtube_regex, normalized_link):
		orgy_type = OrgyTypes.YOUTUBE
		data, _ = get_youtube_id_and_t(normalized_link)
	elif re.match(rumble_regex, normalized_link):
		orgy_type = OrgyTypes.RUMBLE
		data = normalized_link
	else:
		assert False

	orgy = Orgy(title=title, id=0, type = orgy_type, data = data)
	g.db.add(orgy)
	g.db.flush()
	g.db.commit()

def end_orgy():
	assert get_orgy()
	g.db.query(Orgy).delete()
	g.db.flush()
	g.db.commit()
