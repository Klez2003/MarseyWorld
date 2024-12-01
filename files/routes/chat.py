import time
import uuid
from hashlib import md5

from sqlalchemy.orm import load_only
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request

from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.slurs_and_profanities import censor_slurs_profanities
from files.helpers.regex import *
from files.helpers.media import *
from files.helpers.sanitize import *
from files.helpers.alerts import push_notif
from files.helpers.can_see import *
from files.routes.wrappers import *
from files.classes.orgy import *
from files.classes.chats import *

from files.__main__ import app, cache, limiter, db_session

from engineio.payload import Payload
Payload.max_decode_packets = 50

socketio = SocketIO(
	app,
	async_mode='gevent',
	max_http_buffer_size=16777216, #for images, audio, and video
)

muted = cache.get(f'muted') or {}
online = {"messages": set()}
typing = {}

cache.set('loggedin_chat', 0, timeout=86400)

def get_referrer():
	referrer = request.referrer
	if referrer:
		referrer = referrer.replace('https://redscarepod.net', 'https://rdrama.net')
		if '?m=' in referrer:
			referrer = referrer.split("?m=")[0]
	return referrer

def auth_required_socketio(f):
	def wrapper(*args, **kwargs):
		if not hasattr(g, 'db'): g.db = db_session()
		v = get_logged_in_user()
		if not v or v.is_permabanned:
			stop(403, "You can't perform this action while permabanned!")
		x = make_response(f(*args, v=v, **kwargs))
		try: g.db.commit()
		except: g.db.rollback()
		g.db.close()
		stdout.flush()
		return x
	wrapper.__name__ = f.__name__
	return wrapper

@app.post('/chat/<int:chat_id>/refresh_chat')
def refresh_chat(chat_id):
	emit('refresh_chat', namespace='/', to=f'{SITE_FULL}/chat/{chat_id}')
	return ''

@socketio.on('speak')
@auth_required_socketio
def speak(data, v):
	if SITE_NAME == 'WPD' and v.is_suspended:
		stop(403, "You can't send chat messages while banned!")

	try: chat_id = int(data['chat_id'])
	except: stop(403, "Invalid chat ID.")

	chat = g.db.get(Chat, chat_id)
	if not chat: stop(404, "Chat not found!")

	if chat.id == 1:
		if not v.allowed_in_chat: stop(403, "You don't have enough truescore to use this chat!")
		membership = None
	else:
		membership = g.db.query(ChatMembership.is_mod).filter_by(user_id=v.id, chat_id=chat_id).one_or_none()
		if not membership: stop(403, "You're not a member of this chat!")

	file = None
	if data['file']:
		if data['file_type'].startswith('image/'):
			name = f'/images/{time.time()}'.replace('.','') + '.webp'
			with open(name, 'wb') as f:
				f.write(data['file'])
			file = process_image(name, v)
		elif data['file_type'].startswith('video/'):
			name = f'/videos/{time.time()}'.replace('.','')
			with open(name, 'wb') as f:
				f.write(data['file'])
			file = process_video(name, v)[0]
		elif data['file_type'].startswith('audio/'):
			name = f'/audio/{time.time()}'.replace('.','')
			with open(name, 'wb') as f:
				f.write(data['file'])
			file = f'{SITE_FULL}{process_audio(name, v)}'

	text = data['message'].strip()[:1000]
	if file: text += f'\n\n{file}'
	if not text:
		stop(400, "You need to send something!")

	if chat.id == 1:
		vname = v.username.lower()
		if vname in muted:
			if time.time() < muted[vname]:
				minutes = (muted[vname] - time.time()) / 60
				stop(403, f"You're muted for the next {int(minutes)} minutes and can't send messages right now. Reflect on what you've done and be better!")
			else:
				del muted[vname]
				refresh_online(f'{SITE_FULL}/chat/1')
		if v.admin_level >= PERMS['CHAT_MUTE']:
			for i in mute_regex.finditer(text.lower()):
				username = i.group(1).lower()
				muted_until = int(int(i.group(2)) * 60 + time.time())
				muted[username] = muted_until
				refresh_online(f'{SITE_FULL}/chat/1')
			for i in unmute_regex.finditer(text.lower()):
				username = i.group(1).lower()
				muted.pop(username, None)
				refresh_online(f'{SITE_FULL}/chat/1')

	text_html = sanitize(text, count_emojis=True, chat=True)
	if len(text_html) > 5000:
		stop(400, "Rendered message is too long!")

	quotes = data['quotes']
	if quotes: quotes = int(quotes)
	else: quotes = None

	chat_message = ChatMessage(
		user_id=v.id,
		chat_id=chat_id,
		quotes=quotes,
		text=text,
		text_censored=censor_slurs_profanities(text, 'chat', True),
		text_html=text_html,
		text_html_censored=censor_slurs_profanities(text_html, 'chat'),
	)
	g.db.add(chat_message)
	g.db.flush()

	execute_blackjack(v, chat_message, text, "chat")
	execute_under_siege(v, chat_message, "chat")

	data = {
		"id": chat_message.id,
		"quotes": chat_message.quotes,
		"hat": chat_message.hat,
		"user_id": chat_message.user_id,
		"username": chat_message.username,
		"namecolor": chat_message.namecolor,
		"patron": chat_message.patron,
		"pride_username": chat_message.pride_username,
		"text": chat_message.text,
		"text_censored": chat_message.text_censored,
		"text_html": chat_message.text_html,
		"text_html_censored": chat_message.text_html_censored,
		"created_utc": chat_message.created_utc,
	}

	if chat.id != 1:
		if chat.membership_count == 2:
			notify_users = set(g.db.query(ChatMembership.user_id).filter(
				ChatMembership.chat_id == chat.id,
				ChatMembership.user_id != v.id,
			).one())
		else:
			notify_users = NOTIFY_USERS(chat_message.text, v, chat=chat, membership=membership)
			if notify_users == 'everyone':
				notify_users = set()
			if chat_message.quotes:
				quoted_user = g.db.get(User, chat_message.quoted_message.user_id)
				if not quoted_user.has_muted(v) and not quoted_user.has_blocked(v):
					notify_users.add(quoted_user.id)

	if v.shadowbanned:
		emit('speak', data)
	else:
		emit('speak', data, room=get_referrer())

	typing[get_referrer()] = []

	if membership and membership.is_mod:
		added_users = []
		for i in chat_adding_regex.finditer(text):
			user = get_user(i.group(1), graceful=True, attributes=[User.id])
			if user and not user.has_muted(v) and not user.has_blocked(v):
				existing = g.db.query(ChatMembership.user_id).filter_by(user_id=user.id, chat_id=chat_id).one_or_none()
				if not existing:
					chat_membership = ChatMembership(
						user_id=user.id,
						chat_id=chat_id,
					)
					g.db.add(chat_membership)
					g.db.flush()
					added_users.append((user.username, user.name_color, user.patron, user.id, bool(user.has_badge(303))))
		if added_users:
			emit("add", added_users, room=get_referrer())

		kicked_users = []
		for i in chat_kicking_regex.finditer(text):
			user = get_user(i.group(1), graceful=True, attributes=[User.id])
			if user:
				existing = g.db.query(ChatMembership).filter_by(user_id=user.id, chat_id=chat_id).one_or_none()
				if existing:
					g.db.delete(existing)
					g.db.flush()
					send_notification(user.id, f"@{v.username} kicked you from their chat [{chat.name}](/chat/{chat.id})")
					kicked_users.append(user.id)
		if kicked_users:
			emit("kick", kicked_users, room=get_referrer())

	if v.id == chat.owner_id:
		for i in chat_jannying_regex.finditer(text):
			user = get_user(i.group(1), graceful=True, attributes=[User.id])
			if user:
				existing = g.db.query(ChatMembership).filter_by(user_id=user.id, chat_id=chat_id, is_mod=False).one_or_none()
				if existing:
					existing.is_mod = True
					send_notification(user.id, f"@{v.username} has added you as a mod of their chat [{chat.name}](/chat/{chat.id})")

		for i in chat_dejannying_regex.finditer(text):
			user = get_user(i.group(2), graceful=True, attributes=[User.id])
			if user:
				existing = g.db.query(ChatMembership).filter_by(user_id=user.id, chat_id=chat_id, is_mod=True).one_or_none()
				if existing:
					existing.is_mod = False
					send_notification(user.id, f"@{v.username} has removed you as a mod of their chat [{chat.name}](/chat/{chat.id})")

	if chat.id != 1:
		alrdy_here = set(online[get_referrer()].keys())
		memberships = g.db.query(ChatMembership).options(load_only(ChatMembership.user_id)).filter(
			ChatMembership.chat_id == chat_id,
			ChatMembership.user_id.notin_(alrdy_here),
			ChatMembership.notification == False,
		)
		for membership in memberships:
			membership.notification = True
			g.db.add(membership)

		notify_users -= alrdy_here

		uids = {x.user_id for x in memberships if x.user_id not in notify_users}
		title = f'New messages in "{chat.name}"'
		body = ''
		url = f'{SITE_FULL}/chat/{chat.id}'
		push_notif(uids, title, body, url, chat_id=chat.id)

		if notify_users:
			memberships = g.db.query(ChatMembership).options(load_only(ChatMembership.user_id)).filter(
				ChatMembership.chat_id == chat_id,
				ChatMembership.user_id.in_(notify_users),
			)
			for membership in memberships:
				membership.mentions += 1
				g.db.add(membership)

			uids = {x.user_id for x in memberships}
			title = f'New mention of you in "{chat.name}"'
			body = chat_message.text
			url = f'{SITE_FULL}/chat/{chat.id}#{chat_message.id}'
			push_notif(uids, title, body, url, chat_id=chat.id)

	return ''

def refresh_online(room):
	for k, val in list(online[room].items()):
		if time.time() > val[0]:
			del online[room][k]
			if val[1] in typing[room]:
				typing[room].remove(val[1])

	data = [list(online[room].values()), muted]
	emit("online", data, room=room)
	if room == f'{SITE_FULL}/chat/1':
		cache.set('loggedin_chat', len(online[room]), timeout=86400)

@socketio.on('connect')
@auth_required_socketio
def connect(v):
	if not get_referrer(): stop(400, "Invalid referrer!")
	room = get_referrer()

	if room.startswith(f'{SITE_FULL}/notifications/messages'):
		join_room(v.id)
		online["messages"].add(v.id)
		return ''

	join_room(room)

	if not online.get(room):
		online[room] = {}

	if not typing.get(room):
		typing[room] = []

	if v.username in typing.get(room):
		typing[room].remove(v.username)

	emit('typing', typing[room], room=room)

	return ''

@socketio.on('disconnect')
@auth_required_socketio
def disconnect(v):
	if not get_referrer(): stop(400, "Invalid referrer!")
	room = get_referrer()

	if room.startswith(f'{SITE_FULL}/notifications/messages'):
		leave_room(v.id)
		online["messages"].discard(v.id)
		return ''

	if online.get(room):
		online[room].pop(v.id, None)

	if v.username in typing[room]:
		typing[room].remove(v.username)

	leave_room(room)

	if online.get(room):
		refresh_online(room)

	return ''

@socketio.on('heartbeat')
@auth_required_socketio
def heartbeat(v):
	if not get_referrer(): stop(400, "Invalid referrer!")
	room = get_referrer()

	if not online.get(room):
		online[room] = {}

	expire_utc = int(time.time()) + 3610
	already_there = online[room].get(v.id)
	online[room][v.id] = (expire_utc, v.username, v.name_color, v.patron, v.id, bool(v.has_badge(303)))
	if not already_there:
		refresh_online(room)

	return ''

@socketio.on('typing')
@auth_required_socketio
def typing_indicator(data, v):
	if v.is_suspended or v.shadowbanned: return ''
	
	if not get_referrer(): stop(400, "Invalid referrer!")
	room = get_referrer()

	if not typing.get(room):
		typing[room] = []

	if data and v.username not in typing[room]:
		typing[room].append(v.username)
	elif not data and v.username in typing[room]:
		typing[room].remove(v.username)

	emit('typing', typing[room], room=room)

	return ''


@socketio.on('delete')
@auth_required_socketio
def delete(id, v):
	if v.admin_level < PERMS['POST_COMMENT_MODERATION']:
		stop(400, "Your admin-level is not sufficient enough for this action!")

	for msg in g.db.query(ChatMessage).filter_by(quotes=id):
		msg.quotes = None
		g.db.add(msg)

	message = g.db.get(ChatMessage, id)
	g.db.delete(message)
	emit('delete', id, room=f'{SITE_FULL}/chat/1')

	return ''


@app.post("/reply")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("6/minute;50/hour;200/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("6/minute;50/hour;200/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def messagereply(v):
	body = request.values.get("body", "").strip()
	if len(body) > COMMENT_BODY_LENGTH_LIMIT:
		stop(400, f'Message is too long (max {COMMENT_BODY_LENGTH_LIMIT} characters)')

	id = request.values.get("parent_id")
	parent = get_comment(id, v=v)

	if parent.parent_post or parent.wall_user_id:
		stop(403, "You can only reply to messages!")

	user_id = parent.author.id

	if v.is_permabanned and parent.sentto != MODMAIL_ID:
		stop(403, "You are permabanned and may not reply to messages!")
	elif v.is_muted and parent.sentto == MODMAIL_ID:
		stop(403, "You are muted!")

	if parent.sentto == MODMAIL_ID: user_id = None
	elif v.id == user_id: user_id = parent.sentto

	user = None

	if user_id:
		user = get_account(user_id, v=v, include_blocks=True)
		if hasattr(user, 'is_blocking') and user.is_blocking:
			stop(403, f"You're blocking @{user.username}")
		elif (v.admin_level < PERMS['MESSAGE_BLOCKED_USERS']
				and hasattr(user, 'is_blocked') and user.is_blocked):
			stop(403, f"You're blocked by @{user.username}")

		if v.admin_level < PERMS['MESSAGE_BLOCKED_USERS'] and user.has_muted(v):
			stop(403, f"@{user.username} is muting notifications from you, so messaging them is pointless!")

	if not g.is_tor and get_setting("dm_media"):
		body = process_files(request.files, v, body, is_dm=True, dm_user=user)
		if len(body) > COMMENT_BODY_LENGTH_LIMIT:
			stop(400, f'Message is too long (max {COMMENT_BODY_LENGTH_LIMIT} characters)')

	if not body: stop(400, "Message is empty!")

	body_html = sanitize(body)

	if len(body_html) > COMMENT_BODY_HTML_LENGTH_LIMIT:
		stop(400, "Rendered message is too long!")

	if parent.sentto == MODMAIL_ID:
		sentto = MODMAIL_ID
	else:
		sentto = user_id

	c = Comment(author_id=v.id,
							parent_post=None,
							parent_comment_id=id,
							top_comment_id=parent.top_comment_id,
							level=parent.level + 1,
							sentto=sentto,
							body=body,
							body_html=body_html,
							)
	g.db.add(c)
	g.db.flush()
	kind = 'modmail' if sentto == MODMAIL_ID else 'message'
	execute_blackjack(v, c, c.body_html, kind)
	execute_under_siege(v, c, kind)

	if user_id and user_id not in {v.id, MODMAIL_ID} | BOT_IDs and user_id not in online["messages"] and can_see(user, v):
		notif = g.db.query(Notification).filter_by(comment_id=c.id, user_id=user_id).one_or_none()
		if not notif:
			notif = Notification(comment_id=c.id, user_id=user_id)
			g.db.add(notif)

		title = f'New message from @{c.author_name}'
		url = f'{SITE_FULL}/notifications/messages'
		push_notif({user_id}, title, body, url)

	top_comment = c.top_comment

	if top_comment.sentto == MODMAIL_ID:
		if parent.author.id != v.id and parent.author.admin_level < PERMS['VIEW_MODMAIL']:
			notif = Notification(comment_id=c.id, user_id=parent.author.id)
			g.db.add(notif)
	elif user_id and user_id not in {v.id, MODMAIL_ID} | BOT_IDs:
		c.unread = True
		rendered = render_template("comments.html", v=get_account(user_id), comments=[c])
		emit('insert_reply', [parent.id, rendered], namespace='/', to=user_id)

	return {"comment": render_template("comments.html", v=v, comments=[c])}
