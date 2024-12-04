import time
from math import floor
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse, ParseResult
from flask import g, request, session

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship
from sqlalchemy.schema import FetchedValue
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.config.const import *
from files.helpers.config.awards import *
from files.helpers.slurs_and_profanities import *
from files.helpers.lazy import lazy
from files.helpers.regex import *
from files.helpers.sorting_and_time import *
from files.helpers.bleach_body import *

from .saves import CommentSaveRelationship

def get_emoji_awards_emojis(obj, v, kind, NSFW_EMOJIS):
	if g.show_nsfw:
		emojis = [x.note for x in obj.awards if x.kind == kind]
	else:
		emojis = [x.note for x in obj.awards if x.kind == kind and x.note not in NSFW_EMOJIS]
	return reversed(emojis[:20])

def get_award_classes(obj, v, title=False):
	if obj.distinguished and SITE_NAME == 'WPD':
		return ''

	classes = []

	if obj.chudded:
		classes.append("text-uppercase")
		if not title: classes.append(f"chud-img chud-{obj.id_last_num}")

	if not session.get('poor'):
		if not obj.is_longpost and not obj.ghost and obj.author.bite:
			classes.append('author-bitten')
		if obj.award_count('glowie', v):
			classes.append("glow")
		if obj.award_count('gold', v) and not (obj.is_longpost and not title):
			classes.append("gold-text")
		if obj.rainbowed:
			classes.append("rainbow-text")
		if obj.queened:
			classes.append("queen")
		if obj.sharpened:
			classes.append(f"sharpen")
			if not title: classes.append(f"chud-img sharpen-{obj.id_last_num}")

		if IS_HOMOWEEN():
			if obj.award_count('ectoplasm', v):
				classes.append("ectoplasm")
			if obj.award_count('candycorn', v):
				classes.append("candycorn")
			if obj.award_count('stab', v) and isinstance(obj, Comment):
				classes.append("blood")

		if IS_FISTMAS():
			if obj.award_count('candycane', v):
				classes.append("candycane")

	return ' '.join(classes)

def controversial_link_matcher(match):
	url = match.group(0)
	parsed_url = urlparse(url)
	netloc = parsed_url.netloc
	path = parsed_url.path
	qd = parse_qs(parsed_url.query, keep_blank_values=True)
	if 'sort' not in qd:
		qd['sort'] = ['controversial']
	new_url = ParseResult(scheme="https",
						netloc=netloc,
						path=path,
						params=parsed_url.params,
						query=urlencode(qd, doseq=True),
						fragment=parsed_url.fragment)
	return urlunparse(new_url)

def normalize_urls_runtime(body, v):
	if v and v.reddit != 'old.reddit.com':
		body = reddit_to_vreddit_regex.sub(rf'\1https://{v.reddit}/\2/', body)

	if v and v.twitter != 'x.com':
		body = twitter_domain_regex.sub(rf'\1https://{v.twitter}/', body)

	if v and v.imgsed:
		body = instagram_to_imgsed_regex.sub(r'\1https://imgsed.com/', body)

	if v and v.controversial:
		body = controversial_regex.sub(controversial_link_matcher, body)

	if request.headers.get("Cf-Ipcountry") in AMERICAS_CODES:
		body = body.replace('https://videos.watchpeopledie.tv/', 'https://videos2.watchpeopledie.tv/')

	return body


def add_options(self, body, v):
	if 'details>' in body or 'summary>' in body:
		return body

	if isinstance(self, Comment):
		kind = 'comment'
	else:
		kind = 'post'

	if self.options:
		curr = [x for x in self.options if x.exclusive and x.voted(v)]
		if curr: curr = f" value=option-{kind}-" + str(curr[0].id)
		else: curr = ''
		body += f'<input class="d-none" id="current-option-{kind}-{self.id}"{curr}>'
		winner = [x for x in self.options if x.exclusive == 3]

	for o in self.options:
		option_body = ''

		if o.exclusive > 1: #implies bet
			option_body += f'''<div class="custom-control mt-2"><input name="option-{self.id}" class="custom-control-input bet" type="radio" id="{o.id}" data-nonce="{g.nonce}" data-onclick="option_vote_2(this,'{o.id}','{kind}')"'''
			if o.voted(v): option_body += " checked "

			if not (v and v.coins + v.marseybux >= POLL_BET_COINS) or self.total_bet_voted(v):
				option_body += " disabled "

			option_body += f'''><label class="custom-control-label" for="{o.id}">{o.body_html}<span class="presult-{self.id}'''
			if not self.total_poll_voted(v):
				option_body += ' d-none'
			option_body += f'"> - <a href="/votes/{kind}/option/{o.id}"><span id="option-{o.id}">{o.upvotes}</span> bets</a>'
			if not self.total_bet_voted(v):
				option_body += f'''<span class="cost"> (cost of entry: {POLL_BET_COINS} coins or marseybux)</span>'''
			option_body += "</label>"

			if o.exclusive == 3:
				option_body += " - <b>WINNER!</b>"

			if not winner and v and v.admin_level >= PERMS['POST_BETS_DISTRIBUTE']:
				option_body += f'''<button class="btn btn-primary distribute" data-areyousure="postToastReload(this,'/distribute/{kind}/{o.id}')" data-nonce="{g.nonce}" data-onclick="areyousure(this)">Declare winner</button>'''
			option_body += "</div>"
		else:
			input_type = 'radio' if o.exclusive else 'checkbox'
			option_body += f'<div class="custom-control mt-2"><input type="{input_type}" class="custom-control-input" id="option-{kind}-{o.id}" name="option-{self.id}"'
			if o.voted(v): option_body += " checked"

			disabled = False

			if v:
				if self.hole in {'furry','vampire','racist','femboy','edgy'} and not v.house.lower().startswith(self.hole):
					disabled = True
					option_body += ' disabled '

				option_body += f''' data-nonce="{g.nonce}" data-onclick="option_vote_{o.exclusive}('{o.id}', '{self.id}', '{kind}')"'''
			else:
				option_body += f''' data-nonce="{g.nonce}" data-onclick="option_vote_no_v()"'''

			option_body += f'''><label class="custom-control-label" for="option-{kind}-{o.id}">{o.body_html}<span class="presult-{self.id}'''
			if not disabled and not self.total_poll_voted(v):
				option_body += ' d-none'
			option_body += f'"> - <a href="/votes/{kind}/option/{o.id}"><score id="score-option-{kind}-{o.id}">{o.upvotes}</score> votes</a></label></div>'''

		if o.exclusive > 1: s = '##'
		elif o.exclusive: s = '&amp;&amp;'
		else: s = '$$'

		if f'{s}{o.body_html}{s}' in body:
			body = body.replace(f'{s}{o.body_html}{s}', option_body, 1)
		elif not o.created_utc or o.created_utc < 1677622270:
			body += option_body

	return body


class Comment(Base):
	__tablename__ = "comments"

	id = Column(Integer, primary_key=True)
	author_id = Column(Integer, ForeignKey("users.id"))
	parent_post = Column(Integer, ForeignKey("posts.id"))
	wall_user_id = Column(Integer, ForeignKey("users.id"))
	created_utc = Column(Integer)
	edited_utc = Column(Integer, default=0)
	is_banned = Column(Boolean, default=False)
	ghost = Column(Boolean, default=False)
	bannedfor = Column(String)
	chuddedfor = Column(String)
	distinguished = Column(Boolean, default=False)
	deleted_utc = Column(Integer, default=0)
	is_approved = Column(Integer, ForeignKey("users.id"))
	level = Column(Integer, default=1)
	parent_comment_id = Column(Integer, ForeignKey("comments.id"))
	top_comment_id = Column(Integer)
	is_bot = Column(Boolean, default=False)
	pinned = Column(String)
	pinned_utc = Column(Integer)
	num_of_pinned_children = Column(Integer, default=0)
	sentto = Column(Integer, ForeignKey("users.id"))
	app_id = Column(Integer, ForeignKey("oauth_apps.id"))
	upvotes = Column(Integer, default=1)
	downvotes = Column(Integer, default=0)
	realupvotes = Column(Integer, default=1)
	body = Column(String, default='')
	body_html = Column(String)
	body_ts = Column(TSVECTOR(), server_default=FetchedValue())
	ban_reason = Column(String)
	treasure_amount = Column(String)
	slots_result = Column(String)
	ping_cost = Column(Integer, default=0)
	blackjack_result = Column(String)
	casino_game_id = Column(Integer, ForeignKey("casino_games.id"))
	chudded = Column(Boolean, default=False)
	rainbowed = Column(Boolean, default=False)
	queened = Column(Boolean, default=False)
	sharpened = Column(Boolean, default=False)
	dyslexia = Column(Boolean, default=False)
	coins = Column(Integer, default=0)

	if FEATURES['NSFW_MARKING']:
		nsfw = Column(Boolean, default=False)
	else:
		nsfw = False

	oauth_app = relationship("OauthApp")
	post = relationship("Post", back_populates="comments")
	author = relationship("User", primaryjoin="User.id==Comment.author_id")
	senttouser = relationship("User", primaryjoin="User.id==Comment.sentto")
	parent_comment = relationship("Comment", remote_side=[id])
	awards = relationship("AwardRelationship", order_by="AwardRelationship.awarded_utc.desc()", back_populates="comment")
	reports = relationship("CommentReport", order_by="CommentReport.created_utc")
	options = relationship("CommentOption", order_by="CommentOption.id")
	casino_game = relationship("CasinoGame")
	wall_user = relationship("User", primaryjoin="User.id==Comment.wall_user_id")
	edits = relationship("CommentEdit", order_by="CommentEdit.id.desc()")
	media_usages = relationship("MediaUsage", back_populates="comment")
	notes = relationship("CommentNote", order_by="CommentNote.id", back_populates="parent")

	def __init__(self, *args, **kwargs):
		if "created_utc" not in kwargs:
			kwargs["created_utc"] = int(time.time())
		super().__init__(*args, **kwargs)

	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id})>"

	@property
	@lazy
	def top_comment(self):
		return g.db.get(Comment, self.top_comment_id)

	@property
	@lazy
	def controversial(self):
		if self.downvotes > 5 and 0.25 < self.upvotes / self.downvotes < 4: return True
		return False

	@property
	@lazy
	def age_string(self):
		notif_utc = self.__dict__.get("notif_utc")

		if notif_utc: timestamp = notif_utc
		elif self.created_utc: timestamp = self.created_utc
		else: return None
		return make_age_string(timestamp)

	@property
	@lazy
	def edited_string(self):
		if not self.edited_utc: return None
		return make_age_string(self.edited_utc)

	@property
	@lazy
	def score(self):
		return self.upvotes - self.downvotes

	@property
	@lazy
	def fullname(self):
		return f"c_{self.id}"

	@property
	@lazy
	def id_last_num(self):
		return str(self.id)[-1]

	@property
	@lazy
	def parent_fullname(self):
		if self.parent_comment_id: return f"c_{self.parent_comment_id}"
		elif self.parent_post: return f"p_{self.parent_post}"

	@lazy
	def replies(self, sort):
		if self.replies2 != None:
			return self.replies2

		replies = g.db.query(Comment).filter_by(parent_comment_id=self.id).order_by(Comment.pinned, Comment.num_of_pinned_children.desc())
		if not self.parent_post: sort='old'
		return sort_objects(sort, replies, Comment).all()


	@property
	def replies2(self):
		return self.__dict__.get("replies2")

	@replies2.setter
	def replies2(self, value):
		self.__dict__["replies2"] = value

	@property
	@lazy
	def shortlink(self):
		if self.wall_user_id:
			return f"/@{self.wall_user.username}/wall/comment/{self.id}#context"
		if self.parent_post:
			return f"{self.post.shortlink}/{self.id}#context"
		return f"/notification/{self.id}#context"

	@property
	@lazy
	def permalink(self):
		return f"{SITE_FULL}{self.shortlink}"

	@property
	@lazy
	def textlink(self):
		return f'<a href="{self.shortlink}">this comment</a>'

	@property
	@lazy
	def log_link(self):
		return f"{SITE_FULL}/transfers/{self.id}"

	@property
	@lazy
	def more_comments(self):
		if self.wall_user_id:
			return f"/@{self.wall_user.username}/wall/comment/{self.id}?context=0#context"
		return f"{self.post.permalink}/{self.id}?context=0#context"

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

	@lazy
	def award_count(self, kind, v):
		if self.distinguished and SITE_NAME == 'WPD':
			return 0

		if session.get('poor'):
			return 0
		return len([x for x in self.awards if x.kind == kind])

	@property
	@lazy
	def json(self):
		if self.is_banned:
			data = {'is_banned': True,
					'ban_reason': self.ban_reason,
					'id': self.id,
					'post_id': self.post.id if self.post else 0,
					'hole': self.hole,
					'level': self.level,
					'parent': self.parent_fullname
					}
		elif self.deleted_utc:
			data = {'deleted_utc': self.deleted_utc,
					'id': self.id,
					'post_id': self.post.id if self.post else 0,
					'hole': self.hole,
					'level': self.level,
					'parent': self.parent_fullname
					}
		else:
			reports = {}
			for r in self.reports:
				reports[r.user.username] = r.reason

			data = {
				'id': self.id,
				'level': self.level,
				'author_id': '👻' if self.ghost else self.author_id,
				'author_name': self.author_name,
				'body': self.body,
				'body_html': self.body_html,
				'is_bot': self.is_bot,
				'created_utc': self.created_utc,
				'edited_utc': self.edited_utc or 0,
				'is_banned': bool(self.is_banned),
				'deleted_utc': self.deleted_utc,
				'is_nsfw': self.nsfw,
				'permalink': f'/comment/{self.id}#context',
				'pinned': self.pinned,
				'distinguished': self.distinguished,
				'post_id': self.post.id if self.post else 0,
				'hole': self.hole,
				'score': self.score,
				'upvotes': self.upvotes,
				'downvotes': self.downvotes,
				'is_bot': self.is_bot,
				'reports': reports,
				'replies': [x.id for x in self.replies(sort="old")]
				}

		if self.level >= 2: data['parent_comment_id'] = self.parent_comment_id

		return data

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

		if body:
			if self.hole != 'chudrama':
				body = censor_slurs_profanities(body, v)

			body = normalize_urls_runtime(body, v)

			if self.created_utc > 1706137534:
				body = bleach_body_html(body, runtime=True) #to stop slur filters and poll options being used as a vector for html/js injection

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

		return body

	@lazy
	def collapse_for_user(self, v, focused_comment, path=''):
		if v and self.author_id == v.id: return False

		if path.endswith('/comments'): return False

		if focused_comment: return False

		if self.nsfw and not (any(path.startswith(x) for x in ('/post/','/comment/','/h/')) and self.post.nsfw) and not g.show_nsfw:
			return True

		if self.is_banned: return True

		if v and v.filter_words and self.body and any(x in self.body for x in v.filter_words): return True

		return False

	@property
	@lazy
	def is_op(self): return self.author_id==self.post.author_id

	@lazy
	def filtered_reports(self, v):
		return [r for r in self.reports if not r.user.shadowbanned or (v and v.id == r.user_id) or (v and v.admin_level >= PERMS['USER_SHADOWBAN'])]

	@lazy
	def active_reports(self, v):
		return len(self.filtered_reports(v))

	@property
	@lazy
	def blackjack_html(self):
		if not self.blackjack_result: return ''

		split_result = self.blackjack_result.split('_')
		blackjack_status = split_result[3]
		player_hand = split_result[0].replace('X', '10')
		dealer_hand = split_result[1].split('/')[0] if blackjack_status == 'active' else split_result[1]
		dealer_hand = dealer_hand.replace('X', '10')
		wager = int(split_result[4])
		try: kind = split_result[5]
		except: kind = "coins"
		currency_kind = "Coins" if kind == "coins" else "Marseybux"

		try: is_insured = split_result[6]
		except: is_insured = "0"

		body = f"<span id='blackjack-{self.id}' class='ml-2'><em>{player_hand} vs. {dealer_hand}</em>"

		if blackjack_status == 'push':
			body += f"<strong class='ml-2'>Pushed. Refunded {commas(wager)} {currency_kind}.</strong>"
		elif blackjack_status == 'bust':
			body += f"<strong class='ml-2'>Bust. Lost {commas(wager)} {currency_kind}.</strong>"
		elif blackjack_status == 'lost':
			body += f"<strong class='ml-2'>Lost {commas(wager)} {currency_kind}.</strong>"
		elif blackjack_status == 'won':
			body += f"<strong class='ml-2'>Won {commas(wager)} {currency_kind}.</strong>"
		elif blackjack_status == 'blackjack':
			body += f"<strong class='ml-2'>Blackjack! Won {commas(floor(wager * 3/2))} {currency_kind}.</strong>"

		if is_insured == "1":
			body += " <em class='text-success'>Insured.</em>"

		body += '</span>'
		return body


	@property
	@lazy
	def num_savers(self):
		return g.db.query(CommentSaveRelationship).filter_by(comment_id=self.id).count()

	@lazy
	def award_classes(self, v):
		return get_award_classes(self, v)

	@lazy
	def emoji_awards_emojis(self, v, kind, NSFW_EMOJIS):
		return get_emoji_awards_emojis(self, v, kind, NSFW_EMOJIS)

	@property
	@lazy
	def is_longpost(self):
		return self.body and len(self.body) >= 2000

	@property
	@lazy
	def hole(self):
		if self.parent_post:
			return self.post.hole
		return None

	def pin_parents(self):
		c = self
		while c.level > 1:
			c = c.parent_comment
			c.num_of_pinned_children += 1
			g.db.add(c)

	def unpin_parents(self):
		c = self
		while c.level > 1:
			c = c.parent_comment
			c.num_of_pinned_children -= 1
			if c.num_of_pinned_children < 0:
				c.num_of_pinned_children = 0
			g.db.add(c)
