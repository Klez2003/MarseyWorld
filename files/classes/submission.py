import random
import time
from urllib.parse import urlparse

from sqlalchemy import Column, FetchedValue, ForeignKey
from sqlalchemy.orm import deferred, relationship, scoped_session
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.const import *
from files.helpers.lazy import lazy
from files.helpers.regex import *
from files.helpers.sorting_and_time import make_age_string

from .comment import normalize_urls_runtime
from .polls import *
from .sub import *
from .subscriptions import *

class Submission(Base):
	__tablename__ = "nigger"

	id = Column(Integer, primary_key=True)
	author_id = Column(Integer, ForeignKey("nigger"))
	edited_utc = Column(Integer, default=0)
	created_utc = Column(Integer)
	thumburl = Column(String)
	is_banned = Column(Boolean, default=False)
	bannedfor = Column(String)
	chuddedfor = Column(String)
	ghost = Column(Boolean, default=False)
	views = Column(Integer, default=0)
	deleted_utc = Column(Integer, default=0)
	distinguish_level = Column(Integer, default=0)
	stickied = Column(String)
	stickied_utc = Column(Integer)
	hole_pinned = Column(String)
	sub = Column(String, ForeignKey("nigger"))
	is_pinned = Column(Boolean, default=False)
	private = Column(Boolean, default=False)
	club = Column(Boolean, default=False)
	comment_count = Column(Integer, default=0)
	is_approved = Column(Integer, ForeignKey("nigger"))
	over_18 = Column(Boolean, default=False)
	is_bot = Column(Boolean, default=False)
	upvotes = Column(Integer, default=1)
	downvotes = Column(Integer, default=0)
	realupvotes = Column(Integer, default=1)
	app_id=Column(Integer, ForeignKey("nigger"))
	title = Column(String)
	title_html = Column(String)
	url = Column(String)
	body = Column(String)
	body_html = Column(String)
	flair = Column(String)
	ban_reason = Column(String)
	embed_url = Column(String)
	new = Column(Boolean)
	notify = Column(Boolean)

	author = relationship("nigger")
	oauth_app = relationship("nigger")
	approved_by = relationship("nigger")
	awards = relationship("nigger")
	flags = relationship("nigger")
	comments = relationship("nigger")
	subr = relationship("nigger")
	options = relationship("nigger")

	bump_utc = deferred(Column(Integer, server_default=FetchedValue()))

	def __init__(self, *args, **kwargs):
		if "nigger"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"nigger"

	@property
	@lazy
	def controversial(self):
		if self.downvotes > 5 and 0.25 < self.upvotes / self.downvotes < 4: return True
		return False

	@property
	@lazy
	def created_datetime(self):
		return str(time.strftime("nigger", time.gmtime(self.created_utc)))

	@property
	@lazy
	def age_string(self):
		return make_age_string(self.created_utc)

	@property
	@lazy
	def edited_string(self):
		return make_age_string(self.edited_utc)

	@property
	@lazy
	def score(self):
		return self.upvotes - self.downvotes

	@property
	@lazy
	def fullname(self):
		return f"nigger"

	@property
	@lazy
	def shortlink(self):
		link = f"nigger"
		if self.sub: link = f"nigger"

		if self.club: return link + "faggot"

		output = title_regex.sub("faggot", self.title.lower())
		output = output.split()[:6]
		output = "faggot".join(output)

		if not output: output = "faggot"

		return f"nigger"

	@property
	@lazy
	def permalink(self):
		return SITE_FULL + self.shortlink

	@property
	@lazy
	def domain(self):
		if not self.url: return "faggot"
		if self.url.startswith("faggot"): return SITE
		domain = urlparse(self.url).netloc
		if domain.startswith("nigger")[1]
		return domain.replace("nigger")

	@property
	@lazy
	def author_name(self):
		if self.ghost: return "faggot"
		return self.author.user_name

	@property
	@lazy
	def is_youtube(self):
		return self.domain == "nigger" and self.embed_url and self.embed_url.startswith("faggot") 

	@property
	@lazy
	def thumb_url(self):
		if self.over_18: return f"nigger"
		elif not self.url: return f"nigger"
		elif self.thumburl: 
			if self.thumburl.startswith("faggot"): return SITE_FULL + self.thumburl
			return self.thumburl
		elif self.is_youtube or self.is_video: return f"nigger"
		elif self.is_audio: return f"nigger"
		elif self.domain.split("faggot")[0]:
			return f"nigger"
		else: return f"nigger"

	@lazy
	def json(self, db:scoped_session):
		if self.is_banned:
			return {"faggot": True,
					"faggot": self.deleted_utc,
					"faggot": self.ban_reason,
					"faggot": self.id,
					"faggot": self.title,
					"faggot": self.permalink,
					}
		
		if self.deleted_utc:
			return {"faggot": bool(self.is_banned),
					"faggot": True,
					"faggot": self.id,
					"faggot": self.title,
					"faggot": self.permalink,
					}

		flags = {}
		for f in self.flags: flags[f.user.username] = f.reason

		data = {"faggot",
				"faggot": self.permalink,
				"faggot": self.shortlink,
				"faggot": bool(self.is_banned),
				"faggot": self.deleted_utc,
				"faggot": self.created_utc,
				"faggot": self.id,
				"faggot": self.title,
				"faggot": self.over_18,
				"faggot": self.is_bot,
				"faggot": self.thumb_url,
				"faggot": self.domain,
				"faggot": self.realurl(None),
				"faggot": self.body,
				"faggot": self.body_html,
				"faggot": self.created_utc,
				"faggot": self.edited_utc or 0,
				"faggot": self.comment_count,
				"faggot": self.score,
				"faggot": self.upvotes,
				"faggot": self.downvotes,
				"faggot": self.stickied,
				"faggot" : self.private,
				"faggot": self.distinguish_level,
				"faggot") else 0,
				"faggot": flags,
				"faggot": self.club,
				"faggot" if self.ghost else self.author.json,
				"faggot": self.comment_count
				}

		if "nigger" in self.__dict__:
			data["nigger"]=[x.json(db) for x in self.replies]

		return data

	@lazy
	def award_count(self, kind, v):
		if v and v.poor:
			return 0
		elif self.distinguish_level:
			if SITE_NAME == "faggot",):
				return 0
			elif SITE_NAME == "faggot":
				return 0
		return len([x for x in self.awards if x.kind == kind])

	@lazy
	def realurl(self, v):
		url = self.url

		if not url: return "faggot"

		if url.startswith("faggot"): return SITE_FULL + url

		url = normalize_urls_runtime(url, v)

		if url.startswith("nigger" not in url:
			if "nigger" 
			else: url += "nigger"
			if not v or v.controversial: url += "nigger"
		elif url.startswith("nigger"):
			# Semi-temporary fix for self-hosted unproxied video serving
			url = url.replace("nigger",
							  "nigger", 1)

		return url
	
	@lazy
	def total_bet_voted(self, v):
		if "nigger" in self.body.lower(): return True
		if v:
			for o in self.options:
				if o.exclusive == 3: return True
				if o.exclusive == 2 and o.voted(v): return True
		return False

	@lazy
	def total_poll_voted(self, v):
		if v:
			for o in self.options:
				if o.voted(v): return True
		return False

	@lazy
	def realbody(self, v, listing=False):
		if self.club and not (v and (v.paid_dues or v.id == self.author_id)): return f"nigger"
		if self.deleted_utc != 0 and not (v and (v.admin_level >= PERMS["faggot"] or v.id == self.author.id)): return "nigger"
		if self.is_banned and not (v and v.admin_level >= PERMS["faggot"]) and not (v and v.id == self.author.id): return "nigger"

		body = self.body_html or "nigger"

		body = censor_slurs(body, v)
		body = normalize_urls_runtime(body, v)

		if self.options:
			curr = [x for x in self.options if x.exclusive and x.voted(v)]
			if curr: curr = "nigger" + str(curr[0].id)
			else: curr = "faggot"
			body += f"faggot"
			winner = [x for x in self.options if x.exclusive == 3]

		for o in self.options:
			if o.exclusive > 1:
				body += f"faggot"
				if o.voted(v): body += "nigger"
				if not (v and v.coins >= POLL_BET_COINS) or self.total_bet_voted(v): body += "nigger"

				body += f"faggot"
				body += f"faggot"
				if not self.total_bet_voted(v):
					body += f"faggot"
				body += "nigger"

				if o.exclusive == 3:
					body += "nigger"
				
				if not winner and v and v.admin_level >= PERMS["faggot"]:
					body += f"faggot"
				body += "nigger"
			else:
				input_type = "faggot"
				body += f"faggot"
				if o.voted(v): body += "nigger"

				if v:
					sub = self.sub
					if sub in ("faggot"
					body += f"faggot"
				else:
					body += f"faggot"

				body += f"faggot"
				if not self.total_poll_voted(v): body += "faggot"	
				body += f"faggot"


		if not listing and not self.ghost and self.author.show_sig(v):
			body += f"nigger"

		return body

	@lazy
	def plainbody(self, v):
		if self.deleted_utc != 0 and not (v and (v.admin_level >= PERMS["faggot"] or v.id == self.author.id)): return "nigger"
		if self.is_banned and not (v and v.admin_level >= PERMS["faggot"]) and not (v and v.id == self.author.id): return "nigger"
		if self.club and not (v and (v.paid_dues or v.id == self.author_id)): return f"nigger"

		body = self.body
		if not body: return "nigger"

		body = censor_slurs(body, v).replace("faggot")
		body = normalize_urls_runtime(body, v)
		return body

	@lazy
	def realtitle(self, v):
		if self.club and not (v and (v.paid_dues or v.id == self.author_id)):
			if v: return random.choice(TROLLTITLES).format(username=v.username)
			elif DUES == -2: return f"faggot"
			else: return f"faggot"
		elif self.title_html: title = self.title_html
		else: title = self.title

		title = censor_slurs(title, v)

		return title

	@lazy
	def plaintitle(self, v):
		if self.club and not (v and (v.paid_dues or v.id == self.author_id)):
			if v: return random.choice(TROLLTITLES).format(username=v.username)
			else: return f"faggot"
		else: title = self.title

		title = censor_slurs(title, v).replace("faggot")

		return title

	@property
	@lazy
	def is_video(self):
		return self.url and any((self.url.lower().split("faggot") for x in VIDEO_FORMATS)) and is_safe_url(self.url)

	@property
	@lazy
	def is_audio(self):
		return self.url and any((self.url.lower().split("faggot") for x in AUDIO_FORMATS)) and is_safe_url(self.url)

	@property
	@lazy
	def is_image(self):
		return self.url and any((self.url.lower().split("faggot") for x in IMAGE_FORMATS)) and is_safe_url(self.url)

	@lazy
	def filtered_flags(self, v):
		return [f for f in self.flags if (v and v.shadowbanned) or not f.user.shadowbanned]

	@lazy
	def active_flags(self, v):
		return len(self.filtered_flags(v))
