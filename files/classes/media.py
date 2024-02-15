import time

from sqlalchemy.orm import Mapped
from sqlalchemy.sql.sqltypes import *
from files.classes import Base
from files.helpers.types import str_pk, user_id_fk

class Media(Base):
	__tablename__ = "media"
	kind: Mapped[str_pk]
	filename: Mapped[str_pk]
	user_id: Mapped[user_id_fk]
	created_utc: Mapped[int]
	size: Mapped[int]

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(kind={self.kind}, filename={self.filename})>"
