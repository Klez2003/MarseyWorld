import json
from sys import stdout

import gevent
from flask import g
from pywebpush import webpush
import time
from sqlalchemy.sql import text, and_
from sqlalchemy.orm import load_only

from files.classes import Comment, Post, Notification, PushSubscription, Group, Mod, GroupMembership, ChatMembership

from .config.const import *
from .regex import *
from .sanitize import *
from .slurs_and_profanities import censor_slurs_profanities

def create_comment(text_html):
	new_comment = Comment(author_id=AUTOJANNY_ID,
							parent_post=None,
							body_html=text_html,
							distinguished=True,
							is_bot=True)
	g.db.add(new_comment)
	g.db.flush()

	new_comment.top_comment_id = new_comment.id

	return new_comment.id

def send_repeatable_notification(uid, text, only_repeatable_after_1week=False):
	if uid in BOT_IDs: return

	if hasattr(g, 'v') and g.v and g.v.shadowbanned and g.db.query(User.admin_level).filter_by(id=uid).one()[0] < PERMS['USER_SHADOWBAN']:
		return

	text_html = sanitize(text, blackjack="notification")

	existing_comments = g.db.query(Comment.id).filter_by(author_id=AUTOJANNY_ID, parent_post=None, body_html=text_html, is_bot=True).order_by(Comment.id).all()

	existing_notif = None
	for c in existing_comments:
		existing_notif = g.db.query(Notification).filter_by(user_id=uid, comment_id=c.id).one_or_none()
		if not existing_notif:
			notif = Notification(comment_id=c.id, user_id=uid)
			g.db.add(notif)

			push_notif({uid}, 'New notification', text, f'{SITE_FULL}/notification/{c.id}')
			return notif

	one_week_ago = time.time() - 604800
	if only_repeatable_after_1week and existing_notif and existing_notif.created_utc > one_week_ago:
		return

	cid = create_comment(text_html)
	notif = Notification(comment_id=cid, user_id=uid)
	g.db.add(notif)

	push_notif({uid}, 'New notification', text, f'{SITE_FULL}/notification/{cid}')

	return notif


def send_notification(uid, text):
	send_repeatable_notification(uid, text, only_repeatable_after_1week=True)

def notif_comment(text):

	text_html = sanitize(text, blackjack="notification")

	existing = g.db.query(Comment.id).filter(
		Comment.author_id == AUTOJANNY_ID,
		Comment.parent_post == None,
		Comment.body_html == text_html,
		Comment.is_bot == True,
	).order_by(Comment.id).all()

	if len(existing) > 1:
		to_delete = [x[0] for x in existing[1:]]

		for n in g.db.query(Notification).filter(Notification.comment_id.in_(to_delete)):
			g.db.delete(n)

		for c in g.db.query(Comment).filter(Comment.id.in_(to_delete)):
			g.db.delete(c)

		return existing[0][0]
	elif existing:
		return existing[0][0]
	else:
		return create_comment(text_html)


def notif_comment_mention(p):
	if p.ghost:
		author_link = '@👻'
	else:
		author_link = f'<a href="/id/{p.author_id}"><img loading="lazy" src="/pp/{p.author_id}">@{p.author_name}</a>'

	text = f'@{p.author_name} has mentioned you: {p.title}'

	search_html = f'%</a> has mentioned you: <a href="/post/{p.id}"%'

	existing = g.db.query(Comment.id).filter(
		Comment.author_id == AUTOJANNY_ID,
		Comment.parent_post == None,
		Comment.body_html.like(search_html),
	).first()

	if existing: return existing[0], text
	else:
		text_html = f'{author_link} has mentioned you: <a href="/post/{p.id}">{p.title_html}</a>'
		if p.hole: text_html += f" in <a href='/h/{p.hole}'>/h/{p.hole}"
		return create_comment(text_html), text


def add_notif(cid, uid, text, pushnotif_url='', check_existing=True):
	if uid in BOT_IDs: return

	if hasattr(g, 'v') and g.v and g.v.shadowbanned and g.db.query(User.admin_level).filter_by(id=uid).one()[0] < PERMS['USER_SHADOWBAN']:
		return

	if check_existing:
		existing = g.db.query(Notification.user_id).filter_by(comment_id=cid, user_id=uid).one_or_none()
		if existing: return

	notif = Notification(comment_id=cid, user_id=uid)
	g.db.add(notif)

	if not pushnotif_url:
		pushnotif_url = f'{SITE_FULL}/notification/{cid}'

	if ' has mentioned you: [' in text:
		text = text.split(':')[0] + '!'

	push_notif({uid}, 'New notification', text, pushnotif_url)


def NOTIFY_USERS(text, v, oldtext=None, ghost=False, obj=None, followers_ping=True, commenters_ping_post_id=None, charge=True, chat=None, membership=None):
	# Restrict young accounts from generating notifications
	if v.age < NOTIFICATION_SPAM_AGE_THRESHOLD:
		return set()

	text = text.lower()

	if oldtext:
		oldtext = oldtext.lower()

	notify_users = set()


	criteria = (Notification.user_id == User.id, Notification.read == False)

	keyword_users = g.db.query(User.id, User.keyword_notifs).outerjoin(Notification, and_(*criteria)).group_by(User.id, User.keyword_notifs).having(func.count(Notification.user_id) < 100).filter(User.keyword_notifs != None, User.patron >= 5)

	for uid, keyword_notifs in keyword_users:
		for word in keyword_notifs.lower().split('\n'):
			if not word: continue
			if word in text:
				notify_users.add(uid)


	names = set(m.group(1) for m in user_mention_regex.finditer(text))

	if oldtext:
		oldnames = set(m.group(1) for m in user_mention_regex.finditer(oldtext))
		names = names - oldnames

	user_ids = get_users(names, ids_only=True, graceful=True)
	notify_users.update(user_ids)

	if SITE_NAME == "WPD" and (
		('daisy' in text and 'destruction' in text)
		or ('kill myself' in text and obj and isinstance(obj, Post))
		or word_alert_regex.search(text)
	):
		admin_ids = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS['NOTIFICATIONS_SPECIFIC_WPD_COMMENTS'], User.id != AEVANN_ID)]
		notify_users.update(admin_ids)

	if FEATURES['PING_GROUPS']:
		cost = 0
		cost_groups = []
		coin_receivers = set()

		for i in group_mention_regex.finditer(text):
			if oldtext and re.search(f'(?<![:/\w])!{i.group(1)}($|[^\w-])', oldtext):
				continue

			if re.search(f'^>.*?(?<![:/\w])!{i.group(1)}', text):
				continue

			if i.group(1) == 'focusgroup' and not v.admin_level:
				stop(403, "Only admins can mention !focusgroup")

			if i.group(1) == 'everyone':
				if chat:
					if not membership.is_mod:
						stop(403, "You need to be the chat owner or a mod to do that!")
					group = None
					member_ids = {x[0] for x in g.db.query(ChatMembership.user_id).filter_by(chat_id=chat.id).all()} - {v.id}
				else:
					if charge:
						cutoff = time.time() - 604800
						cost = g.db.query(User).filter(
									User.id != v.id,
									User.last_active > cutoff,
								).count() * 5

						if cost > v.coins + v.marseybux:
							stop(403, f"You need {cost} currency to mention these ping groups!")
						
						reason = "Group pinging cost (<code>!everyone</code>)"
						if chat:
							reason += f' in <a href="/chat/{chat.id}">{chat.name}'
						if obj:
							reason += f" on {obj.textlink}"
						v.charge_account('coins/marseybux', cost, reason)
						if obj:
							obj.ping_cost += cost
					return 'everyone'
			elif i.group(1) == 'jannies':
				group = None
				member_ids = {x[0] for x in g.db.query(User.id).filter(User.admin_level > 0)}
				if SITE == 'watchpeopledie.tv':
					member_ids.remove(AEVANN_ID)
			elif i.group(1) == 'holejannies':
				if not get_obj_hole(obj):
					stop(403, "!holejannies can only be used inside holes!")
				group = None
				member_ids = {x[0] for x in g.db.query(Mod.user_id).filter_by(hole=obj.hole)}
			elif i.group(1) == 'followers':
				if not followers_ping:
					stop(403, f"You can't use !followers in posts!")
				group = None
				member_ids = {x[0] for x in g.db.query(Follow.user_id).filter_by(target_id=v.id)}
			elif i.group(1) == 'commenters':
				if not commenters_ping_post_id:
					stop(403, "You can only use !commenters in comments made under posts!")
				group = None
				member_ids = {x[0] for x in g.db.query(User.id).join(Comment, Comment.author_id == User.id).filter(Comment.parent_post == commenters_ping_post_id)} - {v.id} #to force it to charge
			else:
				group = g.db.get(Group, i.group(1))
				if not group: continue
				member_ids = group.member_ids
				if chat:
					member_ids = {x[0] for x in g.db.query(ChatMembership.user_id).filter(
						ChatMembership.chat_id == chat.id,
						ChatMembership.user_id.in_(member_ids)
					).all()}

			members = member_ids - notify_users - BOT_IDs - v.all_twoway_blocks - v.muters

			notify_users.update(members)

			if charge:
				realghost = ghost and i.group(1) != 'ghosts'
				if (realghost or v.id not in member_ids) and i.group(1) != 'followers':
					if group and group.name == 'verifiedrich':
						stop(403, f"Only !verifiedrich members can mention it!")
					cost += len(members) * 5
					cost_groups.append(i.group(1))
					if cost > v.coins + v.marseybux:
						stop(403, f"You need {cost} currency to mention these ping groups!")

					if i.group(1) in {'biofoids','neofoids','jannies'}:
						coin_receivers.update(member_ids)

		if charge:
			if cost:
				reason = f"Group pinging cost (<code>!" + "</code>, <code>!".join(cost_groups) + "</code>)"
				if chat:
					reason += f' in <a href="/chat/{chat.id}">{chat.name}'
				if obj:
					reason += f" on {obj.textlink}"
				v.charge_account('coins/marseybux', cost, reason)
				if obj:
					obj.ping_cost += cost

			if coin_receivers:
				g.db.query(User).options(load_only(User.id)).filter(User.id.in_(coin_receivers)).update({ User.coins: User.coins + 5 })

			largest_ping_group_count = g.db.query(func.count(GroupMembership.group_name)).group_by(GroupMembership.group_name).order_by(func.count(GroupMembership.group_name).desc()).first()
			if largest_ping_group_count: largest_ping_group_count = largest_ping_group_count[0]
			else: largest_ping_group_count = 0
			max_ping_count = max(1000, largest_ping_group_count)
			if len(notify_users) > max_ping_count and v.admin_level < PERMS['POST_COMMENT_INFINITE_PINGS']:
				stop(403, f"You can only notify a maximum of {max_ping_count} users.")

	if v.shadowbanned or (obj and obj.is_banned):
		notify_users = {x[0] for x in g.db.query(User.id).filter(User.id.in_(notify_users), User.admin_level >= PERMS['USER_SHADOWBAN']).all()}

	return notify_users - BOT_IDs - {v.id, 0} - v.all_twoway_blocks - v.muters


def push_notif(uids, title, body, url_or_comment, chat_id=None):
	if VAPID_PUBLIC_KEY == DEFAULT_CONFIG_VALUE:
		return

	if hasattr(g, 'v') and g.v and g.v.shadowbanned:
		uids = [x[0] for x in g.db.query(User.id).filter(User.id.in_(uids), User.admin_level >= PERMS['USER_SHADOWBAN']).all()]
		if not uids:
			return

	# uids = set(uids)
	# if SITE == 'rdrama.net' and chat_id != 182 and '!jannies' not in body:
	# 	uids.discard(147)
	# 	uids.discard(11031)

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
					'icon': f'{SITE_FULL}/icon.webp?x=15',
					}),
				vapid_private_key=VAPID_PRIVATE_KEY,
				vapid_claims={"sub": f"mailto:{EMAIL}"}
			)
		except: continue

def alert_everyone(cid):
	cid = int(cid)
	t = int(time.time())
	cutoff = t - 604800
	_everyone_query = text(f"""
	insert into notifications
	select id, {cid}, false, {t} from users where id != {g.v.id} and last_active > {cutoff}
	on conflict do nothing;""")
	g.db.execute(_everyone_query)

def alert_admins(body):
	body_html = sanitize(body, blackjack="admin alert")

	new_comment = Comment(author_id=AUTOJANNY_ID,
						parent_post=None,
						level=1,
						body_html=body_html,
						sentto=MODMAIL_ID,
						distinguished=True,
						is_bot=True
						)
	g.db.add(new_comment)
	g.db.flush()

	new_comment.top_comment_id = new_comment.id

def alert_active_users(body, vid, extra_criteria):
	body_html = sanitize(body, blackjack="notification")
	cid = create_comment(body_html)
	cutoff = time.time() - 604800

	notified_users = [x[0] for x in g.db.query(User.id).filter(
			User.last_active > cutoff,
			User.id != vid,
			extra_criteria,
		)]
	for uid in notified_users:
		add_notif(cid, uid, body, check_existing=False)
