import json
from sys import stdout

import gevent
from flask import g
from pywebpush import webpush
import time
from sqlalchemy.sql import text
from sqlalchemy.orm import load_only

from files.classes import Comment, Notification, PushSubscription, Group, Mod

from .config.const import *
from .regex import *
from .sanitize import *
from .slurs_and_profanities import censor_slurs_profanities

def create_comment(text_html):
	new_comment = Comment(author_id=AUTOJANNY_ID,
							parent_post=None,
							body_html=text_html,
							distinguish_level=6,
							is_bot=True)
	g.db.add(new_comment)
	g.db.flush()

	new_comment.top_comment_id = new_comment.id

	return new_comment.id

def send_repeatable_notification(uid, text):
	if uid in BOT_IDs: return

	if hasattr(g, 'v') and g.v and g.v.shadowbanned and g.db.query(User.admin_level).filter_by(id=uid).one()[0] < PERMS['USER_SHADOWBAN']:
		return

	text_html = sanitize(text, blackjack="notification")

	existing_comments = g.db.query(Comment.id).filter_by(author_id=AUTOJANNY_ID, parent_post=None, body_html=text_html, is_bot=True).order_by(Comment.id).all()

	for c in existing_comments:
		existing_notif = g.db.query(Notification.user_id).filter_by(user_id=uid, comment_id=c.id).one_or_none()
		if not existing_notif:
			notif = Notification(comment_id=c.id, user_id=uid)
			g.db.add(notif)

			push_notif({uid}, 'New notification', text, f'{SITE_FULL}/notification/{c.id}')
			return notif

	cid = create_comment(text_html)
	notif = Notification(comment_id=cid, user_id=uid)
	g.db.add(notif)

	push_notif({uid}, 'New notification', text, f'{SITE_FULL}/notification/{cid}')

	return notif


def send_notification(uid, text):
	if uid in BOT_IDs: return

	if hasattr(g, 'v') and g.v and g.v.shadowbanned and g.db.query(User.admin_level).filter_by(id=uid).one()[0] < PERMS['USER_SHADOWBAN']:
		return

	cid = notif_comment(text)
	add_notif(cid, uid, text)


def notif_comment(text):

	text_html = sanitize(text, blackjack="notification")

	existing = g.db.query(Comment.id).filter(
		Comment.author_id == AUTOJANNY_ID,
		Comment.parent_post == None,
		Comment.body_html == text_html,
		Comment.is_bot == True,
	).order_by(Comment.id).all()

	if len(existing) > 1:
		replace_with = existing[0][0]
		replaced = [x[0] for x in existing[1:]]

		for n in g.db.query(Notification).filter(Notification.comment_id.in_(replaced)):
			n.comment_id = replace_with
			g.db.add(n)

		for c in g.db.query(Comment).filter(Comment.id.in_(replaced)):
			g.db.delete(c)

		return replace_with
	elif existing:
		return existing[0][0]
	else:
		return create_comment(text_html)


def notif_comment2(p):
	if p.ghost:
		author_link = '@👻'
	else:
		author_link = f'<a href="/id/{p.author_id}"><img loading="lazy" src="/pp/{p.author_id}">@{p.author_name}</a>'

	text = f'@{p.author_name} has mentioned you: {p.title}'

	search_html = f'%</a> has mentioned you: <a href="/post/{p.id}"%'

	existing = g.db.query(Comment.id).filter(Comment.author_id == AUTOJANNY_ID, Comment.parent_post == None, Comment.body_html.like(search_html)).first()

	if existing: return existing[0], text
	else:
		text_html = f'{author_link} has mentioned you: <a href="/post/{p.id}">{p.title_html}</a>'
		if p.hole: text_html += f" in <a href='/h/{p.hole}'>/h/{p.hole}"
		return create_comment(text_html), text


def add_notif(cid, uid, text, pushnotif_url=''):
	if uid in BOT_IDs: return

	if hasattr(g, 'v') and g.v and g.v.shadowbanned and g.db.query(User.admin_level).filter_by(id=uid).one()[0] < PERMS['USER_SHADOWBAN']:
		return

	existing = g.db.query(Notification.user_id).filter_by(comment_id=cid, user_id=uid).one_or_none()
	if not existing:
		notif = Notification(comment_id=cid, user_id=uid)
		g.db.add(notif)

		if not pushnotif_url:
			pushnotif_url = f'{SITE_FULL}/notification/{cid}'

		if ' has mentioned you: [' in text:
			text = text.split(':')[0] + '!'

		if not request.path.startswith('/submit'):
			push_notif({uid}, 'New notification', text, pushnotif_url)


def NOTIFY_USERS(text, v, oldtext=None, ghost=False, obj=None, followers_ping=True, commenters_ping_post_id=None):
	# Restrict young accounts from generating notifications
	if v.age < NOTIFICATION_SPAM_AGE_THRESHOLD:
		return set()

	text = text.lower()

	if oldtext:
		oldtext = oldtext.lower()

	notify_users = set()

	for word, id in NOTIFIED_USERS.items():
		if word in text:
			notify_users.add(id)

	names = set(m.group(1) for m in mention_regex.finditer(text))

	if oldtext:
		oldnames = set(m.group(1) for m in mention_regex.finditer(oldtext))
		names = names - oldnames

	user_ids = get_users(names, ids_only=True, graceful=True)
	notify_users.update(user_ids)

	if SITE_NAME == "WPD" and 'daisy' in text:
		admin_ids = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS['NOTIFICATIONS_SPECIFIC_WPD_COMMENTS'])]
		notify_users.update(admin_ids)

	if FEATURES['PING_GROUPS']:
		cost = 0
		coin_receivers = set()

		for i in group_mention_regex.finditer(text):
			if oldtext and i.group(1) in oldtext:
				continue

			if i.group(1) == 'focusgroup' and not v.admin_level:
				abort(403, f"Only admins can mention !focusgroup")

			if i.group(1) == 'everyone':
				cost = g.db.query(User).count() * 5
				if cost > v.coins + v.marseybux:
					abort(403, f"You need {cost} currency to mention these ping groups!")

				v.charge_account('coins/marseybux', cost)
				if obj:
					obj.ping_cost += cost
				return 'everyone'
			elif i.group(1) == 'jannies':
				group = None
				member_ids = set(x[0] for x in g.db.query(User.id).filter(User.admin_level > 0, User.id != AEVANN_ID))
			elif i.group(1) == 'holejannies':
				if not get_obj_hole(obj):
					abort(403, "!holejannies can only be used inside holes!")
				group = None
				member_ids = set(x[0] for x in g.db.query(Mod.user_id).filter_by(hole=obj.hole))
			elif i.group(1) == 'followers':
				if not followers_ping:
					abort(403, f"You can't use !followers in posts!")
				group = None
				member_ids = set(x[0] for x in g.db.query(Follow.user_id).filter_by(target_id=v.id))
			elif i.group(1) == 'commenters':
				if not commenters_ping_post_id:
					abort(403, "You can only use !commenters in comments made under posts!")
				group = None
				member_ids = set(x[0] for x in g.db.query(User.id).join(Comment, Comment.author_id == User.id).filter(Comment.parent_post == commenters_ping_post_id)) - {v.id}
			else:
				group = g.db.get(Group, i.group(1))
				if not group: continue
				member_ids = group.member_ids

			members = member_ids - notify_users - BOT_IDs - v.all_twoway_blocks - v.muters

			notify_users.update(members)

			realghost = ghost and i.group(1) != 'ghosts'
			if (realghost or v.id not in member_ids) and i.group(1) != 'followers':
				if group and group.name == 'verifiedrich':
					abort(403, f"Only !verifiedrich members can mention it!")
				cost += len(members) * 5
				if cost > v.coins + v.marseybux:
					abort(403, f"You need {cost} currency to mention these ping groups!")

				if i.group(1) in {'biofoids','neofoids','jannies'}:
					coin_receivers.update(member_ids)

		if cost:
			v.charge_account('coins/marseybux', cost)
			if obj:
				obj.ping_cost += cost

		if coin_receivers:
			g.db.query(User).options(load_only(User.id)).filter(User.id.in_(coin_receivers)).update({ User.coins: User.coins + 5 })

	if len(notify_users) > 400 and v.admin_level < PERMS['POST_COMMENT_INFINITE_PINGS']:
		abort(403, "You can only notify a maximum of 400 users.")

	if v.shadowbanned or (obj and obj.is_banned):
		notify_users = set(x[0] for x in g.db.query(User.id).filter(User.id.in_(notify_users), User.admin_level >= PERMS['USER_SHADOWBAN']).all())

	return notify_users - BOT_IDs - {v.id, 0} - v.all_twoway_blocks - v.muters


def push_notif(uids, title, body, url_or_comment):
	if hasattr(g, 'v') and g.v and g.v.shadowbanned:
		uids = [x[0] for x in g.db.query(User.id).filter(User.id.in_(uids), User.admin_level >= PERMS['USER_SHADOWBAN']).all()]
		if not uids:
			return

	if VAPID_PUBLIC_KEY == DEFAULT_CONFIG_VALUE:
		return

	if isinstance(url_or_comment, Comment):
		c = url_or_comment
		if c.is_banned: return

		if c.wall_user_id:
			url = f'{SITE_FULL}/@{c.wall_user.username}/wall/comment/{c.id}?read=true#context'
		else:
			url = f'{SITE_FULL}/comment/{c.id}?read=true#context'
	else:
		url = url_or_comment

	if len(body) > PUSH_NOTIF_LIMIT:
		body = body[:PUSH_NOTIF_LIMIT] + "..."

	body = censor_slurs_profanities(body, None, True)

	subscriptions = g.db.query(PushSubscription.subscription_json).filter(PushSubscription.user_id.in_(uids)).all()
	subscriptions = [x[0] for x in subscriptions]
	gevent.spawn(_push_notif_thread, subscriptions, title, body, url)


def _push_notif_thread(subscriptions, title, body, url):
	for subscription in subscriptions:
		try:
			webpush(
				subscription_info=json.loads(subscription),
				data=json.dumps({
					"title": title,
					"body": body,
					'url': url,
					'icon': f'{SITE_FULL}/icon.webp?x=7',
					}),
				vapid_private_key=VAPID_PRIVATE_KEY,
				vapid_claims={"sub": f"mailto:{EMAIL}"}
			)
		except: continue

def alert_everyone(cid):
	cid = int(cid)
	t = int(time.time())
	_everyone_query = text(f"""
	insert into notifications
	select id, {cid}, false, {t} from users
	on conflict do nothing;""")
	g.db.execute(_everyone_query)
