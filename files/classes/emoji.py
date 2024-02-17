import time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import *

from files.classes import Base

class Emoji(Base):
	__tablename__ = "emojis"

	name: Mapped[str] = mapped_column(primary_key=True)
	kind: Mapped[str]
	author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	tags: Mapped[str]
	count: Mapped[int] = mapped_column(default=0)
	submitter_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	created_utc: Mapped[int]
	nsfw: Mapped[bool] = mapped_column(default=False)

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
