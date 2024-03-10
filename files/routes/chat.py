import atexit
import time
import uuid
from hashlib import md5

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
from files.classes.private_chats import *

from files.__main__ import app, cache, limiter

from engineio.payload import Payload
Payload.max_decode_packets = 50

socketio = SocketIO(
	app,
	async_mode='gevent',
	max_http_buffer_size=8388608, #for images
)

muted = cache.get(f'muted') or {}

messages = cache.get(f'messages') or {}

online = {
	"chat": {},
	"messages": set()
}

typing = {
	"chat": []
}

cache.set('loggedin_chat', len(online["chat"]), timeout=86400)

def auth_required_socketio(f):
	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		if not v or v.is_permabanned: return ''
		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

def is_not_banned_socketio(f):
	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		if not v or v.is_suspended: return ''
		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

CHAT_ERROR_MESSAGE = f"To prevent spam, you'll need {TRUESCORE_MINIMUM} truescore (this is {TRUESCORE_MINIMUM} votes, either up or down, on any threads or comments you've made) in order to access chat. Sorry! I love you 💖"

@app.post('/refresh_chat')
def refresh_chat():
	emit('refresh_chat', namespace='/', to="chat")
	return ''

@app.get("/chat/")
def chat_redirect():
	return redirect("/chat")

@app.get("/chat")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def chat(v):
	if not v.allowed_in_chat:
		abort(403, CHAT_ERROR_MESSAGE)

	displayed_messages = {k: val for k, val in messages.items() if val["user_id"] not in v.userblocks}

	orgy = get_running_orgy(v)
	if orgy:
		x = secrets.token_urlsafe(8)
		orgies = g.db.query(Orgy).order_by(Orgy.start_utc).all()
		return render_template("orgy.html", v=v, messages=displayed_messages, orgy=orgy, x=x, orgies=orgies)

	return render_template("chat.html", v=v, messages=displayed_messages)

@socketio.on('speak')
@is_not_banned_socketio
def speak(data, v):
	if request.referrer.startswith(f'{SITE_FULL}/chat/'):
		chat_id = int(data['chat_id'])

		chat = g.db.get(Chat, chat_id)
		if not chat:
			abort(404, "Chat not found!")

		is_member = g.db.query(ChatMembership.user_id).filter_by(user_id=v.id, chat_id=chat_id).one_or_none()
		if not is_member: return ''

		image = None
		if data['file']:
			name = f'/chat_images/{time.time()}'.replace('.','') + '.webp'
			with open(name, 'wb') as f:
				f.write(data['file'])
			image = process_image(name, v)

		text = data['message'].strip()[:CHAT_LENGTH_LIMIT]
		if image: text += f'\n\n{image}'
		if not text: return ''

		text_html = sanitize(text, count_emojis=True, chat=True)
		if isinstance(text_html , tuple): return ''

		execute_under_siege(v, None, text, "private chat")

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

		if v.id == chat.owner_id:
			if chat_adding_regex.fullmatch(text):
				user = get_user(text[2:], graceful=True, attributes=[User.id])
				if user and not user.has_muted(v) and not user.has_blocked(v):
					existing = g.db.query(ChatMembership.user_id).filter_by(user_id=user.id, chat_id=chat_id).one_or_none()
					leave = g.db.query(ChatLeave.user_id).filter_by(user_id=user.id, chat_id=chat_id).one_or_none()
					if not existing and not leave:
						chat_membership = ChatMembership(
							user_id=user.id,
							chat_id=chat_id,
						)
						g.db.add(chat_membership)
						g.db.flush()
			elif chat_kicking_regex.fullmatch(text):
				user = get_user(text[2:], graceful=True, attributes=[User.id])
				if user:
					existing = g.db.query(ChatMembership).filter_by(user_id=user.id, chat_id=chat_id).one_or_none()
					if existing:
						g.db.delete(existing)
						g.db.flush()

		to_notify = [x[0] for x in g.db.query(ChatMembership.user_id).filter(
			ChatMembership.chat_id == chat_id,
			ChatMembership.user_id.notin_(online[request.referrer]),
		)]
		for uid in to_notify:
			n = ChatNotification(
				user_id=uid,
				chat_message_id=chat_message.id,
				chat_id=chat_id,
			)
			g.db.add(n)

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

		if v.shadowbanned or execute_blackjack(v, None, text, "chat"):
			emit('speak', data)
		else:
			emit('speak', data, room=request.referrer, broadcast=True)

		try: g.db.commit()
		except: g.db.rollback()
		g.db.close()
		stdout.flush()

		return ''



	if not v.allowed_in_chat: return ''

	image = None
	if data['file']:
		name = f'/chat_images/{time.time()}'.replace('.','') + '.webp'
		with open(name, 'wb') as f:
			f.write(data['file'])
		image = process_image(name, v)

	global messages

	text = data['message'].strip()[:CHAT_LENGTH_LIMIT]
	if image: text += f'\n\n{image}'
	if not text: return ''

	text_html = sanitize(text, count_emojis=True, chat=True)
	if isinstance(text_html , tuple): return ''

	execute_under_siege(v, None, text, "chat")

	quotes = data['quotes']
	id = secrets.token_urlsafe(5)

	self_only = False

	vname = v.username.lower()
	if vname in muted:
		if time.time() < muted[vname]:
			self_only = True
		else:
			del muted[vname]
			refresh_online("chat")

	if SITE == 'rdrama.net' and v.admin_level < PERMS['BYPASS_ANTISPAM_CHECKS']:
		def shut_up():
			self_only = True
			muted_until = int(time.time() + 600)
			muted[vname] = muted_until
			refresh_online("chat")

		if not self_only:
			identical = [x for x in list(messages.values())[-5:] if v.id == x['user_id'] and text == x['text']]
			if len(identical) >= 3: shut_up()

		if not self_only:
			count = len([x for x in list(messages.values())[-12:] if v.id == x['user_id']])
			if count >= 10: shut_up()

		if not self_only:
			count = len([x for x in list(messages.values())[-25:] if v.id == x['user_id']])
			if count >= 20: shut_up()

	data = {
		"id": id,
		"quotes": quotes if messages.get(quotes) else '',
		"hat": v.hat_active(None)[0],
		"user_id": v.id,
		"username": v.username,
		"namecolor": v.name_color,
		"patron": v.patron,
		"pride_username": bool(v.has_badge(303)),
		"text": text,
		"text_censored": censor_slurs_profanities(text, 'chat', True),
		"text_html": text_html,
		"text_html_censored": censor_slurs_profanities(text_html, 'chat'),
		"created_utc": int(time.time()),
	}


	if v.admin_level >= PERMS['USER_BAN']:
		text = text.lower()
		for i in mute_regex.finditer(text):
			username = i.group(1).lower()
			muted_until = int(int(i.group(2)) * 60 + time.time())
			muted[username] = muted_until
			refresh_online("chat")

	if self_only or v.shadowbanned or execute_blackjack(v, None, text, "chat"):
		emit('speak', data)
	else:
		emit('speak', data, room="chat", broadcast=True)
		messages[id] = data
		messages = dict(list(messages.items())[-250:])

	typing["chat"] = []

	return ''

def refresh_online(room):
	for k, val in list(online[room].items()):
		if time.time() > val[0]:
			del online[room][k]
			if val[1] in typing[room]:
				typing[room].remove(val[1])

	data = [list(online[room].values()), muted]
	emit("online", data, room=room, broadcast=True)
	cache.set('loggedin_chat', len(online[room]), timeout=86400)

@socketio.on('connect')
@auth_required_socketio
def connect(v):
	if request.referrer == f'{SITE_FULL}/notifications/messages':
		join_room(v.id)
		online["messages"].add(v.id)
		return ''

	if request.referrer and request.referrer.startswith(f'{SITE_FULL}/chat/'):
		room = request.referrer
	else:
		room = "chat"

	join_room(room)

	if not typing.get(room):
		typing[room] = []

	if v.username in typing.get(room):
		typing[room].remove(v.username)

	emit('typing', typing[room], room=room)
	return ''

@socketio.on('disconnect')
@auth_required_socketio
def disconnect(v):
	if request.referrer == f'{SITE_FULL}/notifications/messages':
		leave_room(v.id)
		online["messages"].remove(v.id)
		return ''

	if request.referrer and request.referrer.startswith(f'{SITE_FULL}/chat/'):
		room = request.referrer
	else:
		room = "chat"

	online[room].pop(v.id, None)

	if v.username in typing[room]:
		typing[room].remove(v.username)

	leave_room(room)
	refresh_online(room)

	return ''

@socketio.on('heartbeat')
@auth_required_socketio
def heartbeat(v):
	if request.referrer and request.referrer.startswith(f'{SITE_FULL}/chat/'):
		room = request.referrer
	else:
		room = "chat"

	if not online.get(room):
		online[room] = {}

	expire_utc = int(time.time()) + 3610
	already_there = online[room].get(v.id)
	online[room][v.id] = (expire_utc, v.username, v.name_color, v.patron, v.id, bool(v.has_badge(303)))
	if not already_there:
		refresh_online(room)

	return ''

@socketio.on('typing')
@is_not_banned_socketio
def typing_indicator(data, v):
	if request.referrer and request.referrer.startswith(f'{SITE_FULL}/chat/'):
		room = request.referrer
	else:
		room = "chat"

	if not typing.get(room):
		typing[room] = []

	if data and v.username not in typing[room]:
		typing[room].append(v.username)
	elif not data and v.username in typing[room]:
		typing[room].remove(v.username)

	emit('typing', typing[room], room=room, broadcast=True)
	return ''


@socketio.on('delete')
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def delete(id, v):
	messages.pop(id, None)
	emit('delete', id, room="chat", broadcast=True)
	return ''


def close_running_threads():
	cache.set('messages', messages, timeout=86400)
	cache.set('muted', muted, timeout=86400)
atexit.register(close_running_threads)


@app.post("/reply")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("6/minute;50/hour;200/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("6/minute;50/hour;200/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def messagereply(v):
	body = request.values.get("body", "").strip()
	if len(body) > COMMENT_BODY_LENGTH_LIMIT:
		abort(400, f'Message is too long (max {COMMENT_BODY_LENGTH_LIMIT} characters)')

	id = request.values.get("parent_id")
	parent = get_comment(id, v=v)

	if parent.parent_post or parent.wall_user_id:
		abort(403, "You can only reply to messages!")

	user_id = parent.author.id

	if v.is_permabanned and parent.sentto != MODMAIL_ID:
		abort(403, "You are permabanned and may not reply to messages!")
	elif v.is_muted and parent.sentto == MODMAIL_ID:
		abort(403, "You are muted!")

	if parent.sentto == MODMAIL_ID: user_id = None
	elif v.id == user_id: user_id = parent.sentto

	user = None

	if user_id:
		user = get_account(user_id, v=v, include_blocks=True)
		if hasattr(user, 'is_blocking') and user.is_blocking:
			abort(403, f"You're blocking @{user.username}")
		elif (v.admin_level <= PERMS['MESSAGE_BLOCKED_USERS']
				and hasattr(user, 'is_blocked') and user.is_blocked):
			abort(403, f"You're blocked by @{user.username}")

		if user.has_muted(v):
			abort(403, f"@{user.username} is muting notifications from you, so messaging them is pointless!")

	if not g.is_tor and get_setting("dm_media"):
		body = process_files(request.files, v, body, is_dm=True, dm_user=user)
		if len(body) > COMMENT_BODY_LENGTH_LIMIT:
			abort(400, f'Message is too long (max {COMMENT_BODY_LENGTH_LIMIT} characters)')

	if not body: abort(400, "Message is empty!")

	body_html = sanitize(body)

	if len(body_html) > COMMENT_BODY_HTML_LENGTH_LIMIT:
		abort(400, "Rendered message is too long!")

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
	execute_blackjack(v, c, c.body_html, 'message')
	execute_under_siege(v, c, c.body_html, 'message')

	if user_id and user_id not in {v.id, MODMAIL_ID} | BOT_IDs and user_id not in online["messages"]:
		if can_see(user, v):
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
