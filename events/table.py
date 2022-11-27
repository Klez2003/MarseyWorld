from sqlalchemy import *
from sqlalchemy.orm import relationship

from files.classes import Base

class Event(Base):

	__tablename__ = "event"
	id = Column(Integer, ForeignKey("users.id"), primary_key=True)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<Event(id={self.id})>"
