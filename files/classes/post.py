import random
import time
from urllib.parse import urlparse
from flask import g, session
from bs4 import BeautifulSoup

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
from files.helpers.bleach_body import *
from files.helpers.youtube import *

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
	effortpost = Column(Boolean, default=False)
	views = Column(Integer, default=0)
	deleted_utc = Column(Integer, default=0)
	distinguished = Column(Boolean, default=False)
	pinned = Column(String)
	pinned_utc = Column(Integer)
	profile_pinned = Column(Boolean, default=False)
	hole_pinned = Column(String)
	hole = Column(String, ForeignKey("holes.name"))
	draft = Column(Boolean, default=False)
	comment_count = Column(Integer, default=0)
	is_approved = Column(Integer, ForeignKey("users.id"))
	is_bot = Column(Boolean, default=False)
	upvotes = Column(Integer, default=1)
	downvotes = Column(Integer, default=0)
	realupvotes = Column(Integer, default=1)
	app_id = Column(Integer, ForeignKey("oauth_apps.id"))
	title = Column(String)
	title_html = Column(String)
	url = Column(String)
	body = Column(String, default='')
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
	title_ts = Column(TSVECTOR(), server_default=FetchedValue())
	body_ts = Column(TSVECTOR(), server_default=FetchedValue())

	if FEATURES['NSFW_MARKING']:
		nsfw = Column(Boolean, default=False)
	else:
		nsfw = False

	if SITE_NAME == 'WPD' and not IS_LOCALHOST:
		cw = Column(Boolean, default=False)

	author = relationship("User", primaryjoin="Post.author_id==User.id")
	oauth_app = relationship("OauthApp")
	approved_by = relationship("User", uselist=False, primaryjoin="Post.is_approved==User.id")
	awards = relationship("AwardRelationship", order_by="AwardRelationship.awarded_utc.desc()", back_populates="post")
	reports = relationship("Report", order_by="Report.created_utc")
	comments = relationship("Comment", primaryjoin="Comment.parent_post==Post.id", order_by="Comment.id", back_populates="post")
	hole_obj = relationship("Hole", primaryjoin="foreign(Post.hole)==remote(Hole.name)")
	options = relationship("PostOption", order_by="PostOption.id")
	edits = relationship("PostEdit", order_by="PostEdit.id.desc()")
	media_usages = relationship("MediaUsage", back_populates="post")

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

		if self.is_banned or self.hole in {'chudrama', 'countryclub', 'highrollerclub'}:
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
	def textlink(self):
		return f'<a href="{self.shortlink}">{self.title}</a>'

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
		return self.author.switched.user_name

	@property
	@lazy
	def author_name_punish_modal(self):
		if self.ghost and not (hasattr(g, 'v') and g.v and self.id == g.v.id): return '👻'
		return self.author.username

	@property
	@lazy
	def is_youtube(self):
		return self.domain == "youtube.com" and self.embed and self.embed.startswith('<lite-youtube')

	@property
	@lazy
	def thumb_url(self):
		if self.nsfw:
			return f"{SITE_FULL_IMAGES}/i/nsfw.webp?x=15"
		elif not self.url:
			return f"{SITE_FULL_IMAGES}/i/{SITE_NAME}/default_text.webp?x=15"
		elif self.thumburl:
			if self.thumburl.startswith('/'): return SITE_FULL + self.thumburl
			return self.thumburl
		elif self.domain == 'youtube.com':
			id, _ = get_youtube_id_and_t(self.url)
			if id:
				return f"https://i.ytimg.com/vi/{id}/hqdefault.jpg"
		elif self.is_youtube or self.is_video:
			return f"{SITE_FULL_IMAGES}/i/default_thumb_video.webp?x=15"
		elif self.is_audio:
			return f"{SITE_FULL_IMAGES}/i/default_thumb_audio.webp?x=15"
		elif self.domain == SITE:
			return f"{SITE_FULL_IMAGES}/i/{SITE_NAME}/site_preview.webp?x=15"
		elif self.domain == 'reddit.com':
			if SITE == 'watchpeopledie.tv':
				return "https://i.watchpeopledie.tv/images/1728360164949774.webp"
			else:
				return "https://i.rdrama.net/images/17325804049299114.webp"
		elif self.domain == 'x.com':
			if SITE == 'watchpeopledie.tv':
				return "https://i.watchpeopledie.tv/images/17110710913860154.webp"
			else:
				return "https://i.rdrama.net/images/17104844257987864.webp"
		elif self.domain == 'bsky.app':
			return "https://i.rdrama.net/images/1732387179866288.webp"
		elif self.domain == 'scored.co':
			return "https://i.rdrama.net/images/17309046624223871.webp"
		elif self.domain == 'tiktok.com':
			if SITE == 'watchpeopledie.tv':
				return "https://i.watchpeopledie.tv/images/17323894958019562r.webp"
			else:
				return "https://i.rdrama.net/images/17323893974484575r.webp"
		elif self.domain == 'instagram.com':
			if SITE == 'watchpeopledie.tv':
				return "https://i.watchpeopledie.tv/images/1732443717978363r.webp"
			else:
				return "https://i.rdrama.net/images/17324436577768068r.webp"
		elif self.domain == 'news.ycombinator.com':
			return "https://i.rdrama.net/images/17324613596010087r.webp"
		elif self.domain.startswith('kiwifarms.'):
			return "https://i.rdrama.net/images/16764197614414222.webp"
		else:
			return f"{SITE_FULL_IMAGES}/i/default_thumb_link.webp?x=15"

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
				'pinned': self.pinned,
				'draft' : self.draft,
				'distinguished': self.distinguished,
				'voted': self.voted if hasattr(self, 'voted') else 0,
				'reports': reports,
				}

		if "replies" in self.__dict__:
			data["replies"] = [x.json for x in self.replies]

		return data

	@lazy
	def award_count(self, kind, v):
		if session.get('poor'):
			return 0

		if self.distinguished and SITE_NAME == 'WPD':
			return 0

		num = len([x for x in self.awards if x.kind == kind])

		if kind in {"shit", "fireflies", "tilt"}:
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
		if self.deleted_utc != 0 and not (v and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or v.id == self.author.id)):
			return "[Deleted by user]"
		if self.is_banned and not (v and v.admin_level >= PERMS['POST_COMMENT_MODERATION']) and not (v and v.id == self.author.id):
			return ""

		body = self.body_html or ""

		body = add_options(self, body, v)

		if self.hole != 'chudrama':
			body = censor_slurs_profanities(body, v)

		if self.embed and self.domain in {"x.com", "bsky.app"}:
			body = self.embed + body

		body = normalize_urls_runtime(body, v)

		if self.created_utc > 1706137534:
			body = bleach_body_html(body, runtime=True) #to stop slur filters and poll options being used as a vector for html/js injection

		t = time.time()
		community_notes = g.db.query(Comment).filter(
			Comment.parent_post == self.id,
			Comment.pinned.like('% (community note award)'),
		)
		for community_note in community_notes:
			body += f'<fieldset class="card rounded community-note"><legend><i class="fas fa-users text-blue mr-2"></i>Community Note</legend>{community_note.realbody(v)}</fieldset>'

		print(time.time() - t, flush=True)

		return body

	@lazy
	def plainbody(self, v):
		if self.deleted_utc != 0 and not (v and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or v.id == self.author.id)):
			return "[Deleted by user]"
		if self.is_banned and not (v and v.admin_level >= PERMS['POST_COMMENT_MODERATION']) and not (v and v.id == self.author.id):
			return ""

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
		return self.url and any(str(self.url).lower().split('?')[0].endswith(f'.{x}') for x in VIDEO_FORMATS) and is_safe_url(self.url)

	@property
	@lazy
	def is_audio(self):
		return self.url and any(str(self.url).lower().split('?')[0].endswith(f'.{x}') for x in AUDIO_FORMATS) and is_safe_url(self.url)

	@property
	@lazy
	def is_image(self):
		return self.url and any(str(self.url).lower().split('?')[0].endswith(f'.{x}') for x in IMAGE_FORMATS) and is_safe_url(self.url)

	@lazy
	def filtered_reports(self, v):
		return [r for r in self.reports if not r.user.shadowbanned or (v and v.id == r.user_id) or (v and v.admin_level >= PERMS['USER_SHADOWBAN'])]

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
	def emoji_awards_emojis(self, v, kind, NSFW_EMOJIS):
		return get_emoji_awards_emojis(self, v, kind, NSFW_EMOJIS)

	@property
	@lazy
	def is_longpost(self):
		return self.body and len(self.body) >= 2000

	@lazy
	def hole_changable(self, v):
		if self.hole == 'chudrama':
			return v.admin_level >= PERMS['POST_COMMENT_MODERATION']
		else:
			return v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or (v.mods_hole(self.hole)) or self.author_id == v.id

	@property
	@lazy
	def can_be_effortpost(self):
		if SITE_NAME == 'WPD':
			min_chars = 2000
			min_lines = 10
		else:
			min_chars = 3000
			min_lines = 20

		if self.body_html.count('<p>') < min_lines:
			return False

		soup = BeautifulSoup(self.body_html, 'lxml')
		tags = soup.html.body.find_all(lambda tag: tag.name in {'p','ul','table','details'} and tag.text, recursive=False)
		post_char_count = 0
		for tag in tags:
			post_char_count += len(tag.text)

		if post_char_count < min_chars:
			return False

		return True

	@property
	@lazy
	def hot_ranking(self):
		ti = int(time.time()) + 3600
		metric = self.realupvotes + 1 + self.comment_count/5
		return -1000000*(metric / pow(((ti - self.created_utc)/1000), 1.4))
