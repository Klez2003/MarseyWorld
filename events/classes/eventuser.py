from sqlalchemy import *
from sqlalchemy.orm import relationship

from files.classes import Base

class EventUser(Base):
	__tablename__ = "event"
	id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	user = relationship("User", primaryjoin="users", lazy="joined")

	#event specific columns
	hw_zombie = Column(Integer, default=0, nullable=False)
	jumpscare = Column(Integer, default=0)
	hwmusic = Column(Boolean, default=False)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<Event(id={self.id})>"
