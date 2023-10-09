import random
import time
from urllib.parse import quote
from sqlalchemy.sql import func
import gevent
import requests
from flask import g

from files.classes.reports import Report
from files.classes.mod_logs import ModAction
from files.classes.notifications import Notification
from files.classes.polls import CommentOption, PostOption
from files.classes.award import AwardRelationship
from files.classes.exiles import Exile

from files.helpers.alerts import send_repeatable_notification, push_notif
from files.helpers.config.const import *
from files.helpers.config.awards import AWARDS
from files.helpers.const_stateful import *
from files.helpers.get import *
from files.helpers.logging import log_file
from files.helpers.sanitize import *
from files.helpers.settings import get_setting
from files.helpers.slots import check_slots_command

from files.routes.routehelpers import check_for_alts

def _archiveorg(url):
	try:
		requests.post('https://ghostarchive.org/archive2', data={"archive": url}, headers=HEADERS, timeout=10, proxies=proxies)
	except: pass
	try:
		requests.get(f'https://web.archive.org/save/{url}', headers=HEADERS, timeout=10, proxies=proxies)
	except: pass


def archive_url(url):
	gevent.spawn(_archiveorg, url)
	if url.startswith('https://twitter.com/'):
		url = url.replace('https://twitter.com/', 'https://nitter.net/')
		gevent.spawn(_archiveorg, url)
	if url.startswith('https://instagram.com/'):
		url = url.replace('https://instagram.com/', 'https://imginn.com/')
		gevent.spawn(_archiveorg, url)

def snappy_report(post, reason):
	report = Report(post_id=post.id, user_id=SNAPPY_ID, reason=reason)
	g.db.add(report)
	message = f'@Snappy reported [{post.title}]({post.shortlink})\n\n> {reason}'
	send_repeatable_notification(post.author_id, message)

def execute_snappy(post, v):
	if post.hole and g.db.query(Exile.user_id).filter_by(user_id=SNAPPY_ID, hole=post.hole).one_or_none():
		return

	ghost = post.ghost

	snappy = get_account(SNAPPY_ID)

	ping_cost = 0

	post_ping_group_count = len(list(group_mention_regex.finditer(post.body)))

	if post_ping_group_count > 3:
		body = "Unnecessary and uncalled for ping :marseydownvotemad: two more strikes and you're getting blocked + megadownvoted buddy, don't test your luck"
		vote = Vote(user_id=SNAPPY_ID,
					vote_type=-1,
					post_id=post.id,
					real = True
					)
		g.db.add(vote)
		post.downvotes += 1
	elif v.id == CARP_ID:
		if random.random() < 0.08:
			body = random.choice(("i love you carp", "https://i.rdrama.net/images/16614707883108485.webp", "https://i.rdrama.net/images/1636916964YyM.webp", "https://youtube.com/watch?v=zRbQHTdsjuY", "https://i.rdrama.net/images/1696250281381682.webp"))
		elif IS_DKD():
			body = ":#donkeykongfuckoffcarp:"
		elif IS_HOMOWEEN():
			body = "F̵̽̉U̷̓̕C̵̟̍K̴̾̍ ̵́̒O̶͐̇F̷͗̐F̴͛̄ ̸̆͠CARP"
		else:
			body = ":#marseyfuckoffcarp:"
	elif v.id == AEVANN_ID:
		body = "https://i.rdrama.net/images/16909380805064178.webp"
	elif v.id == LAWLZ_ID:
		if random.random() < 0.5: body = "wow, this lawlzpost sucks!"
		else: body = "wow, a good lawlzpost for once!"
	elif v.id == 253:
		body = "https://i.rdrama.net/images/16961715452780113.webp"
	else:
		if IS_DKD():
			SNAPPY_CHOICES = SNAPPY_KONGS
		elif IS_FISTMAS():
			SNAPPY_CHOICES = SNAPPY_QUOTES_FISTMAS
		elif IS_HOMOWEEN():
			SNAPPY_CHOICES = SNAPPY_QUOTES_HOMOWEEN
		elif SNAPPY_MARSEYS and SNAPPY_QUOTES:
			if random.random() > 0.5:
				SNAPPY_CHOICES = SNAPPY_QUOTES
			else:
				SNAPPY_CHOICES = SNAPPY_MARSEYS
		elif SNAPPY_MARSEYS:
			SNAPPY_CHOICES = SNAPPY_MARSEYS
		elif SNAPPY_QUOTES:
			SNAPPY_CHOICES = SNAPPY_QUOTES
		else:
			SNAPPY_CHOICES = [""]

		body = random.choice(SNAPPY_CHOICES).strip()
		if body.startswith('▼') or body.startswith(':#marseydownvote'):
			if body.startswith('▼'): body = body[1:]
			vote = Vote(user_id=SNAPPY_ID,
						vote_type=-1,
						post_id=post.id,
						real = True
						)
			g.db.add(vote)
			post.downvotes += 1
			if body.startswith('OP is a Trump supporter'):
				snappy_report(post, 'Trump supporter')
			elif body.startswith('You had your chance. Downvoted and reported'):
				snappy_report(post, 'Retard')
		elif body.startswith('▲') or body.startswith(':#marseyupvote'):
			if body.startswith('▲'): body = body[1:]
			vote = Vote(user_id=SNAPPY_ID,
						vote_type=1,
						post_id=post.id,
						real = True
						)
			g.db.add(vote)
			post.upvotes += 1
		elif body.startswith(':#marseyghost'):
			ghost = True
		elif body == '!slots':
			body = f'!slots{snappy.coins}'
		elif body == '!pinggroup':
			group = g.db.query(Group).order_by(func.random()).first()

			cost = len(group.member_ids) * 5
			snappy.charge_account('coins', cost)

			body = f'!{group.name}'

			ping_cost = cost
		elif body.startswith(':#marseyglow'):
			award_object = AwardRelationship(
					user_id=snappy.id,
					kind="glowie",
					post_id=post.id,
				)
			g.db.add(award_object)

			awarded_coins = int(AWARDS["glowie"]['price'] * COSMETIC_AWARD_COIN_AWARD_PCT) if AWARDS["glowie"]['cosmetic'] else 0
			if AWARDS["glowie"]['cosmetic']:
				post.author.pay_account('coins', awarded_coins)

			msg = f"@Snappy has given your [post]({post.shortlink}) the {AWARDS['glowie']['title']} Award"
			if awarded_coins > 0:
				msg += f" and you have received {awarded_coins} coins as a result"
			msg += "!"
			send_repeatable_notification(post.author.id, msg)


	body += "\n\n"

	if post.url and not post.url.startswith('/') and not post.url.startswith(f'{SITE_FULL}/') and not post.url.startswith(SITE_FULL_IMAGES):
		if post.url.startswith('https://old.reddit.com/r/'):
			rev = post.url.replace('https://old.reddit.com/', '')
			rev = f"* [undelete.pullpush.io](https://undelete.pullpush.io/{rev})\n\n"
		elif post.url.startswith("https://old.reddit.com/user/"):
			rev = post.url.replace('https://old.reddit.com/user/', '')
			rev = f"* [search-new.pullpush.io](https://search-new.pullpush.io/?author={rev}&type=submission)\n\n"
		else: rev = ''

		body += f"Snapshots:\n\n{rev}* [ghostarchive.org](https://ghostarchive.org/search?term={quote(post.url)})\n\n* [archive.org](https://web.archive.org/{post.url})\n\n* [archive.ph](https://archive.ph/?url={quote(post.url)}&run=1) (click to archive)\n\n"
		archive_url(post.url)

	captured = []
	body_for_snappy = post.body_html.replace(' data-src="', ' src="')


	for i in list(snappy_url_regex.finditer(body_for_snappy)):
		href = i.group(1)
		if href in [x[0] for x in captured]: continue
		title = i.group(2)
		captured.append((href, title))


	for href, title in captured:
		if href.startswith(f'{SITE_FULL}/') or href.startswith(SITE_FULL_IMAGES): continue
		if "Snapshots:\n\n" not in body: body += "Snapshots:\n\n"
		if f'**[{title}]({href})**:\n\n' not in body:
			addition = f'**[{title}]({href})**:\n\n'
			if href.startswith('https://old.reddit.com/r/'):
				rev = href.replace('https://old.reddit.com/', '')
				addition += f'* [undelete.pullpush.io](https://undelete.pullpush.io/{rev})\n\n'
			elif href.startswith('https://old.reddit.com/user/'):
				rev = href.replace('https://old.reddit.com/user/', '')
				addition += f"* [search-new.pullpush.io](https://search-new.pullpush.io/?author={rev}&type=submission)\n\n"
			addition += f'* [ghostarchive.org](https://ghostarchive.org/search?term={quote(href)})\n\n'
			addition += f'* [archive.org](https://web.archive.org/{href})\n\n'
			addition += f'* [archive.ph](https://archive.ph/?url={quote(href)}&run=1) (click to archive)\n\n'
			if len(f'{body}{addition}') > COMMENT_BODY_LENGTH_LIMIT: break
			body += addition
			archive_url(href)

	body = body[:COMMENT_BODY_LENGTH_LIMIT].strip()
	body_html = sanitize(body, snappy=True, showmore=True)

	if len(body_html) == 0:
		return

	if len(body_html) < COMMENT_BODY_HTML_LENGTH_LIMIT:
		c = Comment(author_id=SNAPPY_ID,
			distinguish_level=6,
			parent_post=post.id,
			level=1,
			nsfw=False,
			is_bot=True,
			app_id=None,
			body=body,
			body_html=body_html,
			ghost=ghost,
			ping_cost=ping_cost,
			)

		g.db.add(c)

		check_slots_command(c, v, snappy)

		snappy.comment_count += 1
		snappy.pay_account('coins', 1)
		g.db.add(snappy)

		if FEATURES['PINS'] and (body.startswith(':#marseypin:') or body.startswith(':#marseypin2:')):
			post.stickied = "Snappy"
			post.stickied_utc = int(time.time()) + 3600

		elif SITE_NAME == 'rDrama' and body.startswith(':#marseyban:'):
			days = 0.01
			reason = f'<a href="/post/{post.id}">/post/{post.id}</a>'
			v.ban(admin=snappy, reason=reason, days=days)
			text = f"@Snappy has banned you for **{days}** days for the following reason:\n\n> {reason}"
			send_repeatable_notification(v.id, text)
			duration = f"for {days} days"
			ma = ModAction(
				kind="ban_user",
				user_id=snappy.id,
				target_user_id=v.id,
				_note=f'duration: {duration}, reason: "{reason}"'
				)
			g.db.add(ma)
			post.bannedfor = f'{duration} by @Snappy'

		g.db.flush()

		if c.ping_cost:
			for x in group.member_ids:
				n = Notification(comment_id=c.id, user_id=x)
				g.db.add(n)
				push_notif({x}, f'New mention of you by @Snappy', c.body, c)

		c.top_comment_id = c.id

		post.comment_count += 1
		post.replies = [c]

def execute_zozbot(c, level, post, v):
	if SITE_NAME != 'rDrama': return

	if random.random() >= 0.001: return

	posting_to_post = isinstance(post, Post)

	if posting_to_post and post.hole and g.db.query(Exile.user_id).filter_by(user_id=ZOZBOT_ID, hole=post.hole).one_or_none():
		return

	c2 = Comment(author_id=ZOZBOT_ID,
		parent_post=post.id if posting_to_post else None,
		wall_user_id=post.id if not posting_to_post else None,
		parent_comment_id=c.id,
		level=level+1,
		is_bot=True,
		body="zoz",
		body_html='<p class="zozbot">zoz</p>',
		top_comment_id=c.top_comment_id,
		ghost=c.ghost,
		distinguish_level=6
	)

	g.db.add(c2)
	g.db.flush()
	n = Notification(comment_id=c2.id, user_id=v.id)
	g.db.add(n)

	c3 = Comment(author_id=ZOZBOT_ID,
		parent_post=post.id if posting_to_post else None,
		wall_user_id=post.id if not posting_to_post else None,
		parent_comment_id=c2.id,
		level=level+2,
		is_bot=True,
		body="zle",
		body_html='<p class="zozbot">zle</p>',
		top_comment_id=c.top_comment_id,
		ghost=c.ghost,
		distinguish_level=6
	)

	g.db.add(c3)
	g.db.flush()


	c4 = Comment(author_id=ZOZBOT_ID,
		parent_post=post.id if posting_to_post else None,
		wall_user_id=post.id if not posting_to_post else None,
		parent_comment_id=c3.id,
		level=level+3,
		is_bot=True,
		body="zozzle",
		body_html='<p class="zozbot">zozzle</p>',
		top_comment_id=c.top_comment_id,
		ghost=c.ghost,
		distinguish_level=6
	)

	g.db.add(c4)

	zozbot = get_account(ZOZBOT_ID)
	zozbot.comment_count += 3
	zozbot.pay_account('coins', 1)
	g.db.add(zozbot)

	if posting_to_post:
		post.comment_count += 3
		g.db.add(post)

	push_notif({v.id}, f'New reply by @{c2.author_name}', "zoz", c2)

def execute_longpostbot(c, level, body, body_html, post, v):
	if SITE_NAME != 'rDrama': return

	if not len(c.body.split()) >= 200: return

	if "</blockquote>" in body_html: return

	posting_to_post = isinstance(post, Post)

	if posting_to_post and post.hole and g.db.query(Exile.user_id).filter_by(user_id=LONGPOSTBOT_ID, hole=post.hole).one_or_none():
		return

	body = random.choice(LONGPOSTBOT_REPLIES)
	if body.startswith('▼'):
		body = body[1:]
		vote = CommentVote(user_id=LONGPOSTBOT_ID,
			vote_type=-1,
			comment_id=c.id,
			real = True
		)
		g.db.add(vote)
		c.downvotes = 1

	body_html = sanitize(body)

	c2 = Comment(author_id=LONGPOSTBOT_ID,
		parent_post=post.id if posting_to_post else None,
		wall_user_id=post.id if not posting_to_post else None,
		parent_comment_id=c.id,
		level=level+1,
		is_bot=True,
		body=body,
		body_html=body_html,
		top_comment_id=c.top_comment_id,
		ghost=c.ghost
	)

	g.db.add(c2)

	longpostbot = get_account(LONGPOSTBOT_ID)
	longpostbot.comment_count += 1
	longpostbot.pay_account('coins', 1)
	g.db.add(longpostbot)
	g.db.flush()
	n = Notification(comment_id=c2.id, user_id=v.id)
	g.db.add(n)

	if posting_to_post:
		post.comment_count += 1
		g.db.add(post)

	push_notif({v.id}, f'New reply by @{c2.author_name}', c2.body, c2)


def tempban_for_spam(v):
	text = "Your account has been banned for **1 day** for the following reason:\n\n> Too much spam!"
	send_repeatable_notification(v.id, text)
	v.ban(reason="Spam", days=1)

	ma = ModAction(
		kind="ban_user",
		user_id=AUTOJANNY_ID,
		target_user_id=v.id,
		_note=f'duration: for 1 day, reason: "Spam"'
		)
	g.db.add(ma)


def execute_antispam_post_check(title, v, url):
	if v.admin_level >= PERMS['BYPASS_ANTISPAM_CHECKS']:
		return True

	now = int(time.time())
	cutoff = now - 60 * 60 * 24

	similar_posts = g.db.query(Post).filter(
					Post.author_id == v.id,
					Post.title.op('<->')(title) < SPAM_SIMILARITY_THRESHOLD,
					Post.created_utc > cutoff
	).all()

	if url:
		similar_urls = g.db.query(Post).filter(
					Post.author_id == v.id,
					Post.url.op('<->')(url) < SPAM_URL_SIMILARITY_THRESHOLD,
					Post.created_utc > cutoff
		).all()
	else: similar_urls = []

	threshold = SPAM_SIMILAR_COUNT_THRESHOLD
	if v.age >= (60 * 60 * 24 * 7): threshold *= 3
	elif v.age >= (60 * 60 * 24): threshold *= 2

	if max(len(similar_urls), len(similar_posts)) >= threshold:
		tempban_for_spam(v)

		for post in similar_posts + similar_urls:
			post.is_banned = True
			post.is_pinned = False
			post.ban_reason = "AutoJanny"
			g.db.add(post)
			ma=ModAction(
					user_id=AUTOJANNY_ID,
					target_post_id=post.id,
					kind="ban_post",
					_note="Spam"
					)
			g.db.add(ma)
		return False
	return True

def execute_antispam_duplicate_comment_check(v, body_html):
	if v.admin_level >= PERMS['BYPASS_ANTISPAM_CHECKS']:
		return
	if v.id in ANTISPAM_BYPASS_IDS:
		return
	if v.age >= NOTIFICATION_SPAM_AGE_THRESHOLD:
		return
	if len(body_html) < 16:
		return

	ANTISPAM_DUPLICATE_THRESHOLD = 3
	compare_time = int(time.time()) - 60 * 60 * 24
	count = g.db.query(Comment.id).filter(Comment.body_html == body_html,
										  Comment.created_utc >= compare_time).count()
	if count <= ANTISPAM_DUPLICATE_THRESHOLD: return

	tempban_for_spam(v)

	g.db.commit()
	abort(403, "Too much spam!")

def execute_antispam_comment_check(body, v):
	if v.admin_level >= PERMS['BYPASS_ANTISPAM_CHECKS']:
		return

	if v.id in ANTISPAM_BYPASS_IDS: return
	if len(body) <= COMMENT_SPAM_LENGTH_THRESHOLD: return
	now = int(time.time())
	cutoff = now - 60 * 60 * 24

	similar_comments = g.db.query(Comment).filter(
		Comment.author_id == v.id,
		Comment.body.op('<->')(body) < COMMENT_SPAM_SIMILAR_THRESHOLD,
		Comment.created_utc > cutoff
	).all()

	threshold = COMMENT_SPAM_COUNT_THRESHOLD
	if v.age >= (60 * 60 * 24 * 7):
		threshold *= 3
	elif v.age >= (60 * 60 * 24):
		threshold *= 2

	if len(similar_comments) <= threshold: return

	tempban_for_spam(v)

	for comment in similar_comments:
		comment.is_banned = True
		comment.ban_reason = "AutoJanny"
		g.db.add(comment)
		ma=ModAction(
			user_id=AUTOJANNY_ID,
			target_comment_id=comment.id,
			kind="ban_comment",
			_note="Spam"
		)
		g.db.add(ma)
	g.db.commit()
	abort(403, "Too much spam!")

def execute_dylan(v):
	if "dylan" in v.username.lower() and "hewitt" in v.username.lower():
		v.shadowbanned = AUTOJANNY_ID
		v.ban_reason = "Dylan"
		g.db.add(v)
		ma = ModAction(
			kind="shadowban",
			user_id=AUTOJANNY_ID,
			target_user_id=v.id,
			_note=f'reason: "Dylan ({v.age} seconds)"'
		)
		g.db.add(ma)

def execute_under_siege(v, target, body, kind):
	if v.shadowbanned: return

	if SITE == 'watchpeopledie.tv':
		execute_dylan(v)
		if v.shadowbanned: return
		if kind != 'post': return

	if not get_setting("under_siege"): return
	if v.admin_level >= PERMS['BYPASS_UNDER_SIEGE_MODE']: return

	if kind in {'message', 'report'} and SITE == 'rdrama.net':
		threshold = 86400
	elif kind == 'post' and SITE == 'watchpeopledie.tv':
		threshold = 86400
	else:
		threshold = UNDER_SIEGE_AGE_THRESHOLD

	if v.age > threshold: return

	unshadowbannedcels = [x[0] for x in g.db.query(ModAction.target_user_id).filter_by(kind='unshadowban')]
	if v.id in unshadowbannedcels: return

	check_for_alts(v)
	if v.shadowbanned: return

	v.shadowbanned = AUTOJANNY_ID
	v.ban_reason = "Under Siege"
	g.db.add(v)

	if kind == "report":
		if isinstance(target, Post):
			reason = f'report on <a href="{target.permalink}">post</a>'
		else:
			reason = f'report on <a href="{target.permalink}">comment</a>'
	else:
		reason = kind

	ma = ModAction(
		kind="shadowban",
		user_id=AUTOJANNY_ID,
		target_user_id=v.id,
		_note=f'reason: "Under Siege ({reason}, {v.age} seconds)"'
	)
	g.db.add(ma)

	if kind == 'message':
		notified_ids = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS['BLACKJACK_NOTIFICATIONS'])]
		for uid in notified_ids:
			n = Notification(comment_id=target.id, user_id=uid)
			g.db.add(n)


def execute_lawlz_actions(v, p):
	if v.id != LAWLZ_ID: return
	if SITE_NAME != 'rDrama': return
	if not FEATURES['PINS']: return
	p.stickied_utc = int(time.time()) + 86400
	p.stickied = "AutoJanny"
	p.distinguish_level = 6
	p.flair = filter_emojis_only(":ben10: Required Reading")
	ma_1 = ModAction(
		kind="pin_post",
		user_id=AUTOJANNY_ID,
		target_post_id=p.id,
		_note='for 1 day'
	)
	ma_2 = ModAction(
		kind="distinguish_post",
		user_id=AUTOJANNY_ID,
		target_post_id=p.id
	)
	ma_3 = ModAction(
		kind="flair_post",
		user_id=AUTOJANNY_ID,
		target_post_id=p.id,
		_note=f'"{p.flair}"'
	)
	g.db.add(p)
	g.db.add(ma_1)
	g.db.add(ma_2)
	g.db.add(ma_3)


def process_poll_options(v, target):

	patterns = [(poll_regex, 0), (choice_regex, 1)]

	if v.admin_level >= PERMS['POST_BETS']:
		patterns.append((bet_regex, 2))

	option_count = 0

	option_objects = []

	for pattern, exclusive in patterns:
		body_html = target.body_html.replace('&amp;', '&')
		for i in pattern.finditer(body_html):
			option_count += 1

			if option_count > POLL_MAX_OPTIONS:
				abort(400, f"Max number of poll options is {POLL_MAX_OPTIONS}")

			body = i.group(2)

			if len(body) > 500:
				abort(400, f"Poll option body too long! (Max 500 characters)")

			if isinstance(target, Post):
				cls = PostOption
			else:
				cls = CommentOption

			existing = g.db.query(cls).filter_by(
					parent_id=target.id,
					body_html=body,
					exclusive=exclusive,
				).first()

			if not existing:
				option = cls(
					parent_id=target.id,
					body_html=body,
					exclusive=exclusive,
				)
				option_objects.append(option) #shitty hack to bypass autoflush

	g.db.add_all(option_objects)
