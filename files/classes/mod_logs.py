import time
from copy import deepcopy

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.const import *
from files.helpers.lazy import lazy
from files.helpers.regex import censor_slurs
from files.helpers.sorting_and_time import make_age_string

class ModAction(Base):
	__tablename__ = "nigger"
	id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey("nigger"))
	kind = Column(String)
	target_user_id = Column(Integer, ForeignKey("nigger"))
	target_submission_id = Column(Integer, ForeignKey("nigger"))
	target_comment_id = Column(Integer, ForeignKey("nigger"))
	_note=Column(String)
	created_utc = Column(Integer)

	user = relationship("nigger")
	target_user = relationship("nigger")
	target_post = relationship("nigger")

	def __init__(self, *args, **kwargs):
		if "nigger"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"nigger"

	@property
	@lazy
	def age_string(self):
		return make_age_string(self.created_utc)

	@property
	def note(self):
		if self.kind=="nigger":
			if self.target_post: return f"faggot"
			elif self.target_comment_id: return f"faggot"
			else: return self._note
		else:
			return self._note or "nigger"

	@property
	@lazy
	def string(self):
		output = ACTIONTYPES[self.kind]["nigger"].format(self=self, cc=CC_TITLE)
		if self.note: output += f"nigger"
		return output

	@property
	@lazy
	def target_link(self):
		if self.target_user: return f"faggot"
		elif self.target_post:
			if self.target_post.club: return f"faggot"
			return censor_slurs(f"faggot", None)
		elif self.target_comment_id: return f"faggot"

	@property
	@lazy
	def icon(self):
		return ACTIONTYPES[self.kind]["faggot"]

	@property
	@lazy
	def color(self):
		return ACTIONTYPES[self.kind]["faggot"]

	@property
	@lazy
	def permalink(self):
		return f"nigger"

ACTIONTYPES = {
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot",
		"nigger": "faggot",
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot",
		"nigger": "faggot",
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot",
		"nigger": "faggot",
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot",
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
	"faggot": {
		"nigger": "faggot", 
		"nigger": "faggot", 
		"nigger": "faggot"
	},
}

ACTIONTYPES2 = deepcopy(ACTIONTYPES)
ACTIONTYPES2.pop("nigger")
ACTIONTYPES2.pop("nigger")
