import random
from operator import *
import datetime

import pyotp
from sqlalchemy import Column, ForeignKey, FetchedValue
from sqlalchemy.orm import aliased, deferred, Query
from sqlalchemy.sql import case, func, literal
from sqlalchemy.sql.expression import not_, and_, or_
from sqlalchemy.sql.sqltypes import *
from sqlalchemy.exc import OperationalError
from flask import g, session, request, has_request_context

from files.classes import Base
from files.classes.casino_game import CasinoGame
from files.classes.group import *
from files.classes.hole import Hole
from files.classes.chats import *
from files.classes.currency_logs import CurrencyLog
from files.classes.mod_logs import ModAction
from files.helpers.config.const import *
from files.helpers.config.modaction_kinds import *
from files.helpers.config.awards import *
from files.helpers.media import *
from files.helpers.security import *
from files.helpers.sorting_and_time import *
from files.helpers.can_see import *

from .alts import Alt
from .award import AwardRelationship
from .badges import *
from .clients import *
from .follows import *
from .hats import *
from .mod_logs import *
from .notifications import Notification
from .saves import *
from .hole_relationship import *
from .hole_logs import *
from .subscriptions import *
from .userblock import *
from .usermute import *
from .art_submissions import *

from math import ceil

if SITE == 'devrama.net':
	DEFAULT_ADMIN_LEVEL = 3
	DEFAULT_COINS = 100000000
	DEFAULT_MARSEYBUX = 100000000
else:
	DEFAULT_ADMIN_LEVEL = 0
	DEFAULT_COINS = 0
	DEFAULT_MARSEYBUX = 0

def is_underage_reason(reason):
	reason = reason.lower()
	if reason.startswith('underage'): return True
	if ' underage' in reason: return True
	return False

class User(Base):
	__tablename__ = "users"

	id = Column(Integer, primary_key=True)
	username = Column(String)
	namecolor = Column(String, default=DEFAULT_COLOR)
	background = Column(String)
	profile_background = Column(String)
	flair = deferred(Column(String))
	flair_html = Column(String)
	flaircolor = Column(String, default=DEFAULT_COLOR)
	theme = Column(String, default=DEFAULT_THEME)
	themecolor = Column(String, default=DEFAULT_COLOR)
	song = Column(String)
	highres = Column(String)
	profileurl = Column(String)
	bannerurl = Column(String)
	house = Column(String, default='')
	old_house = Column(String, default='')
	patron = Column(Integer, default=0)
	patron_utc = Column(Integer, default=0)
	verified = Column(String)
	verifiedcolor = Column(String)
	hieroglyphs = Column(Integer, default=0)
	rehab = Column(Integer, default=0)
	longpost = Column(Integer, default=0)
	bird = Column(Integer, default=0)
	email = deferred(Column(String))
	css = Column(String)
	profilecss = deferred(Column(String))
	passhash = deferred(Column(String))
	post_count = Column(Integer, default=0)
	comment_count = Column(Integer, default=0)
	received_award_count = Column(Integer, default=0)
	created_utc = Column(Integer)
	admin_level = Column(Integer, default=DEFAULT_ADMIN_LEVEL)
	last_active = Column(Integer)
	currency_spent_on_awards = Column(Integer, default=0)
	currency_spent_on_hats = Column(Integer, default=0)
	lootboxes_bought = Column(Integer, default=0)
	chud = Column(Integer, default=0)
	queen = Column(Integer, default=0)
	chud_phrase = Column(String)
	email_verified = Column(Boolean, default=False)
	shadowbanned = Column(Integer, ForeignKey("users.id"))
	chudded_by = Column(Integer, ForeignKey("users.id"))
	slurreplacer = Column(Integer, default=1)
	profanityreplacer = Column(Integer, default=1)
	flairchanged = Column(Integer, default=0)
	namechanged = Column(Integer, default=0)
	newtab = Column(Boolean, default=False)
	newtabexternal = Column(Boolean, default=True)
	frontsize = Column(Integer, default=25)
	bio = deferred(Column(String))
	bio_html = Column(String)
	sig = deferred(Column(String))
	sig_html = Column(String)
	show_sigs = Column(Boolean, default=True)
	progressivestack = Column(Integer, default=0)
	deflector = Column(Integer, default=0)
	penetrator = Column(Integer, default=0)
	friends = deferred(Column(String))
	friends_html = deferred(Column(String))
	enemies = deferred(Column(String))
	enemies_html = deferred(Column(String))
	is_banned = Column(Integer, ForeignKey("users.id"))
	unban_utc = Column(Integer)
	ban_reason = deferred(Column(String))
	shadowban_reason = deferred(Column(String))
	is_muted = Column(Boolean, default=False)
	login_nonce = Column(Integer, default=0)
	coins = Column(Integer, default=DEFAULT_COINS)
	truescore = Column(Integer, default=0)
	marseybux = Column(Integer, default=DEFAULT_MARSEYBUX)
	mfa_secret = deferred(Column(String))
	private_posts = Column(Boolean, default=False)
	private_comments = Column(Boolean, default=False)
	stored_subscriber_count = Column(Integer, default=0)
	defaultsortingcomments = Column(String, default="hot")
	defaultsorting = Column(String, default="hot")
	defaulttime = Column(String, default=DEFAULT_TIME_FILTER)
	custom_filter_list = Column(String)
	keyword_notifs = Column(String)
	snappy_quotes = deferred(Column(String))
	original_username = Column(String)
	extra_username = Column(String)
	prelock_username = Column(String)
	referred_by = Column(Integer, ForeignKey("users.id"))
	currently_held_lottery_tickets = Column(Integer, default=0)
	total_held_lottery_tickets = Column(Integer, default=0)
	total_lottery_winnings = Column(Integer, default=0)
	last_viewed_modmail_notifs = Column(Integer, default=0)
	last_viewed_post_notifs = Column(Integer, default=0)
	last_viewed_log_notifs = Column(Integer, default=0)
	last_viewed_offsite_notifs = Column(Integer, default=0)
	bite = Column(Integer, default=0)
	owoify = Column(Integer, default=0)
	sharpen = Column(Integer, default=0)
	marsify = Column(Integer, default=0)
	rainbow = Column(Integer, default=0)
	spider = Column(Integer, default=0)
	lifetimedonated = Column(Integer, default=0)
	lifetimedonated_visible = Column(Boolean, default=False)
	blacklisted_by = Column(Integer, ForeignKey("users.id"))
	grinch = Column(Boolean, default=SITE_NAME != 'rDrama') #don't put in an if condition, it will cause an error bc it has a not-null constraint
	group_creation_notifs = Column(Boolean, default=False)
	effortpost_notifs = Column(Boolean, default=False)
	offsite_mentions = Column(Boolean)
	pronouns = Column(String, default=DEFAULT_PRONOUNS)
	flag = Column(String)

	if SITE_NAME == 'WPD' and not IS_LOCALHOST:
		twitter = 'x.com'
		imgsed = False
		controversial = False
		reddit = 'old.reddit.com'
		earlylife = 0
		hole_creation_notifs = False
		hidevotedon = Column(Boolean, default=False)
		hide_cw = Column(Boolean, default=False)
	else:
		twitter = Column(String, default='x.com')
		imgsed = Column(Boolean, default=False)
		controversial = Column(Boolean, default=False)
		reddit = Column(String, default='old.reddit.com')
		earlylife = Column(Integer, default=0)
		hole_creation_notifs = Column(Boolean, default=True)
		hidevotedon = False
		hide_cw = False

	if IS_HOMOWEEN():
		zombie = Column(Integer, default=0) # > 0 vaxxed; < 0 zombie
		jumpscare = Column(Integer, default=0)

	badges = relationship("Badge", order_by="Badge.created_utc", back_populates="user")
	subscriptions = relationship("Subscription", back_populates="user")
	following = relationship("Follow", primaryjoin="Follow.user_id==User.id", back_populates="user")
	followers = relationship("Follow", primaryjoin="Follow.target_id==User.id", back_populates="target")
	blocking = relationship("UserBlock", lazy="dynamic", primaryjoin="User.id==UserBlock.user_id", back_populates="user")
	blocked = relationship("UserBlock", lazy="dynamic", primaryjoin="User.id==UserBlock.target_id", back_populates="target")
	authorizations = relationship("ClientAuth", back_populates="user")
	apps = relationship("OauthApp", back_populates="author")
	awards = relationship("AwardRelationship", primaryjoin="User.id==AwardRelationship.user_id", back_populates="user")
	referrals = relationship("User", primaryjoin="User.id==User.referred_by", order_by="User.created_utc")
	designed_hats = relationship("HatDef", primaryjoin="User.id==HatDef.author_id", back_populates="author")
	owned_hats = relationship("Hat", back_populates="owners")
	hats_equipped = relationship("Hat", lazy="raise", viewonly=True)
	hole_mods = relationship("Mod", primaryjoin="User.id == Mod.user_id", lazy="raise")
	notifications = relationship("Notification", back_populates="user")
	deletion = relationship("AccountDeletion", back_populates="user", uselist=False)

	def __init__(self, **kwargs):

		if "password" in kwargs:
			kwargs["passhash"] = hash_password(kwargs["password"])
			kwargs.pop("password")

		if "created_utc" not in kwargs:
			kwargs["created_utc"] = int(time.time())
			kwargs["last_active"] = kwargs["created_utc"]
			kwargs["last_viewed_modmail_notifs"] = kwargs["created_utc"]
			kwargs["last_viewed_post_notifs"] = kwargs["created_utc"]
			kwargs["last_viewed_log_notifs"] = kwargs["created_utc"]
			kwargs["last_viewed_offsite_notifs"] = kwargs["created_utc"]

		super().__init__(**kwargs)


	def __repr__(self):
		return f"<{self.__class__.__name__}(id={self.id}, username={self.username})>"

	def pay_account(self, currency, amount, reason=None):
		if self.id in {AUTOJANNY_ID, LONGPOSTBOT_ID, ZOZBOT_ID}:
			return

		if SITE == 'watchpeopledie.tv' and self.id == 5222:
			return

		if self.admin_level < PERMS['INFINITE_CURRENCY']:
			user_query = g.db.query(User).options(load_only(User.id)).filter_by(id=self.id)

			if currency == 'coins':
				try:
					user_query.update({ User.coins: User.coins + amount })
				except OperationalError as e:
					if str(e).startswith('(psycopg2.errors.QueryCanceled) canceling statement due to statement timeout'):
						stop(409, f"Statement timeout while trying to pay @{self.username} {amount} coins!")
					raise
			else:
				user_query.update({ User.marseybux: User.marseybux + amount })

		if reason and amount:
			currency_log = CurrencyLog(
				user_id=self.id,
				currency=currency,
				amount=amount,
				reason=reason,
			)
			g.db.add(currency_log)
			if currency == 'coins':
				currency_log.balance = self.coins
			else:
				currency_log.balance = self.marseybux

	def charge_account(self, currency, amount, reason=None, **kwargs):
		succeeded = False

		should_check_balance = kwargs.get('should_check_balance', True)

		if self.admin_level < PERMS['INFINITE_CURRENCY']:
			user_query = g.db.query(User).options(load_only(User.id)).filter_by(id=self.id)

		logs = []
		if currency == 'coins':
			account_balance = self.coins

			if not should_check_balance or account_balance >= amount:
				if self.admin_level < PERMS['INFINITE_CURRENCY']:
					user_query.update({ User.coins: User.coins - amount })
				succeeded = True
				logs = [['coins', amount]]
		elif currency == 'marseybux':
			account_balance = self.marseybux

			if not should_check_balance or account_balance >= amount:
				if self.admin_level < PERMS['INFINITE_CURRENCY']:
					user_query.update({ User.marseybux: User.marseybux - amount })
				succeeded = True
				logs = [['marseybux', amount]]
		elif currency == 'coins/marseybux':
			if self.marseybux >= amount:
				subtracted_mbux = amount
				subtracted_coins = 0
			else:
				subtracted_mbux = self.marseybux
				subtracted_coins = amount - subtracted_mbux
				if subtracted_coins > self.coins and self.admin_level < PERMS['INFINITE_CURRENCY']:
					return False

			if self.admin_level < PERMS['INFINITE_CURRENCY']:
				user_query.update({
					User.marseybux: User.marseybux - subtracted_mbux,
					User.coins: User.coins - subtracted_coins,
				})
			succeeded = True
			logs = [['coins', subtracted_coins], ['marseybux', subtracted_mbux]]

		if self.admin_level >= PERMS['INFINITE_CURRENCY'] or self.id == 48:
			succeeded = True

		if succeeded:
			g.db.add(self)
			if reason:
				for currency, amount in logs:
					if not amount: continue
					currency_log = CurrencyLog(
						user_id=self.id,
						currency=currency,
						amount=-amount,
						reason=reason,
					)
					g.db.add(currency_log)
					if currency == 'coins':
						currency_log.balance = self.coins
					else:
						currency_log.balance = self.marseybux

		return succeeded

	@property
	@lazy
	def event_music(self):
		return session.get('event_music', SITE_NAME == 'rDrama')

	@property
	@lazy
	def cursormarsey(self):
		return session.get('cursormarsey', CURSORMARSEY_DEFAULT)

	@property
	@lazy
	def nsfw_warnings(self):
		return bool(session.get('nsfw_warnings', True))

	@property
	@lazy
	def allowed_in_chat(self):
		if self.admin_level >= PERMS['BYPASS_CHAT_TRUESCORE_REQUIREMENT']:
			return True
		if self.truescore >= TRUESCORE_MINIMUM:
			return True
		if self.patron > 1:
			return True
		return False

	@property
	@lazy
	def num_of_bought_awards(self):
		return g.db.query(AwardRelationship).filter_by(user_id=self.id).count()

	@property
	@lazy
	def num_of_owned_hats(self):
		return len(self.owned_hats)

	@property
	@lazy
	def hats_owned_proportion_display(self):
		total_num_of_hats = g.db.query(HatDef).filter(HatDef.submitter_id == None, HatDef.price > 0).count()
		proportion = f'{float(self.num_of_owned_hats) / total_num_of_hats:.1%}' if total_num_of_hats else 'N/A'
		return (proportion, total_num_of_hats)

	@property
	@lazy
	def num_of_designed_hats(self):
		return len(self.designed_hats)

	@property
	def equipped_hats(self):
		try:
			return self.hats_equipped
		except:
			return g.db.query(Hat).filter_by(user_id=self.id, equipped=True).all()

	@property
	@lazy
	def equipped_hat_ids(self):
		return [x.hat_id for x in self.equipped_hats]

	@property
	@lazy
	def equipped_hat(self):
		if self.equipped_hats:
			return random.choice(self.equipped_hats)
		return None

	@property
	@lazy
	def forced_hat(self):
		if self.is_suspended:

			if self.username.startswith('deleted~') and not (g.v and g.v.admin_level >= PERMS['VIEW_DELETED_ACCOUNTS']):
				text = "This user was banned before they deleted their account!"
			else:
				text = 'Banned'
				if not self.ban_reason.startswith('Ban award') and not self.ban_reason.startswith('Grass award'):
					text += f' by {self.banned_by}'
				text += f' for "{self.ban_reason}"'
				if self.unban_utc:
					text += f' - {self.unban_string}'

			return ("Behind Bars", text)

		user_forced_hats = []
		for k, val in forced_hats.items():
			get = getattr(self, k)
			if get and (get is True or get > 1):
				if isinstance(val[0], tuple):
					user_forced_hats.append(random.choice(val))
				else:
					user_forced_hats.append(val)
		if user_forced_hats: return random.choice(user_forced_hats)
		else: return None

	@property
	@lazy
	def new_user(self):
		return self.age < NEW_USER_AGE

	@lazy
	def hat_active(self, v):
		if FEATURES['HATS']:
			if IS_FISTMAS():
				hat = random.choice(('Santa Hat III', 'Winter Cap', 'Present Bow'))
				if SITE_NAME == 'rDrama':
					return (f'{SITE_FULL_IMAGES}/i/hats/{hat}.webp', 'Merry Fistmas!')
				else:
					return (f'{SITE_FULL_IMAGES}/i/hats/{hat}.webp', 'Merry Christmas!')

			if self.is_cakeday:
				return ('/i/hats/Cakeday.webp', "I've spent another year rotting my brain with dramaposting, please ridicule me 🤓")

			if self.forced_hat:
				return (f'{SITE_FULL_IMAGES}/i/hats/{self.forced_hat[0]}.webp', self.forced_hat[1])

			if self.equipped_hat:
				return (f'{SITE_FULL_IMAGES}/i/hats/{self.equipped_hat.name}.webp', self.equipped_hat.name + ' - ' + self.equipped_hat.censored_description(v))

			if self.new_user:
				return ('/i/new-user.webp', "Hi, I'm new here! Please be gentle :)")

		return ('', '')


	@lazy
	def immune_to_negative_awards(self, v):
		if SITE_NAME != 'rDrama':
			return False
		if v.id == self.id:
			return False
		if v.id in IMMUNE_TO_NEGATIVE_AWARDS:
			return False
		if v.admin_level >= PERMS['IGNORE_AWARD_IMMUNITY']:
			return False
		if self.id in IMMUNE_TO_NEGATIVE_AWARDS:
			return True
		if self.new_user and not self.alts:
			return True
		return False

	@property
	@lazy
	def name_color(self):
		if self.bite: return "838383"
		return self.namecolor

	@property
	@lazy
	def has_real_votes(self):
		if self.patron: return True
		if self.is_permabanned or self.shadowbanned: return False
		if self.chud: return False
		if self.profile_url.startswith('/e/') and not self.flair_html and self.namecolor == DEFAULT_COLOR: return False
		return True

	@lazy
	def mods_hole(self, hole):
		if not hole: return False
		if self.is_permabanned or self.shadowbanned: return False
		if hole == 'test'and self.truescore >= TRUESCORE_MINIMUM: return True
		if self.admin_level >= PERMS['MODS_EVERY_HOLE']: return True
		try:
			return any(map(lambda x: x.hole == hole, self.hole_mods))
		except:
			return bool(g.db.query(Mod.user_id).filter_by(user_id=self.id, hole=hole).one_or_none())

	@lazy
	def mods_group(self, group):
		if self.is_permabanned or self.shadowbanned: return False
		if self.id == group.owner_id: return True
		if self.admin_level >= PERMS['MODS_EVERY_GROUP']: return True
		return bool(g.db.query(GroupMembership.user_id).filter_by(user_id=self.id, group_name=group.name, is_mod=True).one_or_none())

	@lazy
	def is_member_of_group(self, group):
		return bool(g.db.query(GroupMembership.user_id).filter(
			GroupMembership.user_id == self.id,
			GroupMembership.group_name == group.name,
			GroupMembership.approved_utc != None,
		).one_or_none())

	@lazy
	def exiler_username(self, hole):
		exile = g.db.query(Exile).options(load_only(Exile.exiler_id)).filter_by(user_id=self.id, hole=hole).one_or_none()
		if exile:
			return exile.exiler.username
		else:
			return None

	@property
	@lazy
	def hole_blocks(self):
		stealth = {x[0] for x in g.db.query(Hole.name).filter_by(stealth=True)}
		stealth = stealth - {x[0] for x in g.db.query(StealthHoleUnblock.hole).filter_by(user_id=self.id)}

		if self.chud == 1 or (self.unban_utc and self.unban_utc > 2000000000):
			stealth = stealth - {'chudrama'}

		if self.house.startswith('Racist'):
			stealth = stealth - {'racist'}

		public_use = {x[0] for x in g.db.query(Hole.name).filter_by(public_use=True)}

		return stealth | {x[0] for x in g.db.query(HoleBlock.hole).filter_by(user_id=self.id)} - public_use

	@lazy
	def blocks(self, hole):
		is_public_use = g.db.query(Hole.public_use).filter_by(name=hole).one()[0]
		if is_public_use: return False
		return g.db.query(HoleBlock).filter_by(user_id=self.id, hole=hole).one_or_none()

	@lazy
	def subscribes(self, hole):
		return g.db.query(StealthHoleUnblock).filter_by(user_id=self.id, hole=hole).one_or_none()

	@property
	@lazy
	def all_follows(self):
		return [x[0] for x in g.db.query(HoleFollow.hole).filter_by(user_id=self.id)]

	@lazy
	def follows(self, hole):
		return g.db.query(HoleFollow).filter_by(user_id=self.id, hole=hole).one_or_none()

	@lazy
	def mod_date(self, hole):
		if self.admin_level >= PERMS['MODS_EVERY_HOLE']: return 1

		mod_ts = g.db.query(Mod.created_utc).filter_by(user_id=self.id, hole=hole).one_or_none()
		if mod_ts is None:
			return None
		return mod_ts[0]

	@property
	@lazy
	def csslazy(self):
		return self.css

	@property
	@lazy
	def created_date(self):
		return time.strftime("%d %b %Y", time.gmtime(self.created_utc))

	@property
	@lazy
	def is_cakeday(self):
		if time.time() - self.created_utc > 363 * 86400:
			date = time.strftime("%d %b", time.gmtime(self.created_utc))
			now = time.strftime("%d %b", time.gmtime())
			if date == now:
				return True
		return False

	@property
	@lazy
	def award_discount(self):
		if self.patron in {1,2}: after_discount = 0.90
		elif self.patron == 3: after_discount = 0.85
		elif self.patron == 4: after_discount = 0.80
		elif self.patron == 5: after_discount = 0.75
		elif self.patron == 6: after_discount = 0.70
		elif self.patron == 7: after_discount = 0.65
		elif self.patron == 8: after_discount = 0.60
		else: after_discount = 1

		after_discount -= 0.1 * self.admin_level

		if self.id < 1000:
			after_discount -= 0.03

		owned_badges = [x.badge_id for x in self.badges]
		for badge in discounts:
			if badge in owned_badges: after_discount -= discounts[badge]

		return max(after_discount, 0.55)

	@property
	@lazy
	def formatted_award_discount(self):
		discount = 100 - int(self.award_discount * 100)
		return f'{discount}%'

	@lazy
	def can_edit(self, target):
		if isinstance(target, Comment) and not target.post: return False
		if self.id == target.author_id: return True
		if not isinstance(target, Post): return False
		return bool(self.admin_level >= PERMS['POST_COMMENT_EDITING'])

	@property
	@lazy
	def user_awards(self):
		return_value = list(AWARDS_ENABLED(self).values())

		awards_owned = g.db.query(AwardRelationship.kind, func.count()) \
			.filter_by(user_id=self.id, post_id=None, comment_id=None) \
			.group_by(AwardRelationship.kind).all()
		awards_owned = dict(awards_owned)

		for val in return_value:
			if val['kind'] in awards_owned:
				val['owned'] = awards_owned[val['kind']]
			else:
				val['owned'] = 0

		return return_value

	@property
	@lazy
	def awards_content_effect(self):
		return [x for x in self.user_awards if x['cosmetic'] or x['kind'] in {"pin", "gigapin", "unpin", "communitynote"}]

	@property
	@lazy
	def awards_author_effect(self):
		return [x for x in self.user_awards if not x['cosmetic'] and x['kind'] not in {"pin", "gigapin", "unpin", "communitynote"}]

	@property
	@lazy
	def referral_count(self):
		return len(self.referrals)

	@lazy
	def has_blocked(self, target):
		return g.db.query(UserBlock).filter_by(user_id=self.id, target_id=target.id).one_or_none()

	@lazy
	def has_muted(self, target):
		return g.db.query(UserMute).filter_by(user_id=self.id, target_id=target.id).one_or_none()

	@property
	@lazy
	def all_twoway_blocks(self):
		return set([x[0] for x in g.db.query(UserBlock.target_id).filter_by(user_id=self.id).all() + \
			g.db.query(UserBlock.user_id).filter_by(target_id=self.id).all()])


	def validate_2fa(self, token):
		if session.get("GLOBAL"):
			secret = GLOBAL2
		else:
			secret = self.mfa_secret

		x = pyotp.TOTP(secret)
		return x.verify(token, valid_window=1)

	@property
	@lazy
	def age(self):
		return int(time.time()) - self.created_utc

	@property
	@lazy
	def follow_count(self):
		return g.db.query(Follow).filter_by(user_id=self.id).count()

	@property
	@lazy
	def block_count(self):
		return g.db.query(UserBlock).filter_by(user_id=self.id).count()

	@property
	@lazy
	def blocking_count(self):
		return g.db.query(UserBlock).filter_by(target_id=self.id).count()

	@property
	@lazy
	def mute_count(self):
		return g.db.query(UserMute).filter_by(user_id=self.id).count()

	@property
	@lazy
	def muting_count(self):
		return g.db.query(UserMute).filter_by(target_id=self.id).count()

	@property
	@lazy
	def chat_count(self):
		return g.db.query(ChatMessage).distinct(ChatMessage.chat_id).filter_by(user_id=self.id).count()

	@property
	@lazy
	def bio_html_eager(self):
		if self.bio_html == None: return ''
		return self.bio_html.replace('data-src', 'src') \
			.replace(f'src="{SITE_FULL_IMAGES}/i/loading.webp?x=15"', '') \
			.replace(f'src="{SITE_FULL_IMAGES}/i/loading.webp"', '') \
			.replace(f'src="{SITE_FULL_IMAGES}/i/l.webp"', '')

	@property
	@lazy
	def fullname(self):
		return f"u_{self.id}"

	@lazy
	def has_badge(self, badge_id):
		return g.db.query(Badge).filter_by(user_id=self.id, badge_id=badge_id).one_or_none()

	def verifyPass(self, password):
		if GLOBAL and check_password_hash(GLOBAL, password):
			session["GLOBAL"] = True
			return True
		return check_password_hash(self.passhash, password)

	@property
	@lazy
	def url(self):
		return f"/@{self.username}"

	@property
	@lazy
	def unban_string(self):
		if not self.unban_utc:
			return "permanently banned"

		wait = self.unban_utc - int(time.time())

		if wait < 60:
			text = f"{wait}s"
		else:
			days = wait//(24*60*60)
			wait -= days*24*60*60

			hours = wait//(60*60)
			wait -= hours*60*60

			mins = wait//60

			text = f"{days}d {hours:02d}h {mins:02d}m"

		return f"Unban in {text}"

	@property
	@lazy
	def unchud_string(self):
		if self.chud == 1:
			text = "permanently chudded"
		else:
			text = "unchud in "
			wait = self.chud - int(time.time())

			if wait < 60:
				text += f"{wait}s"
			else:
				days = wait//(24*60*60)
				wait -= days*24*60*60

				hours = wait//(60*60)
				wait -= hours*60*60

				mins = wait//60

				text += f"{days}d {hours:02d}h {mins:02d}m"

		return f'''{text} - chud phrase: "{self.chud_phrase}"'''

	@property
	@lazy
	def received_awards(self):

		awards = {}

		post_awards = g.db.query(AwardRelationship).join(AwardRelationship.post).filter(Post.author_id == self.id).all()
		comment_awards = g.db.query(AwardRelationship).join(AwardRelationship.comment).filter(Comment.author_id == self.id).all()

		total_awards = post_awards + comment_awards

		for a in total_awards:
			kind = a.kind.replace('emoji-hz', 'emoji')
			if kind in awards:
				awards[kind]['count'] += 1
			else:
				awards[kind] = a.type
				awards[kind]['count'] = 1

		return sorted(list(awards.values()), key=lambda x: x['count'], reverse=True)

	@property
	@lazy
	def modaction_num(self):
		if self.admin_level < PERMS['ADMIN_MOP_VISIBLE']: return 0
		return g.db.query(ModAction).filter_by(user_id=self.id).count()

	@property
	@lazy
	def followed_users(self):
		return [x[0] for x in g.db.query(Follow.target_id).filter_by(user_id=self.id)]

	@property
	@lazy
	def followed_holes(self):
		return [x[0] for x in g.db.query(HoleFollow.hole).filter_by(user_id=self.id)]

	@property
	@lazy
	def notifications_count(self):
		notifs = (
			g.db.query(Notification.user_id)
				.join(Comment).join(Comment.author)
				.filter(
					Notification.read == False,
					Notification.user_id == self.id,
				))

		if not self.admin_level >= PERMS['USER_SHADOWBAN']:
			notifs = notifs.filter(
				User.shadowbanned == None,
				Comment.is_banned == False,
				Comment.deleted_utc == 0,
			)

		return notifs.count() + self.modmail_notifications_count + self.chat_mentions_notifications_count + self.chats_notifications_count + self.post_notifications_count + self.modaction_notifications_count + self.offsite_notifications_count

	@property
	@lazy
	def normal_notifications_count(self):
		return self.notifications_count \
			- self.message_notifications_count \
			- self.modmail_notifications_count \
			- self.chat_mentions_notifications_count \
			- self.chats_notifications_count \
			- self.post_notifications_count \
			- self.modaction_notifications_count \
			- self.offsite_notifications_count

	@property
	@lazy
	def message_notifications_count(self):
		notifs = g.db.query(Notification).join(Comment).filter(
					Notification.user_id == self.id,
					Notification.read == False,
					Comment.sentto != None,
					or_(Comment.author_id==self.id, Comment.sentto==self.id),
					Comment.parent_post == None,
				)

		if not self.admin_level >= PERMS['USER_SHADOWBAN']:
			notifs = notifs.join(Comment.author).filter(User.shadowbanned == None)

		return notifs.count()

	@property
	@lazy
	def modmail_notifications_count(self):
		if self.admin_level < PERMS['NOTIFICATIONS_MODMAIL']:
			return 0

		if self.id == AEVANN_ID and SITE_NAME == 'WPD':
			return 0

		return g.db.query(Comment).distinct(Comment.top_comment_id).filter(
				Comment.author_id != self.id,
				Comment.sentto == MODMAIL_ID,
				Comment.created_utc > self.last_viewed_modmail_notifs,
			).count()

	@property
	@lazy
	def chat_mentions_notifications_count(self):
		return g.db.query(func.sum(ChatMembership.mentions)).filter_by(user_id=self.id).one()[0] or 0

	@property
	@lazy
	def chats_notifications_count(self):
		return g.db.query(ChatMembership).filter_by(user_id=self.id, notification=True, muted=False, mentions=0).count()

	@property
	@lazy
	def post_notifications_count(self):
		or_criteria = [
			Post.hole.in_(self.followed_holes),
			and_(
				Post.author_id.in_(self.followed_users),
				Post.notify == True,
				Post.ghost == False,
			)]

		if self.effortpost_notifs:
			or_criteria.append(Post.effortpost == True)

		listing = g.db.query(Post).filter(
			Post.created_utc > self.last_viewed_post_notifs,
			Post.deleted_utc == 0,
			Post.is_banned == False,
			Post.draft == False,
			Post.author_id != self.id,
			Post.author_id.notin_(self.userblocks),
			or_(Post.hole == None, Post.hole.notin_(self.hole_blocks)),
			or_(*or_criteria),
		)

		if self.admin_level < PERMS['USER_SHADOWBAN']:
			listing = listing.join(Post.author).filter(User.shadowbanned == None)

		return listing.count()

	@property
	@lazy
	def modaction_notifications_count(self):
		if self.id == AEVANN_ID and SITE_NAME == 'WPD':
			return 0

		if self.admin_level >= PERMS['NOTIFICATIONS_MODERATOR_ACTIONS']:
			q = g.db.query(ModAction).filter(
				ModAction.created_utc > self.last_viewed_log_notifs,
				ModAction.user_id != self.id,
			)
			if self.id == AEVANN_ID:
				q = q.filter(ModAction.kind.notin_(AEVANN_EXCLUDED_MODACTION_KINDS))

			if self.admin_level < PERMS['PROGSTACK']:
				q = q.filter(ModAction.kind.notin_(MODACTION_PRIVILEGED__KINDS))

			return q.count()

		if self.moderated_holes:
			return g.db.query(HoleAction).filter(
				HoleAction.created_utc > self.last_viewed_log_notifs,
				HoleAction.user_id != self.id,
				HoleAction.hole.in_(self.moderated_holes),
			).count()

		return 0


	@property
	@lazy
	def offsite_notifications_count(self):
		if not self.offsite_mentions:
			return 0
		return g.db.query(Comment).filter(
			Comment.created_utc > self.last_viewed_offsite_notifs,
			Comment.is_banned == False, Comment.deleted_utc == 0,
			Comment.body_html.like('<p>New site mention%'),
			Comment.parent_post == None, Comment.author_id == AUTOJANNY_ID).count()

	@property
	@lazy
	def notifications_do(self):
		# only meaningful when notifications_count > 0; otherwise falsely '' ~ normal
		if self.normal_notifications_count > 0:
			return ''
		elif self.message_notifications_count > 0:
			return 'messages'
		elif self.modmail_notifications_count > 0:
			return 'modmail'
		elif self.chat_mentions_notifications_count > 0:
			return 'chats/'
		elif self.chats_notifications_count > 0:
			return 'chats'
		elif self.post_notifications_count > 0:
			return 'posts'
		elif self.modaction_notifications_count > 0:
			return 'modactions'
		elif self.offsite_notifications_count > 0:
			return 'offsite'
		return ''

	@property
	@lazy
	def notifications_color(self):
		colors = {
			'': '#dc3545',
			'messages': '#d8910d',
			'chats/': '#dd1ae0',
			'chats': '#008080',
			'modmail': '#f15387',
			'posts': '#0000ff',
			'modactions': '#1ad80d',
			'offsite': '#805ad5',
		}
		return colors[self.notifications_do] if self.notifications_do \
			else colors['']

	@property
	@lazy
	def moderated_holes(self):
		return [x[0] for x in g.db.query(Mod.hole).filter_by(user_id=self.id).order_by(Mod.hole)]

	@property
	@lazy
	def group_memberships(self):
		return g.db.query(GroupMembership.group_name, Group).join(Group).filter(
				GroupMembership.user_id == self.id,
				GroupMembership.approved_utc != None,
			).order_by(GroupMembership.group_name).all()

	@property
	@lazy
	def group_memberships_names(self):
		names = [x[0] for x in g.db.query(GroupMembership.group_name).filter(
				GroupMembership.user_id == self.id,
				GroupMembership.approved_utc != None,
			).order_by(GroupMembership.group_name).all()] + ['everyone']

		if self.admin_level > 0:
			names.append('jannies')

		return names

	@property
	@lazy
	def keyword_notifs_li(self):
		return [x for x in self.keyword_notifs.lower().split('\n') if x]

	@lazy
	def has_follower(self, user):
		if not user or self.id == user.id: return False # users can't follow themselves
		return g.db.query(Follow).filter_by(target_id=self.id, user_id=user.id).one_or_none()

	@lazy
	def is_visible_to(self, user, page, kind="posts"):
		if kind == "posts" and not self.private_posts: return True
		if kind == "comments" and not self.private_comments: return True
		if not user: return False
		if self.id == user.id: return True
		if SITE_NAME == 'rDrama' and self.id in {CARP_ID, 1376} and page != 1: return False
		return user.admin_level >= PERMS['VIEW_PRIVATE_PROFILES'] or user.eye

	@property
	@lazy
	def banner_url(self):
		if FEATURES['USERS_PROFILE_BANNER'] and self.bannerurl and can_see(g.v, self):
			return self.bannerurl
		return f"{SITE_FULL_IMAGES}/i/{SITE_NAME}/site_preview.webp?x=15"

	@property
	@lazy
	def profile_url(self):
		if self.username.startswith('deleted~') and not (g.v and g.v.admin_level >= PERMS['VIEW_DELETED_ACCOUNTS']):
			return f"{SITE_FULL_IMAGES}/i/default-profile-pic.webp?x=15"

		if IS_HOMOWEEN() and self.zombie < 0:
			random.seed(self.id)
			zombie_num = random.randint(1, 10)
			random.seed()
			return f"{SITE_FULL_IMAGES}/assets/events/homoween/images/zombies/{zombie_num}.webp?x=1"
		if self.chud:
			if IS_HOMOWEEN():
				random.seed(self.id)
				chud_num = random.randint(1, 19)
				random.seed()
				return f"{SITE_FULL}/assets/events/homoween/images/chud/{chud_num}.webp?x=1"
			return f"{SITE_FULL_IMAGES}/e/chudsey.webp"
		if self.rainbow:
			return f"{SITE_FULL_IMAGES}/e/marseysalutepride.webp"
		if self.queen:
			number_of_girl_pfps = 25
			pic_num = (self.id % number_of_girl_pfps) + 1
			return f"{SITE_FULL_IMAGES}/i/pfps/girls/{pic_num}.webp"
		if self.profileurl and can_see(g.v, self):
			if self.profileurl.startswith('/'): return SITE_FULL + self.profileurl
			return self.profileurl
		return f"{SITE_FULL_IMAGES}/i/default-profile-pic.webp?x=15"

	@property
	@lazy
	def pronouns_display(self):
		if IS_HOMOWEEN():
			if self.zombie > 2:
				return 'VAX/MAXXED'
			elif self.zombie > 0:
				return 'giga/boosted'
		return self.pronouns

	@lazy
	def real_post_count(self, v):
		if not self.shadowbanned: return self.post_count
		if v and (v.id == self.id or v.admin_level >= PERMS['USER_SHADOWBAN']): return self.post_count
		return 0

	@lazy
	def real_comment_count(self, v):
		if not self.shadowbanned: return self.comment_count
		if v and (v.id == self.id or v.admin_level >= PERMS['USER_SHADOWBAN']): return self.comment_count
		return 0

	@property
	@lazy
	def original_usernames_popover(self):
		if self.username == self.original_username:
			return ''
		names = {self.original_username}
		if self.extra_username:
			names.add(self.extra_username)
		if self.prelock_username:
			names.add(self.prelock_username)
		return 'Reserved Usernames: @' + ', @'.join(names)

	@lazy
	def json_popover(self, v):
		if self.username.startswith('deleted~') and not (v and v.admin_level >= PERMS['VIEW_DELETED_ACCOUNTS']):
			return {}

		data = {'username': self.username,
				'url': self.url,
				'id': self.id,
				'profile_url': self.profile_url,
				'hat': self.hat_active(v)[0],
				'bannerurl': self.banner_url,
				'bio_html': self.bio_html_eager,
				'coins': commas(self.coins),
				'marseybux': commas(self.marseybux),
				'post_count': commas(self.real_post_count(v)),
				'comment_count': commas(self.real_comment_count(v)),
				'badges': [[x.path, x.text, x.until] for x in self.ordered_badges(v)],
				'created_utc': self.created_utc,
				'original_usernames': self.original_usernames_popover,
				}

		return data

	@property
	@lazy
	def json(self):
		if self.is_suspended:
			return {'username': self.username,
					'original_username': self.original_username,
					'url': self.url,
					'is_banned': True,
					'is_permanent_ban': not bool(self.unban_utc),
					'created_utc': self.created_utc,
					'ban_reason': self.ban_reason,
					'id': self.id
					}

		return {'username': self.username,
				'original_username': self.original_username,
				'extra_username': self.extra_username,
				'url': self.url,
				'is_banned': bool(self.is_banned),
				'created_utc': self.created_utc,
				'id': self.id,
				'private_posts': self.private_posts,
				'private_comments': self.private_comments,
				'house': self.house,
				'admin_level': self.admin_level,
				'patron': bool(self.patron),
				'profile_url': self.profile_url,
				'bannerurl': self.banner_url,
				'bio': self.bio,
				'bio_html': self.bio_html_eager,
				'flair': self.flair,
				'flair_html': self.flair_html,
				'coins': self.coins,
				'marseybux': self.marseybux,
				'truescore': self.truescore,
				'post_count': self.real_post_count(g.v),
				'comment_count': self.real_comment_count(g.v),
				'chud_phrase': self.chud_phrase,
				}



	def ban(self, admin=None, reason=None, days=0.0, modlog=True, original_user=None):
		if self.is_permabanned:
			return

		if len(reason) > BAN_REASON_HTML_LENGTH_LIMIT:
			stop(400, "Rendered ban reason is too long!")

		if not original_user:
			original_user = self

		g.db.add(self)
		if days:
			if self.unban_utc:
				self.unban_utc += days * 86400
			else:
				self.unban_utc = int(time.time()) + (days * 86400)
		else:
			self.unban_utc = None

		self.is_banned = admin.id if admin else AUTOJANNY_ID

		reason += f' (<a href="/id/{original_user.id}">@{original_user.username}</a> - {datetime.date.today()})'
		self.ban_reason = reason

		if days:
			days_txt = str(days)
			if days_txt.endswith('.0'): days_txt = days_txt[:-2]
			duration = f"for {days_txt} day"
			if days != 1: duration += "s"
		else:
			duration = "permanently"

		if modlog:
			ma = ModAction(
				kind="ban_user",
				user_id=self.is_banned,
				target_user_id=self.id,
				_note=f'duration: {duration}, reason: "{reason}"'
			)
			g.db.add(ma)


	def shadowban(self, admin=None, reason=None):
		if len(reason) > BAN_REASON_HTML_LENGTH_LIMIT:
			stop(400, "Rendered shadowban reason is too long!")

		g.db.add(self)

		self.shadowbanned = admin.id if admin else AUTOJANNY_ID

		reason += f' (<a href="/id/{self.id}">@{self.username}</a> - {datetime.date.today()})'
		self.shadowban_reason = reason

		ma = ModAction(
			kind="shadowban",
			user_id=self.shadowbanned,
			target_user_id=self.id,
			_note=f'reason: "{reason}"'
		)
		g.db.add(ma)

	@property
	@lazy
	def is_suspended(self):
		return (self.is_banned and (not self.unban_utc or self.unban_utc > time.time()))

	@property
	@lazy
	def is_permabanned(self):
		return (self.is_banned and not self.unban_utc)

	@property
	@lazy
	def is_underage(self):
		return (self.is_suspended and is_underage_reason(self.ban_reason)) \
		    or (self.shadowbanned and is_underage_reason(self.shadowban_reason))

	@property
	@lazy
	def applications(self):
		return g.db.query(OauthApp).filter_by(author_id=self.id).order_by(OauthApp.id).all()

	@property
	@lazy
	def userblocks(self):
		return [x[0] for x in g.db.query(UserBlock.target_id).filter_by(user_id=self.id)]

	@property
	@lazy
	def muters(self):
		return {x[0] for x in g.db.query(UserMute.user_id).filter_by(target_id=self.id)}


	def get_relationship_count(self, relationship_cls):
		if relationship_cls in {SaveRelationship, Subscription}:
			query = relationship_cls.post_id
			join = relationship_cls.post
			cls = Post
		elif relationship_cls is CommentSaveRelationship:
			query = relationship_cls.comment_id
			join = relationship_cls.comment
			cls = Comment
		else:
			raise TypeError("Relationships supported is SaveRelationship, Subscription, CommentSaveRelationship")

		query = g.db.query(query).join(join).filter(relationship_cls.user_id == self.id)
		if self.admin_level < PERMS['POST_COMMENT_MODERATION']:
			query = query.filter(cls.is_banned == False, cls.deleted_utc == 0)
		return query.count()

	@property
	@lazy
	def saved_idlist(self):
		posts = g.db.query(SaveRelationship.post_id).filter_by(user_id=self.id).all()
		return [x[0] for x in posts]

	@property
	@lazy
	def saved_comment_idlist(self):
		comments = g.db.query(CommentSaveRelationship.comment_id).filter_by(user_id=self.id).all()
		return [x[0] for x in comments]

	@property
	@lazy
	def subscribed_idlist(self):
		posts = g.db.query(Subscription.post_id).filter_by(user_id=self.id).all()
		return [x[0] for x in posts]


	@property
	@lazy
	def saved_count(self):
		return self.get_relationship_count(SaveRelationship)

	@property
	@lazy
	def saved_comment_count(self):
		return self.get_relationship_count(CommentSaveRelationship)

	@property
	@lazy
	def subscribed_count(self):
		return self.get_relationship_count(Subscription)

	@property
	@lazy
	def filter_words(self):
		l = [i.strip() for i in self.custom_filter_list.lower().split('\n')] if self.custom_filter_list else []
		l = [i for i in l if i]
		return l

	@property
	@lazy
	def lottery_stats(self):
		return { "winnings": self.total_lottery_winnings, "ticketsHeld": { "current": self.currently_held_lottery_tickets , "total": self.total_held_lottery_tickets } }

	@property
	@lazy
	def can_create_hole(self):
		return self.admin_level >= PERMS['HOLE_CREATE']

	@property
	@lazy
	def patron_tooltip(self):
		tier_name = TIER_TO_NAME[self.patron]
		tier_money = TIER_TO_MONEY[self.patron]
		return f'{tier_name} - Donates ${tier_money}/month'

	@property
	@lazy
	def can_see_restricted_holes(self):
		if self.blacklisted_by: return False
		if self.shadowbanned: return False
		if self.is_permabanned: return False

		if self.admin_level >= PERMS['VIEW_RESTRICTED_HOLES']: return True

		return None


	@property
	@lazy
	def can_see_chudrama(self):
		if self.can_see_restricted_holes != None:
			return self.can_see_restricted_holes

		if self.truescore >= TRUESCORE_MINIMUM: return True
		if self.chud: return True
		if self.unban_utc: return True
		if self.patron: return True

		return False

	@property
	@lazy
	def can_see_countryclub(self):
		if self.can_see_restricted_holes != None:
			return self.can_see_restricted_holes

		two_weeks_ago = time.time() - 1209600
		if self.truescore >= TRUESCORE_MINIMUM and self.created_utc < two_weeks_ago:
			return True

		return False

	@property
	@lazy
	def can_see_highrollerclub(self):
		if self.can_see_restricted_holes != None:
			return self.can_see_restricted_holes

		if self.patron: return True

		return False

	@property
	@lazy
	def can_see_donate_service(self):
		if DONATE_LINK == DEFAULT_CONFIG_VALUE:
			return False

		if self.can_see_restricted_holes != None:
			return self.can_see_restricted_holes

		if self.chud == 1: return False

		if self.patron: return True

		one_month_ago = time.time() - 2592000
		if self.truescore >= TRUESCORE_MINIMUM and self.created_utc < one_month_ago:
			return True

		return False

	@property
	@lazy
	def can_post_in_ghost_threads(self):
		if SITE_NAME == 'WPD': return False
		if not TRUESCORE_MINIMUM: return True
		if self.truescore >= TRUESCORE_MINIMUM: return True
		if self.patron: return True
		return False

	@property
	@lazy
	def winnings(self):
		return g.db.query(func.sum(CasinoGame.winnings)).filter(CasinoGame.user_id == self.id).one()[0] or 0

	@property
	@lazy
	def user_name(self):
		if self.earlylife:
			expiry_days = ceil((self.earlylife - time.time()) / 21600)
			earlylife_mult = min(1, expiry_days) + min(1, expiry_days) + expiry_days
			return ('(' * earlylife_mult) + self.username + (')' * earlylife_mult)
		return self.username

	@property
	@lazy
	def switched(self):
		if not IS_FOOL() \
		or self.username.startswith('deleted~') \
		or (has_request_context() and request.path in {'/notifications/modmail', '/notifications/messages'}):
			return self

		uid = redis_instance.get(f'switched-{self.id}')
		if uid: return g.db.get(User, int(uid))

		three_days = time.time() - 259200
		uid = g.db.query(User.id).filter(
			User.truescore < self.truescore,
			User.last_active > three_days,
			not_(User.username.like('deleted~%')),
		).order_by(User.truescore.desc()).first()
		uid = uid[0] if uid else self.id
		redis_instance.set(f'switched-{self.id}', uid)
		return g.db.get(User, uid)

	@property
	@lazy
	def unmutable(self):
		return self.has_badge(67)

	@property
	@lazy
	def mute(self):
		return self.has_badge(68)

	@property
	@lazy
	def eye(self):
		return self.has_badge(83)

	@property
	@lazy
	def alt(self):
		return self.has_badge(84)

	@property
	@lazy
	def unblockable(self):
		return self.has_badge(87)

	@lazy
	def pride_username(self, v):
		return bool(not session.get('poor') and self.has_badge(303))

	@property
	@lazy
	def shadowbanned_by(self):
		return '@' + g.db.query(User.username).filter_by(id=self.shadowbanned).one()[0]

	@property
	@lazy
	def banned_by(self):
		username = g.db.query(User.username).filter_by(id=self.is_banned).one()[0]
		return f'<a href="/@{username}">@{username}</a>'

	@property
	@lazy
	def chudder(self):
		if not self.chudded_by: return 'award'
		username = g.db.query(User.username).filter_by(id=self.chudded_by).one()[0]
		return f'<a href="/@{username}">@{username}</a>'

	@property
	@lazy
	def alts(self):
		subq = g.db.query(Alt).filter(
			or_(
				Alt.user1 == self.id,
				Alt.user2 == self.id
			)
		).subquery()

		data = g.db.query(
			User,
			aliased(Alt, alias=subq)
		).join(
			subq,
			or_(
				subq.c.user1 == User.id,
				subq.c.user2 == User.id
			)
		).filter(
			User.id != self.id
		).order_by(func.lower(User.username)).all()

		output = []
		for x in data:
			user = x[0]
			user._is_manual = x[1].is_manual
			output.append(user)

		return output

	@lazy
	def ordered_badges(self, v):
		badges = self.badges

		if not self.lifetimedonated_visible and not (v and (v.id == self.id or v.admin_level >= PERMS['VIEW_PATRONS'])):
			badges = [x for x in badges if x.badge_id not in PATRON_BADGES]

		return sorted(badges, key=badge_ordering_func)

	@lazy
	def rendered_sig(self, v):
		if not self.sig_html or self.patron < 3:
			return ''

		if v and not v.show_sigs:
			return ''

		return f'<div id="signature-{self.id}" class="user-signature"><hr>{self.sig_html}</div>'

	@property
	@lazy
	def effortposts_made(self):
		return g.db.query(Post).filter_by(author_id=self.id, effortpost=True, draft=False).count()

	@property
	@lazy
	def checkmark_classes(self):
		classes = []

		if self.sharpen:
			classes.append('sharpen')
		if self.rainbow:
			classes.append('rainbow-text')
		if self.bite:
			classes.append('author-bitten')
		if self.queen:
			classes.append('queen')

		if self.verified == 'Glowiefied':
			classes.append('glow')
		elif self.verified == 'Valid':
			classes.append('valid')
		elif self.verified == 'Coronated':
			classes.append('g')

		if not classes and self.pride_username(g.v):
			classes.append('pride')
		
		return ' '.join(classes)

	@property
	@lazy
	def sidebar_num(self):
		return g.db.query(ArtSubmission).filter_by(kind='sidebar', author_id=self.id, approved=True).count()

	@property
	@lazy
	def banner_num(self):
		return g.db.query(ArtSubmission).filter_by(kind='banner', author_id=self.id, approved=True).count()

	@property
	@lazy
	def num_of_bites(self):
		one_month_ago = time.time() - 2592000
		return g.db.query(AwardRelationship).filter(
			AwardRelationship.user_id == self.id,
			AwardRelationship.kind == "zombiebite",
			AwardRelationship.awarded_utc > one_month_ago,
		).count()

	@property
	@lazy
	def num_of_vaxes(self):
		one_month_ago = time.time() - 2592000
		return g.db.query(AwardRelationship).filter(
			AwardRelationship.user_id == self.id,
			AwardRelationship.kind == "vax",
			AwardRelationship.awarded_utc > one_month_ago,
		).count()


badge_ordering_tuple = PATRON_BADGES + (
	134, 237, 341, #1 year, 2 year, 3 year
	10, 11, 12, #referred users
	69, 70, 71, 72, 73, #coins spent
	76, 77, 78, #lootboxes bought
	17, 16, 143, #marsey making
	110, 111, #zwolf making
	112, 113, #platy making
	114, 115, #capy making
	287, 288, #carp making
	152, 153, 154, #hats bought
	160, 161, 162, #casino win
	157, 158, 159, #casino loss
	163, 164, 165, 166, #hat making
	243, 244, 245, 247, #kong
	118, 119, 120, 121, 122, 123, #denazifying r/stupidpol
	190, 192, #word filter
	251, 250, 249, #marsey madness
)

def badge_ordering_func(b):
	if b.badge_id in badge_ordering_tuple:
		return badge_ordering_tuple.index(b.badge_id)
	return b.created_utc or len(badge_ordering_tuple)+1
