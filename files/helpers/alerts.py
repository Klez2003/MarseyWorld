import json
from sys import stdout

import gevent
from flask import g
from pywebpush import webpush
import time
from sqlalchemy.sql import text

from files.classes import Comment, Notification, PushSubscription, Group

from .config.const import *
from .regex import *
from .sanitize import *

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

	text_html = sanitize(text, blackjack="notification")

	existing_comments = g.db.query(Comment.id).filter_by(author_id=AUTOJANNY_ID, parent_post=None, body_html=text_html, is_bot=True).order_by(Comment.id).all()

	for c in existing_comments:
		existing_notif = g.db.query(Notification.user_id).filter_by(user_id=uid, comment_id=c.id).one_or_none()
		if not existing_notif:
			notif = Notification(comment_id=c.id, user_id=uid)
			g.db.add(notif)

			push_notif({uid}, 'New notification', text, f'{SITE_FULL}/comment/{c.id}?read=true#context')
			return

	cid = create_comment(text_html)
	notif = Notification(comment_id=cid, user_id=uid)
	g.db.add(notif)

	push_notif({uid}, 'New notification', text, f'{SITE_FULL}/comment/{cid}?read=true#context')


def send_notification(uid, text):

	if uid in BOT_IDs: return
	cid = notif_comment(text)
	add_notif(cid, uid, text)


def notif_comment(text):

	text_html = sanitize(text, blackjack="notification")

	g.db.flush()

	existing = g.db.query(Comment.id).filter(
		Comment.author_id == AUTOJANNY_ID,
		Comment.parent_post == None,
		Comment.body_html == text_html,
		Comment.is_bot == True,
	).order_by(Comment.id).all()

	if len(existing) > 1:
		replace_with = existing[0][0]
		replaced = [x[0] for x in existing[1:]]

		for n in g.db.query(Notification).filter(Notification.comment_id.in_(replaced)).all():
			n.comment_id = replace_with
			g.db.add(n)

		g.db.flush()

		for c in g.db.query(Comment).filter(Comment.id.in_(replaced)).all():
			g.db.delete(c)

		return replace_with
	elif existing:
		return existing[0][0]
	else:
		return create_comment(text_html)


def notif_comment2(p):

	text = f"@{p.author_name} has mentioned you: [{p.title}](/post/{p.id})"

	search_html = f'%</a> has mentioned you: <a href="/post/{p.id}"%'

	existing = g.db.query(Comment.id).filter(Comment.author_id == AUTOJANNY_ID, Comment.parent_post == None, Comment.body_html.like(search_html)).first()

	if existing: return existing[0], text
	else:
		if p.sub: text += f" in <a href='/h/{p.sub}'>/h/{p.sub}"
		text_html = sanitize(text, blackjack="notification")
		return create_comment(text_html), text


def add_notif(cid, uid, text, pushnotif_url=''):
	if uid in BOT_IDs: return

	existing = g.db.query(Notification.user_id).filter_by(comment_id=cid, user_id=uid).one_or_none()
	if not existing:
		notif = Notification(comment_id=cid, user_id=uid)
		g.db.add(notif)

		if not pushnotif_url:
			pushnotif_url = f'{SITE_FULL}/comment/{cid}?read=true#context'

		if ' has mentioned you: [' in text:
			text = text.split(':')[0] + '!'

		push_notif({uid}, 'New notification', text, pushnotif_url)


def NOTIFY_USERS(text, v, oldtext=None, ghost=False, log_cost=None):
	# Restrict young accounts from generating notifications
	if v.age < NOTIFICATION_SPAM_AGE_THRESHOLD:
		return set()

	text = text.lower()
	notify_users = set()

	for word, id in NOTIFIED_USERS.items():
		if word in text:
			notify_users.add(id)

	names = set(m.group(1) for m in mention_regex.finditer(text))

	user_ids = get_users(names, ids_only=True, graceful=True)
	notify_users.update(user_ids)

	if SITE_NAME == "WPD" and 'daisy' in text:
		admin_ids = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS['NOTIFICATIONS_SPECIFIC_WPD_COMMENTS']).all()]
		notify_users.update(admin_ids)




	if FEATURES['PING_GROUPS']:
		cost = 0

		for i in group_mention_regex.finditer(text):
			if oldtext and i.group(1) in oldtext:
				continue

			if i.group(1) == 'everyone' and not v.shadowbanned:
				cost = g.db.query(User).count() * 5
				if cost > v.coins:
					abort(403, f"You need {cost} coins to mention these ping groups!")
				g.db.query(User).update({ User.coins: User.coins + 5 })
				v.charge_account('coins', cost)
				return 'everyone'
			else:
				group = g.db.get(Group, i.group(1))
				if not group: continue

				members = group.member_ids - notify_users - v.all_twoway_blocks

				notify_users.update(members)

				if ghost or v.id not in group.member_ids:
					if group.name == 'biofoids': mul = 10
					else: mul = 5

					cost += len(members) * mul
					if cost > v.coins:
						abort(403, f"You need {cost} coins to mention these ping groups!")

					if log_cost:
						log_cost.ping_cost = cost

					g.db.query(User).filter(User.id.in_(members)).update({ User.coins: User.coins + mul })

		v.charge_account('coins', cost)



	return notify_users - BOT_IDs - {v.id, 0} - v.all_twoway_blocks


def push_notif(uids, title, body, url_or_comment):
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

	body = censor_slurs(body, None)

	subscriptions = g.db.query(PushSubscription.subscription_json).filter(PushSubscription.user_id.in_(uids)).all()
	subscriptions = [x[0] for x in subscriptions]
	g.db.flush()
	gevent.spawn(_push_notif_thread, subscriptions, title, body, url)


def _push_notif_thread(subscriptions, title, body, url):
	for subscription in subscriptions:
		try:
			response = webpush(
				subscription_info=json.loads(subscription),
				data=json.dumps({
					"title": title,
					"body": body,
					'url': url,
					'icon': f'{SITE_FULL}/icon.webp?x=6',
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
