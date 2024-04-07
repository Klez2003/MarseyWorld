import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.lazy import lazy
from files.helpers.config.const import *

class Chat(Base):
	__tablename__ = "chats"
	id = Column(Integer, primary_key=True)
	name = Column(String)
	created_utc = Column(Integer)

	memberships = relationship("ChatMembership", order_by="ChatMembership.created_utc")

	@property
	@lazy
	def owner_id(self):
		if not self.memberships:
			return AUTOJANNY_ID
		return self.memberships[0].user_id

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"


class ChatMembership(Base):
	__tablename__ = "chat_memberships"
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	chat_id = Column(Integer, ForeignKey("chats.id"), primary_key=True)
	notification = Column(Boolean, default=False)
	created_utc = Column(Integer)

	user = relationship("User")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, chat_id={self.chat_id})>"


class ChatLeave(Base):
	__tablename__ = "chat_leaves"
	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	chat_id = Column(Integer, ForeignKey("chats.id"), primary_key=True)
	created_utc = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(user_id={self.user_id}, chat_id={self.chat_id})>"


class ChatMessage(Base):
	__tablename__ = "chat_messages"
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("users.id"))
	chat_id = Column(Integer, ForeignKey("chats.id"))
	quotes = Column(Integer, ForeignKey("chat_messages.id"))
	text = Column(String)
	text_censored = Column(String)
	text_html = Column(String)
	text_html_censored = Column(String)
	created_utc = Column(Integer)

	user = relationship("User")
	quoted_message = relationship("ChatMessage", remote_side=[id])

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def username(self):
		return self.user.username

	@property
	@lazy
	def hat(self):
		return self.user.hat_active(None)[0]

	@property
	@lazy
	def namecolor(self):
		return self.user.name_color

	@property
	@lazy
	def patron(self):
		return self.user.patron

	@property
	@lazy
	def pride_username(self):
		return self.user.pride_username(None)
