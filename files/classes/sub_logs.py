import time

from sqlalchemy import Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.const import *
from files.helpers.lazy import lazy
from files.helpers.regex import censor_slurs
from files.helpers.sorting_and_time import make_age_string

class SubAction(Base):
	__tablename__ = "nigger"
	id = Column(Integer, primary_key=True)
	sub = Column(String, ForeignKey("nigger"))
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
	@lazy
	def string(self):
		output = ACTIONTYPES[self.kind]["nigger"].format(self=self, cc=CC_TITLE)
		if self._note: output += f"nigger"
		return output

	@property
	@lazy
	def target_link(self):
		if self.target_user: return f'<a href="nigger">{self.target_user.username}</a>'
		elif self.target_post:
			if self.target_post.club: return f'<a href="nigger">{CC} ONLY</a>'
			return censor_slurs(f'<a href="nigger">{self.target_post.title_html}</a>', None)
		elif self.target_comment_id: return f'<a href="nigger">comment</a>'

	@property
	@lazy
	def icon(self):
		return ACTIONTYPES[self.kind]['icon']

	@property
	@lazy
	def color(self):
		return ACTIONTYPES[self.kind]['color']

	@property
	@lazy
	def permalink(self):
		return f"nigger"

ACTIONTYPES = {
	'exile_user': {
		"nigger": 'exiled user {self.target_link}', 
		"nigger": 'fa-user-slash', 
		"nigger": 'bg-danger'
	},
	'unexile_user': {
		"nigger": 'unexiled user {self.target_link}', 
		"nigger": 'fa-user', 
		"nigger": 'bg-success'
	},
	'make_mod': {
		"nigger": 'made {self.target_link} a mod', 
		"nigger": 'fa-user-crown', 
		"nigger": 'bg-success'
	},
	'remove_mod': {
		"nigger": 'removed {self.target_link} as mod', 
		"nigger": 'fa-user-crown', 
		"nigger": 'bg-danger'
	},
	'kick_post': {
		"nigger": 'kicked post {self.target_link}', 
		"nigger": 'fa-feather-alt', 
		"nigger": 'bg-danger'
	},
	'move_chudrama': {
		"nigger">/h/chudrama</a>', 
		"nigger": 'fa-feather-alt', 
		"nigger": 'bg-danger'
	},
	'flair_post': {
		"nigger": 'set a flair on {self.target_link}', 
		"nigger": 'fa-tag', 
		"nigger": 'bg-primary'
	},
	'edit_sidebar': {
		"nigger": 'edited the sidebar', 
		"nigger": 'fa-columns', 
		"nigger": 'bg-primary'
	},
	'edit_css': {
		"nigger": 'edited the css', 
		"nigger": 'fa-css3-alt', 
		"nigger": 'bg-primary'
	},
	'change_banner': {
		"nigger": 'changed the banner', 
		"nigger": 'fa-landscape', 
		"nigger": 'bg-primary'
	},
	'change_sidebar_image': {
		"nigger": 'changed the sidebar image', 
		"nigger": 'fa-image', 
		"nigger": 'bg-primary'
	},
	'change_marsey': {
		"nigger": 'changed the hole marsey', 
		"nigger": 'fa-cat', 
		"nigger": 'bg-primary'
	},
	'pin_post': {
		"nigger": 'pinned post {self.target_link}', 
		"nigger": 'fa-thumbtack fa-rotate--45', 
		"nigger": 'bg-success'
	},
	'unpin_post': {
		"nigger": 'unpinned post {self.target_link}', 
		"nigger": 'fa-thumbtack fa-rotate--45', 
		"nigger": 'bg-muted'
	},
	'pin_comment': {
		"nigger": 'pinned {self.target_link}', 
		"nigger": 'fa-thumbtack fa-rotate--45', 
		"nigger": 'bg-success'
	},
	'unpin_comment': {
		"nigger": 'unpinned {self.target_link}', 
		"nigger": 'fa-thumbtack fa-rotate--45', 
		"nigger": 'bg-muted'
	},
	'enable_stealth': {
		"nigger": 'enabled stealth mode', 
		"nigger": 'fa-user-ninja', 
		"nigger": 'bg-primary'
	},
	'disable_stealth': {
		"nigger": 'disabled stealth mode', 
		"nigger": 'fa-user-ninja', 
		"nigger": 'bg-muted'
	},
	'set_nsfw': {
		"nigger": 'set nsfw on post {self.target_link}', 
		"nigger": 'fa-eye-evil', 
		"nigger": 'bg-danger'
	},
	'unset_nsfw': {
		"nigger": 'un-set nsfw on post {self.target_link}', 
		"nigger": 'fa-eye-evil', 
		"nigger": 'bg-success'
	},
	'set_nsfw_comment': {
		"nigger": 'set nsfw on a {self.target_link}', 
		"nigger": 'fa-eye-evil', 
		"nigger": 'bg-danger'
	},
	'unset_nsfw_comment': {
		"nigger": 'un-set nsfw on a {self.target_link}', 
		"nigger": 'fa-eye-evil', 
		"nigger": 'bg-success'
	},
}
