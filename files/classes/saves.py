import time
from typing import Optional, TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.types import comment_id_fk_pk, post_id_fk_pk, user_id_fk_pk

if TYPE_CHECKING:
	from files.classes.comment import Comment
	from files.classes.post import Post


class SaveRelationship(Base):
	__tablename__ = "save_relationship"

	user_id: Mapped[user_id_fk_pk]
	post_id: Mapped[post_id_fk_pk]
	created_utc: Mapped[Optional[int]]

	post: Mapped["Post"] = relationship(uselist=False)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, post_id={self.post_id})>"


class CommentSaveRelationship(Base):

	__tablename__ = "comment_save_relationship"

	user_id: Mapped[user_id_fk_pk]
	comment_id: Mapped[comment_id_fk_pk]
	created_utc: Mapped[Optional[int]]

	comment: Mapped["Comment"] = relationship(uselist=False)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, comment_id={self.comment_id})>"
