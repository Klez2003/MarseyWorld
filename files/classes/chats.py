import time
from flask import g

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.lazy import lazy
from files.helpers.config.const import *
from files.helpers.sorting_and_time import make_age_string

class Chat(Base):
	__tablename__ = "chats"
	id = Column(Integer, primary_key=True)
	name = Column(String)
	created_utc = Column(Integer)
	css = deferred(Column(String))

	@property
	@lazy
	def mod_ids(self):
		return [x[0] for x in g.db.query(ChatMembership.user_id).filter_by(chat_id=self.id, is_mod=True).order_by(ChatMembership.created_utc, ChatMembership.user_id).all()]

	@property
	@lazy
	def owner_id(self):
		return self.mod_ids[0] if self.mod_ids else AUTOJANNY_ID

	@property
	@lazy
	def membership_count(self):
		return g.db.query(ChatMembership).filter_by(chat_id=self.id).count()

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
	muted = Column(Boolean, default=False)
	mentions = Column(Integer, default=0)
	created_utc = Column(Integer)
	is_mod = Column(Boolean, default=False)

	user = relationship("User")

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

	@property
	@lazy
	def permalink(self):
		return f"{SITE_FULL}/chat/{self.chat_id}?m={self.id}#{self.id}"

	@property
	@lazy
	def age_string(self):
		return make_age_string(self.created_utc)
