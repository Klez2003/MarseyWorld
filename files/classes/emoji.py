import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class Emoji(Base):
	__tablename__ = "emojis"

	name = Column(String, primary_key=True)
	kind = Column(String)
	author_id = Column(Integer, ForeignKey("users.id"))
	tags = Column(String)
	count = Column(Integer, default=0)
	submitter_id = Column(Integer, ForeignKey("users.id"))
	created_utc = Column(Integer)
	nsfw = Column(Boolean, default=False)

	author = relationship("User", primaryjoin="User.id==Emoji.author_id")
	submitter = relationship("User", primaryjoin="User.id==Emoji.submitter_id")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(name={self.name})>"

	def tags_list(self):
		return self.tags.split(" ") + [self.name[len("marsey"):]]  # type: ignore

	def json(self):
		data = {
			"name": self.name,
			"author_id": self.author_id,
			"submitter_id": self.submitter_id,
			"tags": self.tags_list(),
			"count": self.count,
			"created_utc": self.created_utc,
			"kind": self.kind,
		}
		if "author_username" in self.__dict__ and self.author_username:
			data["author_username"] = self.author_username
		if "author_original_username" in self.__dict__ and self.author_original_username:
			data["author_original_username"] = self.author_original_username
		if "author_extra_username" in self.__dict__ and self.author_extra_username:
			data["author_extra_username"] = self.author_extra_username
		if "author_prelock_username" in self.__dict__ and self.author_prelock_username:
			data["author_prelock_username"] = self.author_prelock_username
		return data
