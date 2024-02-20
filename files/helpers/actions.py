import random
import time
from urllib.parse import quote
from sqlalchemy.sql import func
import gevent
import requests
import math
from flask import g

from files.classes.reports import Report
from files.classes.mod_logs import ModAction
from files.classes.notifications import Notification
from files.classes.polls import CommentOption, PostOption
from files.classes.award import AwardRelationship
from files.classes.hole_relationship import Exile

from files.helpers.alerts import send_repeatable_notification, push_notif
from files.helpers.config.const import *
from files.helpers.config.awards import AWARDS
from files.helpers.const_stateful import *
from files.helpers.get import *
from files.helpers.logging import log_file
from files.helpers.sanitize import *
from files.helpers.settings import get_setting
from files.helpers.slots import check_slots_command
from files.helpers.useractions import badge_grant

from files.routes.routehelpers import check_for_alts

def _archiveorg(url):
	try:
		requests.post('https://ghostarchive.org/archive2', data={"archive": url}, headers=HEADERS, timeout=10)
	except: pass
	try:
		requests.get(f'https://web.archive.org/save/{url}', headers=HEADERS, timeout=10)
	except: pass


def archive_url(url):
	gevent.spawn(_archiveorg, url)
	if url.startswith('https://twitter.com/'):
		url = url.replace('https://twitter.com/', 'https://nitter.unixfox.eu/')
		gevent.spawn(_archiveorg, url)
	if url.startswith('https://instagram.com/'):
		url = url.replace('https://instagram.com/', 'https://imginn.com/')
		gevent.spawn(_archiveorg, url)

def snappy_report(post, reason):
	report = Report(post_id=post.id, user_id=SNAPPY_ID, reason=reason)
	g.db.add(report)
	message = f'@Snappy reported {post.textlink})\n\n> {reason}'
	send_repeatable_notification(post.author_id, message)

def execute_snappy(post, v):
	if post.hole and g.db.query(Exile.user_id).filter_by(user_id=SNAPPY_ID, hole=post.hole).one_or_none():
		return

	ghost = post.ghost

	snappy = get_account(SNAPPY_ID)

	ping_cost = 0

	post_ping_group_count = len(list(group_mention_regex.finditer(post.body)))

	if post.hole and post.hole_obj.snappy_quotes:
		quotes = post.hole_obj.snappy_quotes.split("[para]")
		body = random.choice(quotes).strip()
	elif SITE_NAME == 'WPD' and ('killing myself' in post.title.lower() or (post.hole != 'suicide' and 'suicide' in post.title.lower())):
		body = "https://i.watchpeopledie.tv/images/1697382435294321.webp"
	elif post_ping_group_count > 3:
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
			body = random.choice(("i love you carp", "https://i.rdrama.net/images/16614707883108485.webp", "https://i.rdrama.net/images/1636916964YyM.webp", "https://youtube.com/watch?v=zRbQHTdsjuY", "https://i.rdrama.net/images/1696250281381682.webp", "https://i.rdrama.net/images/16975678508317988.webp", "https://i.rdrama.net/images/170526627808132.webp", "https://i.rdrama.net/images/17052853054732056.webp"))
		elif IS_DKD():
			body = ":#donkeykongfuckoffcarp:"
		elif IS_HOMOWEEN():
			body = "F̵̽̉U̷̓̕C̵̟̍K̴̾̍ ̵́̒O̶͐̇F̷͗̐F̴͛̄ ̸̆͠CARP"
		elif IS_FISTMAS():
			body = "Merry Christmas Carp :marseychristmasgift2:"
		else:
			body = ":#carpwavelove:"
	elif v.id == AEVANN_ID:
		body = "https://i.rdrama.net/images/16909380805064178.webp"
	elif SITE == 'rdrama.net' and v.id == 253:
		body = "https://i.rdrama.net/images/16961715452780113.webp"
	elif SITE == 'rdrama.net' and v.id == 8094:
		body = "https://i.rdrama.net/images/17025988883967621.webp"
	elif SITE == 'rdrama.net' and v.id == 5214:
		body = random.choice(("https://rdrama.net/audio/1704983217764354.mp3", "Dear Chiobu:\n\nWe are not accepting non-US residents because of difficulty of payment and difficulty of enforcing our Confidentiality Agreement internationally. Additionally, you seem to have opinions incompatible with ours, namely your opinions **Towards the Chinese** and **Towards Transgender Individuals**. We thank you for your interest."))
	elif SITE == 'rdrama.net' and v.id == 9493:
		body = "https://i.rdrama.net/images/16973719400351799.webp"
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
		body = body.replace('%OP%', f'@{post.author_name}')
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
		elif ':#marseyghost' in body:
			ghost = True
		elif body == '!slots':
			body = f'!slots{snappy.coins}'
		elif body == '!pinggroup':
			group = g.db.query(Group).filter(Group.name != 'focusgroup').order_by(func.random()).first()

			cost = len(group.member_ids) * 5
			snappy.charge_account('coins', cost)

			body = f'!{group.name}'

			ping_cost = cost
		elif body.startswith(':#marseyglow'):
			award_object = AwardRelationship(
					user_id=snappy.id,
					kind="glowie",
					post_id=post.id,
					awarded_utc=time.time(),
				)
			g.db.add(award_object)

			awarded_coins = int(AWARDS["glowie"]['price'] * COSMETIC_AWARD_COIN_AWARD_PCT)
			post.author.pay_account('coins', awarded_coins)

			msg = f"@Snappy has given {post.textlink} the Glowie Award and you have received {awarded_coins} coins as a result!"
			send_repeatable_notification(post.author.id, msg)
		elif body.startswith("You're a chud, CHUD I tell you"):
			award_object = AwardRelationship(
					user_id=snappy.id,
					kind="chud",
					post_id=post.id,
					awarded_utc=time.time(),
					note="Trans lives matter",
				)
			g.db.add(award_object)

			msg = f"@Snappy has given {post.textlink} the Chud Award\n\n**You now have to say this phrase in all posts and comments you make for 24 hours:**\n\n> Trans lives matter"
			send_repeatable_notification(post.author.id, msg)

			if v.chud != 1:
				if v.chud and time.time() < v.chud: v.chud += 86400
				else: v.chud = int(time.time()) + 86400
				v.chud_phrase = 'trans lives matter'
				badge_grant(user=v, badge_id=58)
				post.chudded = True
				complies_with_chud(post)

	body += "\n\n"

	if post.url and not post.url.startswith('/') and not post.url.startswith(f'{SITE_FULL}/') and not post.url.startswith(SITE_FULL_IMAGES):
		if post.url.startswith('https://old.reddit.com/r/') and '/comments/' in post.url:
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
		if href == post.url: continue
		if href.startswith(f'{SITE_FULL}/') or href.startswith(SITE_FULL_IMAGES): continue
		if "Snapshots:\n\n" not in body: body += "Snapshots:\n\n"
		if f'**[{title}]({href})**:\n\n' not in body:
			addition = f'**[{title}]({href})**:\n\n'
			if href.startswith('https://old.reddit.com/r/') and '/comments/' in href:
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
			distinguished=True,
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
			post.pinned = "Snappy"
			post.pinned_utc = int(time.time()) + 3600

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
		body_html='<p>zoz</p>',
		top_comment_id=c.top_comment_id,
		ghost=c.ghost,
		distinguished=True
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
		body_html='<p>zle</p>',
		top_comment_id=c.top_comment_id,
		ghost=c.ghost,
		distinguished=True
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
		body_html='<p>zozzle</p>',
		top_comment_id=c.top_comment_id,
		ghost=c.ghost,
		distinguished=True
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
			post.profile_pinned = False
			post.ban_reason = "AutoJanny"
			g.db.add(post)
			ma = ModAction(
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
		ma = ModAction(
			user_id=AUTOJANNY_ID,
			target_comment_id=comment.id,
			kind="ban_comment",
			_note="Spam"
		)
		g.db.add(ma)
	g.db.commit()
	abort(403, "Too much spam!")

def execute_under_siege(v, target, body, kind):
	if v.shadowbanned: return

	if v.admin_level >= PERMS['BYPASS_UNDER_SIEGE_MODE']: return

	thresholds = cache.get("under_siege_thresholds")
	if not thresholds:
		thresholds = DEFAULT_UNDER_SIEGE_THRESHOLDS
		cache.set("under_siege_thresholds", thresholds)

	if v.age > thresholds[kind] * 60:
		return

	unshadowbannedcels = [x[0] for x in g.db.query(ModAction.target_user_id).filter_by(kind='unshadowban')]
	if v.id in unshadowbannedcels: return

	check_for_alts(v)
	if v.shadowbanned: return

	v.shadowbanned = AUTOJANNY_ID
	v.shadowban_reason = "Under Siege"
	g.db.add(v)

	if kind == "report":
		if isinstance(target, Post):
			reason = f'report on <a href="{target.permalink}">post</a>'
		else:
			reason = f'report on <a href="{target.permalink}">comment</a>'
	elif hasattr(target, 'permalink'):
		reason = f'<a href="{target.permalink}">{kind}</a>'
	else:
		reason = kind

	minutes = math.ceil(v.age / 60)
	time_taken = f'{minutes} minute'
	if minutes > 1:
		time_taken += 's'

	ma = ModAction(
		kind="shadowban",
		user_id=AUTOJANNY_ID,
		target_user_id=v.id,
		_note=f'reason: "Under Siege ({reason}, {time_taken})"'
	)
	g.db.add(ma)

def process_options(v, target):

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
				abort(400, f"Poll option body is too long (Max 500 characters)")

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
