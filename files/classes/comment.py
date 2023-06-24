import time
from math import floor
from random import randint
from urllib.parse import parse_qs, urlencode, urlparse
from flask import g

from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship, scoped_session
from sqlalchemy.schema import FetchedValue
from sqlalchemy.sql.sqltypes import *

from files.classes import Base
from files.helpers.config.const import *
from files.helpers.lazy import lazy
from files.helpers.regex import *
from files.helpers.sorting_and_time import *

from .saves import CommentSaveRelationship

def normalize_urls_runtime(body, v):
	if not v: return body
	if v.reddit != 'old.reddit.com':
		body = reddit_to_vreddit_regex.sub(rf'\1https://{v.reddit}/\2/', body)
	if v.nitter:
		body = twitter_to_nitter_regex.sub(r'\1https://nitter.lacontrevoie.fr/', body)
	if v.imginn:
		body = body.replace('https://instagram.com/', 'https://imginn.com/')
	return body


def add_options(self, body, v):
	if isinstance(self, Comment):
		kind = 'comment'
	else:
		kind = 'post'

	if self.options:
		curr = [x for x in self.options if x.exclusive and x.voted(v)]
		if curr: curr = f" value={kind}-" + str(curr[0].id)
		else: curr = ''
		body += f'<input class="d-none" id="current-{kind}-{self.id}"{curr}>'
		winner = [x for x in self.options if x.exclusive == 3]

	for o in self.options:
		option_body = ''

		if o.exclusive > 1:
			option_body += f'''<div class="custom-control mt-2"><input name="option-{self.id}" autocomplete="off" class="custom-control-input bet" type="radio" id="{o.id}" data-nonce="{g.nonce}" data-onclick="bet_vote(this,'{o.id}','{kind}')"'''
			if o.voted(v): option_body += " checked "

			if not (v and v.coins + v.marseybux >= POLL_BET_COINS) or self.total_bet_voted(v):
				option_body += " disabled "

			option_body += f'''><label class="custom-control-label" for="{o.id}">{o.body_html}<span class="presult-{self.id}'''
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
			option_body += f'<div class="custom-control mt-2"><input type="{input_type}" class="custom-control-input" id="{kind}-{o.id}" name="option-{self.id}"'
			if o.voted(v): option_body += " checked"

			if v:
				if kind == 'post':
					sub = self.sub
				elif self.parent_post:
					sub = self.post.sub
				else:
					sub = None

				if sub in {'furry','vampire','racist','femboy'} and not v.house.lower().startswith(sub):
					option_body += ' disabled '

				option_body += f''' data-nonce="{g.nonce}" data-onclick="poll_vote_{o.exclusive}('{o.id}', '{self.id}', '{kind}')"'''
			else:
				option_body += f''' data-nonce="{g.nonce}" data-onclick="poll_vote_no_v()"'''

			option_body += f'''><label class="custom-control-label" for="{kind}-{o.id}">{o.body_html}<span class="presult-{self.id}'''
			if not self.total_poll_voted(v): option_body += ' d-none'
			option_body += f'"> - <a href="/votes/{kind}/option/{o.id}"><span id="score-{kind}-{o.id}">{o.upvotes}</span> votes</a></label></div>'''

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
	distinguish_level = Column(Integer, default=0)
	deleted_utc = Column(Integer, default=0)
	is_approved = Column(Integer, ForeignKey("users.id"))
	level = Column(Integer, default=1)
	parent_comment_id = Column(Integer, ForeignKey("comments.id"))
	top_comment_id = Column(Integer)
	over_18 = Column(Boolean, default=False)
	is_bot = Column(Boolean, default=False)
	stickied = Column(String)
	stickied_utc = Column(Integer)
	stickied_child_id = Column(Integer)
	sentto = Column(Integer, ForeignKey("users.id"))
	app_id = Column(Integer, ForeignKey("oauth_apps.id"))
	upvotes = Column(Integer, default=1)
	downvotes = Column(Integer, default=0)
	realupvotes = Column(Integer, default=1)
	body = Column(String)
	body_html = Column(String)
	body_ts = Column(TSVECTOR(), server_default=FetchedValue())
	ban_reason = Column(String)
	treasure_amount = Column(String)
	slots_result = Column(String)
	ping_cost = Column(Integer)
	blackjack_result = Column(String)
	casino_game_id = Column(Integer, ForeignKey("casino_games.id"))
	chudded = Column(Boolean, default=False)

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
	def replies(self, sort, v):
		if self.replies2 != None:
			return self.replies2

		replies = g.db.query(Comment).filter_by(parent_comment_id=self.id).order_by(Comment.stickied, Comment.stickied_child_id)
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
		return f"{self.post.shortlink}/{self.id}#context"

	@property
	@lazy
	def permalink(self):
		return f"{SITE_FULL}{self.shortlink}"

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
		if self.ghost and not (g.v and self.id == g.v.id): return '👻'
		return self.author.user_name

	@lazy
	def award_count(self, kind, v):
		if v and v.poor and kind.islower(): return 0
		num = len([x for x in self.awards if x.kind == kind])
		if kind == 'tilt' and num > 4: return 4
		return num

	@property
	@lazy
	def json(self):
		if self.is_banned:
			data = {'is_banned': True,
					'ban_reason': self.ban_reason,
					'id': self.id,
					'post': self.post.id if self.post else 0,
					'level': self.level,
					'parent': self.parent_fullname
					}
		elif self.deleted_utc:
			data = {'deleted_utc': self.deleted_utc,
					'id': self.id,
					'post': self.post.id if self.post else 0,
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
				'author_name': self.author_name,
				'body': self.body,
				'body_html': self.body_html,
				'is_bot': self.is_bot,
				'created_utc': self.created_utc,
				'edited_utc': self.edited_utc or 0,
				'is_banned': bool(self.is_banned),
				'deleted_utc': self.deleted_utc,
				'is_nsfw': self.over_18,
				'permalink': f'/comment/{self.id}#context',
				'stickied': self.stickied,
				'distinguish_level': self.distinguish_level,
				'post_id': self.post.id if self.post else 0,
				'score': self.score,
				'upvotes': self.upvotes,
				'downvotes': self.downvotes,
				'is_bot': self.is_bot,
				'reports': reports,
				'author': '👻' if self.ghost else self.author.json,
				# 'replies': [x.json for x in self.replies(sort="old", v=None)] # WORKER TIMEOUTS ON BUGTHREAD
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
			for o in self.options:
				if o.voted(v): return True
		return False

	@lazy
	def realbody(self, v):
		if self.deleted_utc != 0 and not (v and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or v.id == self.author.id)): return "[Deleted by user]"
		if self.is_banned and not (v and v.admin_level >= PERMS['POST_COMMENT_MODERATION']) and not (v and v.id == self.author.id): return ""

		body = self.body_html or ""

		body = add_options(self, body, v)

		if body:
			if not (self.parent_post and self.post.sub == 'chudrama'):
				body = censor_slurs(body, v)

			body = normalize_urls_runtime(body, v)
			if not v or v.controversial:
				captured = []
				for i in controversial_regex.finditer(body):
					if i.group(1) in captured: continue
					captured.append(i.group(1))

					url = i.group(1)
					p = urlparse(url).query
					p = parse_qs(p, keep_blank_values=True)

					if 'sort' not in p: p['sort'] = ['controversial']

					url_noquery = url.split('?')[0]
					body = body.replace(f'"{url}"', f'"{url_noquery}?{urlencode(p, True)}"')
					body = body.replace(f'>{url}<', f'>{url_noquery}?{urlencode(p, True)}<')

		if not self.ghost and self.author.show_sig(v):
			body += f'<section id="signature-{self.author.id}" class="user-signature"><hr>{self.author.sig_html}</section>'

		return body

	@lazy
	def plainbody(self, v):
		if self.deleted_utc != 0 and not (v and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or v.id == self.author.id)): return "[Deleted by user]"
		if self.is_banned and not (v and v.admin_level >= PERMS['POST_COMMENT_MODERATION']) and not (v and v.id == self.author.id): return ""

		body = self.body

		if not body: return ""

		if not (self.parent_post and self.post.sub == 'chudrama'):
			body = censor_slurs(body, v).replace('<img loading="lazy" data-bs-toggle="tooltip" alt=":marseytrain:" title=":marseytrain:" src="/e/marseytrain.webp">', ':marseytrain:')

		return body

	@lazy
	def collapse_for_user(self, v, path):
		if v and self.author_id == v.id: return False

		if path == '/admin/removed/comments': return False

		if comment_link_regex.search(path): return False

		if self.over_18 and not (v and v.over_18) and not (self.post and self.post.over_18): return True

		if self.is_banned: return True

		if self.author.shadowbanned: return True

		if v and v.filter_words and self.body and any(x in self.body for x in v.filter_words): return True

		return False

	@property
	@lazy
	def is_op(self): return self.author_id==self.post.author_id

	@lazy
	def filtered_reports(self, v):
		return [r for r in self.reports if not r.user.shadowbanned or (v and v.id == r.user_id) or (v and v.admin_level)]

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
			body += f"<strong class='ml-2'>Pushed. Refunded {wager} {currency_kind}.</strong>"
		elif blackjack_status == 'bust':
			body += f"<strong class='ml-2'>Bust. Lost {wager} {currency_kind}.</strong>"
		elif blackjack_status == 'lost':
			body += f"<strong class='ml-2'>Lost {wager} {currency_kind}.</strong>"
		elif blackjack_status == 'won':
			body += f"<strong class='ml-2'>Won {wager} {currency_kind}.</strong>"
		elif blackjack_status == 'blackjack':
			body += f"<strong class='ml-2'>Blackjack! Won {floor(wager * 3/2)} {currency_kind}.</strong>"

		if is_insured == "1":
			body += " <em class='text-success'>Insured.</em>"

		body += '</span>'
		return body


	@property
	@lazy
	def num_savers(self):
		return g.db.query(CommentSaveRelationship).filter_by(comment_id=self.id).count()
