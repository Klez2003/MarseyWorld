import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *
from flask import g

from files.classes import Base
from files.helpers.lazy import lazy

class Note(Base):
	__tablename__ = NotImplemented
	__abstract__ = True

	id = Column(Integer, primary_key=True)
	author_id = Column(Integer, ForeignKey("users.id"))
	body_html = Column(Text)
	created_utc = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

class PostNote(Note):
	__tablename__ = "post_notes"
	parent_id = Column(Integer, ForeignKey("posts.id"))

	author = relationship("User")
	votes = relationship("PostNoteVote")

	@property
	@lazy
	def upvotes(self):
		return g.db.query(PostNoteVote).filter_by(note_id=self.id, vote_type=1).count()

	@property
	@lazy
	def downvotes(self):
		return g.db.query(PostNoteVote).filter_by(note_id=self.id, vote_type=-1).count()

	@lazy
	def voted(self, v):
		if not v: return False
		return g.db.query(PostNoteVote.vote_type).filter_by(note_id=self.id, user_id=v.id).one_or_none()

class CommentNote(Note):
	__tablename__ = "comment_notes"
	parent_id = Column(Integer, ForeignKey("comments.id"))

	author = relationship("User")
	votes = relationship("CommentNoteVote")

	@property
	@lazy
	def upvotes(self):
		return g.db.query(CommentNoteVote).filter_by(note_id=self.id, vote_type=1).count()

	@property
	@lazy
	def downvotes(self):
		return g.db.query(CommentNoteVote).filter_by(note_id=self.id, vote_type=-1).count()

	@lazy
	def voted(self, v):
		if not v: return False
		return g.db.query(CommentNoteVote.vote_type).filter_by(note_id=self.id, user_id=v.id).one_or_none()

class NoteVote(Base):
	__tablename__ = NotImplemented
	__abstract__ = True

	user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
	vote_type = Column(Integer)
	created_utc = Column(Integer)

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs: kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id}, vote_type={self.vote_type})>"

class PostNoteVote(NoteVote):
	__tablename__ = "post_note_votes"
	note_id = Column(Integer, ForeignKey("post_notes.id"), primary_key=True)

class CommentNoteVote(NoteVote):
	__tablename__ = "comment_note_votes"
	note_id = Column(Integer, ForeignKey("comment_notes.id"), primary_key=True)
