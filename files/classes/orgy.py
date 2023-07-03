import time
from math import floor
from random import randint
from urllib.parse import parse_qs, urlencode, urlparse
from flask import g

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship, scoped_session
from sqlalchemy.schema import FetchedValue
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.config.const import *
from files.helpers.lazy import lazy
from files.helpers.regex import *
from files.helpers.sorting_and_time import *

class Orgy(Base):
	__tablename__ = "orgies"

	youtube_id = Column(String, primary_key=True)
	title = Column(String)

	def __init__(self, **kwargs):
		super().__init__(**kwargs)

	
	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.youtube_id}, title={self.title})>"


def get_orgy():
	orgy = g.db.query(Orgy).one_or_none()
	return orgy

def create_orgy(youtube_id, title):
	assert not get_orgy()
	assert re.match(yt_id_regex, youtube_id)
	orgy = Orgy(title=title, youtube_id=youtube_id)
	g.db.add(orgy)
	g.db.flush()
	g.db.commit()

def end_orgy():
	assert get_orgy()
	g.db.query(Orgy).delete()
	g.db.flush()
	g.db.commit()
