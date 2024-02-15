import time

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.config.awards import AWARDS, HOUSE_AWARDS
from files.helpers.lazy import lazy


class AwardRelationship(Base):
	__tablename__ = "award_relationships"

	id: Mapped[int] = mapped_column(primary_key=True)
	user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
	post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
	comment_id: Mapped[int] = mapped_column(ForeignKey("comments.id"))
	kind: Mapped[str]
	awarded_utc: Mapped[int]
	created_utc: Mapped[int]
	price_paid: Mapped[int] = mapped_column(default = 0)
	note: Mapped[str]

	user = relationship("User", primaryjoin="AwardRelationship.user_id==User.id", back_populates="awards")
	post = relationship("Post", primaryjoin="AwardRelationship.post_id==Post.id", back_populates="awards")
	comment = relationship("Comment", primaryjoin="AwardRelationship.comment_id==Comment.id", back_populates="awards")

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
