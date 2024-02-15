import time
from typing import Optional, TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.config.awards import AWARDS, HOUSE_AWARDS
from files.helpers.lazy import lazy
from files.helpers.types import comment_id_fk, int_pk, post_id_fk, user_id_fk

if TYPE_CHECKING:
	from files.classes import Comment, Post, User


class AwardRelationship(Base):
	__tablename__ = "award_relationships"

	id: Mapped[int_pk]
	user_id: Mapped[user_id_fk]
	post_id: Mapped[Optional[post_id_fk]]
	comment_id: Mapped[Optional[comment_id_fk]]
	kind: Mapped[str]
	awarded_utc: Mapped[Optional[int]]
	created_utc: Mapped[Optional[int]]
	price_paid: Mapped[int] = mapped_column(default = 0)
	note: Mapped[Optional[str]]

	user: Mapped["User"] = relationship(primaryjoin="AwardRelationship.user_id==User.id", back_populates="awards")
	post: Mapped["Post"] = relationship(primaryjoin="AwardRelationship.post_id==Post.id", back_populates="awards")
	comment: Mapped["Comment"] = relationship(primaryjoin="AwardRelationship.comment_id==Comment.id", back_populates="awards")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def type(self):
		if self.kind in AWARDS: return AWARDS[self.kind]
		elif self.kind in HOUSE_AWARDS: return HOUSE_AWARDS[self.kind]
		else: return AWARDS["fallback"]

	@property
	@lazy
	def title(self):
		return self.type['title']

	@property
	@lazy
	def class_list(self):
		return self.type['icon']+' '+self.type['color']
