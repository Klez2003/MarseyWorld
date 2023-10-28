import random
import time
from urllib.parse import urlparse
from flask import g

from sqlalchemy import Column, FetchedValue, ForeignKey
from sqlalchemy.orm import deferred, relationship
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.config.const import *
from files.helpers.config.awards import *
from files.helpers.slurs_and_profanities import *
from files.helpers.lazy import lazy
from files.helpers.regex import *
from files.helpers.sorting_and_time import make_age_string

from .comment import *
from .polls import *
from .hole import *
from .subscriptions import *
from .saves import SaveRelationship

class Post(Base):
	__tablename__ = "posts"

	id = Column(Integer, primary_key=True)
	author_id = Column(Integer, ForeignKey("users.id"))
	edited_utc = Column(Integer, default=0)
	created_utc = Column(Integer)
	thumburl = Column(String)
	posterurl = Column(String)
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
	hole = Column(String, ForeignKey("holes.name"))
	is_pinned = Column(Boolean, default=False)
	private = Column(Boolean, default=False)
	comment_count = Column(Integer, default=0)
	is_approved = Column(Integer, ForeignKey("users.id"))
	nsfw = Column(Boolean, default=False)
	is_bot = Column(Boolean, default=False)
	upvotes = Column(Integer, default=1)
	downvotes = Column(Integer, default=0)
	realupvotes = Column(Integer, default=1)
	app_id = Column(Integer, ForeignKey("oauth_apps.id"))
	title = Column(String)
	title_html = Column(String)
	url = Column(String)
	body = Column(String)
	body_html = Column(String)
	flair = Column(String)
	ban_reason = Column(String)
	embed = Column(String)
	new = Column(Boolean)
	notify = Column(Boolean)
	chudded = Column(Boolean, default=False)
	rainbowed = Column(Boolean, default=False)
	queened = Column(Boolean, default=False)
	sharpened = Column(Boolean, default=False)
	ping_cost = Column(Integer, default=0)
	bump_utc = Column(Integer)

	author = relationship("User", primaryjoin="Post.author_id==User.id")
	oauth_app = relationship("OauthApp")
	approved_by = relationship("User", uselist=False, primaryjoin="Post.is_approved==User.id")
	awards = relationship("AwardRelationship", order_by="AwardRelationship.awarded_utc.desc()", back_populates="post")
	reports = relationship("Report", order_by="Report.created_utc")
	comments = relationship("Comment", primaryjoin="Comment.parent_post==Post.id", back_populates="post")
	hole_obj = relationship("Hole", primaryjoin="foreign(Post.hole)==remote(Hole.name)")
	options = relationship("PostOption", order_by="PostOption.id")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs:
			kwargs["created_utc"] = int(time.time())
		kwargs["bump_utc"] = kwargs["created_utc"]
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def controversial(self):
		if self.downvotes > 5 and 0.25 < self.upvotes / self.downvotes < 4: return True
		return False

	@property
	@lazy
	def created_datetime(self):
		return time.strftime("%d/%B/%Y %H:%M:%S UTC", time.gmtime(self.created_utc))

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
		return f"p_{self.id}"

	@property
	@lazy
	def id_last_num(self):
		return str(self.id)[-1]

	@property
	@lazy
	def shortlink(self):
		link = f"/post/{self.id}"
		if self.hole: link = f"/h/{self.hole}{link}"

		if self.hole and self.hole in {'chudrama', 'countryclub', 'highrollerclub'}:
			output = '-'
		else:
			title = self.plaintitle(None).lower()
			output = title_regex.sub('', title)
			output = output.split()[:6]
			output = '-'.join(output)
			if not output: output = '-'

		return f"{link}/{output}"

	@property
	@lazy
	def permalink(self):
		return SITE_FULL + self.shortlink

	@property
	@lazy
	def domain(self):
		if not self.url: return ''
		if self.url.startswith('/'): return SITE
		domain = urlparse(self.url).netloc
		if domain.startswith("www."): domain = domain.split("www.")[1]
		return domain.replace("old.reddit.com", "reddit.com")

	@property
	@lazy
	def author_name(self):
		if self.ghost and not (hasattr(g, 'v') and g.v and self.id == g.v.id): return '👻'
		return self.author.user_name

	@property
	@lazy
	def is_youtube(self):
		return self.domain == "youtube.com" and self.embed and self.embed.startswith('<lite-youtube')

	@property
	@lazy
	def thumb_url(self):
		if self.nsfw:
			return f"{SITE_FULL_IMAGES}/i/nsfw.webp?x=6"
		elif not self.url:
			return f"{SITE_FULL_IMAGES}/i/{SITE_NAME}/default_text.webp?x=6"
		elif self.thumburl:
			if self.thumburl.startswith('/'): return SITE_FULL + self.thumburl
			return self.thumburl
		elif self.is_youtube or self.is_video:
			return f"{SITE_FULL_IMAGES}/i/default_thumb_video.webp?x=6"
		elif self.is_audio:
			return f"{SITE_FULL_IMAGES}/i/default_thumb_audio.webp?x=6"
		elif self.domain == SITE:
			return f"{SITE_FULL_IMAGES}/i/{SITE_NAME}/site_preview.webp?x=6"
		else:
			return f"{SITE_FULL_IMAGES}/i/default_thumb_link.webp?x=6"

	@property
	@lazy
	def poster_url(self):
		if self.posterurl: return self.posterurl
		if self.thumburl: return self.thumburl
		return None

	@property
	@lazy
	def json(self):
		if self.is_banned:
			return {'is_banned': True,
					'deleted_utc': self.deleted_utc,
					'ban_reason': self.ban_reason,
					'id': self.id,
					'title': self.title,
					'permalink': self.permalink,
					}

		if self.deleted_utc:
			return {'is_banned': bool(self.is_banned),
					'deleted_utc': True,
					'id': self.id,
					'title': self.title,
					'permalink': self.permalink,
					}

		reports = {}
		for r in self.reports:
			reports[r.user.username] = r.reason

		data = {
				'author_id': '👻' if self.ghost else self.author_id,
				'author_name': self.author_name,
				'permalink': self.permalink,
				'shortlink': self.shortlink,
				'is_banned': bool(self.is_banned),
				'deleted_utc': self.deleted_utc,
				'created_utc': self.created_utc,
				'id': self.id,
				'title': self.title,
				'is_nsfw': self.nsfw,
				'is_bot': self.is_bot,
				'thumb_url': self.thumb_url,
				'domain': self.domain,
				'hole': self.hole,
				'url': self.realurl(None),
				'body': self.body,
				'body_html': self.body_html,
				'edited_utc': self.edited_utc or 0,
				'comment_count': self.comment_count,
				'score': self.score,
				'upvotes': self.upvotes,
				'downvotes': self.downvotes,
				'stickied': self.stickied,
				'private' : self.private,
				'distinguish_level': self.distinguish_level,
				'voted': self.voted if hasattr(self, 'voted') else 0,
				'reports': reports,
				}

		if "replies" in self.__dict__:
			data["replies"] = [x.json for x in self.replies]

		return data

	@lazy
	def award_count(self, kind, v):
		if v and v.poor:
			return 0

		if self.distinguish_level and SITE_NAME == 'WPD':
			return 0

		num = len([x for x in self.awards if x.kind == kind])

		if kind in {"shit", "fireflies"}:
			return num

		if kind == "stalker":
			return min(num, 25)

		if kind in {"emoji", "emoji-hz"}:
			return min(num, 20)

		if kind in {"gingerbread", "pumpkin"}:
			return min(num, 10)

		return min(num, 4)

	@lazy
	def realurl(self, v):
		url = self.url

		if not url: return ''

		url = normalize_urls_runtime(url, v)

		if url.startswith('/'): return SITE_FULL + url

		return url

	@lazy
	def total_bet_voted(self, v):
		if "closed" in self.body.lower(): return True
		if v:
			for o in self.options:
				if o.exclusive == 3: return True
				if o.exclusive == 2 and o.voted(v): return True
		return False

	@lazy
	def total_poll_voted(self, v):
		if v:
			if v.id == self.author_id:
				return True
			for o in self.options:
				if o.voted(v): return True
		return False

	@lazy
	def realbody(self, v):
		if self.deleted_utc != 0 and not (v and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or v.id == self.author.id)): return "[Deleted by user]"
		if self.is_banned and not (v and v.admin_level >= PERMS['POST_COMMENT_MODERATION']) and not (v and v.id == self.author.id): return ""

		body = self.body_html or ""

		body = add_options(self, body, v)

		if self.hole != 'chudrama':
			body = censor_slurs_profanities(body, v)

		body = normalize_urls_runtime(body, v)

		return body

	@lazy
	def plainbody(self, v):
		if self.deleted_utc != 0 and not (v and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or v.id == self.author.id)): return "[Deleted by user]"
		if self.is_banned and not (v and v.admin_level >= PERMS['POST_COMMENT_MODERATION']) and not (v and v.id == self.author.id): return ""

		body = self.body
		if not body: return ""

		if self.hole != 'chudrama':
			body = censor_slurs_profanities(body, v, True)

		body = normalize_urls_runtime(body, v)

		return body

	@lazy
	def realtitle(self, v):
		title = self.title_html

		if self.hole != 'chudrama':
			title = censor_slurs_profanities(title, v)

		return title

	@lazy
	def plaintitle(self, v):
		title = self.title

		if self.hole != 'chudrama':
			title = censor_slurs_profanities(title, v, True)

		return title

	@property
	@lazy
	def is_video(self):
		return self.url and any((str(self.url).lower().split('?')[0].endswith(f'.{x}') for x in VIDEO_FORMATS)) and is_safe_url(self.url)

	@property
	@lazy
	def is_audio(self):
		return self.url and any((str(self.url).lower().split('?')[0].endswith(f'.{x}') for x in AUDIO_FORMATS)) and is_safe_url(self.url)

	@property
	@lazy
	def is_image(self):
		return self.url and any((str(self.url).lower().split('?')[0].endswith(f'.{x}') for x in IMAGE_FORMATS)) and is_safe_url(self.url)

	@lazy
	def filtered_reports(self, v):
		return [r for r in self.reports if not r.user.shadowbanned or (v and v.id == r.user_id) or (v and v.admin_level)]

	@lazy
	def active_reports(self, v):
		return len(self.filtered_reports(v))

	@property
	@lazy
	def num_subscribers(self):
		return g.db.query(Subscription).filter_by(post_id=self.id).count()

	@property
	@lazy
	def num_savers(self):
		return g.db.query(SaveRelationship).filter_by(post_id=self.id).count()

	@lazy
	def award_classes(self, v, title=False):
		return get_award_classes(self, v, title)

	@lazy
	def emoji_awards_emojis(self, v, kind, OVER_18_EMOJIS):
		return get_emoji_awards_emojis(self, v, kind, OVER_18_EMOJIS)

	@property
	@lazy
	def is_effortpost(self):
		return len(self.body) >= 1000
