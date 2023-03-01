import json
from sys import stdout

import gevent
from flask import g
from pywebpush import webpush

from files.classes import Comment, Notification, PushSubscription, Group

from .config.const import *
from .regex import *
from .sanitize import *

def create_comment(text_html):
	new_comment = Comment(author_id=AUTOJANNY_ID,
							parent_submission=None,
							body_html=text_html,
							distinguish_level=6,
							is_bot=True)
	g.db.add(new_comment)
	g.db.flush()

	new_comment.top_comment_id = new_comment.id

	return new_comment.id

def send_repeatable_notification(uid, text):

	if uid in bots: return

	text_html = sanitize(text, blackjack="notification")

	existing_comments = g.db.query(Comment.id).filter_by(author_id=AUTOJANNY_ID, parent_submission=None, body_html=text_html, is_bot=True).order_by(Comment.id).all()

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

	if uid in bots: return
	cid = notif_comment(text)
	add_notif(cid, uid, text)


def notif_comment(text):

	text_html = sanitize(text, blackjack="notification")

	g.db.flush()

	existing = g.db.query(Comment.id).filter(
		Comment.author_id == AUTOJANNY_ID,
		Comment.parent_submission == None,
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

	search_html = f'%</a> has mentioned you: <a href="/post/{p.id}">%'

	existing = g.db.query(Comment.id).filter(Comment.author_id == AUTOJANNY_ID, Comment.parent_submission == None, Comment.body_html.like(search_html)).first()

	if existing: return existing[0], text
	else:
		if p.sub: text += f" in <a href='/h/{p.sub}'>/h/{p.sub}"
		text_html = sanitize(text, blackjack="notification")
		return create_comment(text_html), text


def add_notif(cid, uid, text, pushnotif_url=''):
	if uid in bots: return

	existing = g.db.query(Notification.user_id).filter_by(comment_id=cid, user_id=uid).one_or_none()
	if not existing:
		notif = Notification(comment_id=cid, user_id=uid)
		g.db.add(notif)

		if not pushnotif_url:
			pushnotif_url = f'{SITE_FULL}/comment/{cid}?read=true#context'

		if ' has mentioned you: [' in text:
			text = text.split(':')[0] + '!'

		push_notif({uid}, 'New notification', text, pushnotif_url)


def NOTIFY_USERS(text, v):
	# Restrict young accounts from generating notifications
	if v.age < NOTIFICATION_SPAM_AGE_THRESHOLD:
		return set()

	text = text.lower()
	notify_users = set()

	for word, id in NOTIFIED_USERS.items():
		if word in text and id not in notify_users:
			notify_users.add(id)

	if FEATURES['PING_GROUPS']:
		billed = set()
		for i in group_mention_regex.finditer(text):
			if i.group(2) == 'everyone':
				everyone = [x[0] for x in g.db.query(User.id).all()]
				billed.update(everyone)
				notify_users.update(everyone)
			else:
				group = g.db.get(Group, i.group(2))
				if group:
					if v.id not in group.member_ids:
						billed.update(group.member_ids)
					notify_users.update(group.member_ids)

		if billed:
			cost = len(billed) * 5
			if cost > v.coins:
				abort(403, f"You need {cost} coins for this!")
			g.db.query(User).filter(User.id.in_(billed)).update({ User.coins: User.coins + 5 })
			v.coins -= cost
			g.db.add(v)


	names = set(m.group(2) for m in mention_regex.finditer(text))
	for user in get_users(names, graceful=True):
		if v.id != user.id and not v.any_block_exists(user):
			notify_users.add(user.id)

	if SITE_NAME == "WPD" and 'daisy' in text:
		admin_ids = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS['NOTIFICATIONS_SPECIFIC_WPD_COMMENTS']).all()]
		notify_users.update(admin_ids)

	return notify_users - bots - {v.id, 0}


def push_notif(uids, title, body, url_or_comment):
	if VAPID_PUBLIC_KEY == DEFAULT_CONFIG_VALUE:
		return

	if isinstance(url_or_comment, Comment):
		c = url_or_comment
		if c.wall_user_id:
			url = f'{SITE_FULL}/@{c.wall_user.username}/wall/comment/{c.id}?read=true#context'
		else:
			url = f'{SITE_FULL}/comment/{c.id}?read=true#context'
	else:
		url = url_or_comment

	if len(body) > PUSH_NOTIF_LIMIT:
		body = body[:PUSH_NOTIF_LIMIT] + "..."

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
					'icon': f'{SITE_FULL}/icon.webp?v=1',
					}),
				vapid_private_key=VAPID_PRIVATE_KEY,
				vapid_claims={"sub": f"mailto:{EMAIL}"}
			)
		except: continue
