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
from files.routes.wrappers import *
from files.classes.orgy import *

from files.__main__ import app, cache, limiter

socketio = SocketIO(
	app,
	async_mode='gevent',
	max_http_buffer_size=8388608,
)

muted = cache.get(f'muted') or {}

ALLOWED_REFERRERS = {
	f'{SITE_FULL}/chat',
	f'{SITE_FULL}/notifications/messages',
}

messages = cache.get(f'messages') or {
	f'{SITE_FULL}/chat': {},
}
typing = {
	f'{SITE_FULL}/chat': [],
}
online = {
	f'{SITE_FULL}/chat': [],
}

cache.set('loggedin_chat', len(online[f'{SITE_FULL}/chat']), timeout=0)

def auth_required_socketio(f):
	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		if not v: return '', 401
		if v.is_permabanned: return '', 403
		if request.referrer:
			g.referrer = request.referrer.split('?')[0]
		else:
			g.referrer = None
		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

def is_not_banned_socketio(f):
	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		if not v: return '', 401
		if v.is_suspended: return '', 403
		if request.referrer:
			g.referrer = request.referrer.split('?')[0]
		else:
			g.referrer = None
		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

CHAT_ERROR_MESSAGE = f"To prevent spam, you'll need {TRUESCORE_CC_CHAT_MINIMUM} truescore (this is {TRUESCORE_CC_CHAT_MINIMUM} votes, either up or down, on any threads or comments you've made) in order to access chat. Sorry! I love you 💖"

@app.post('/refresh_chat')
def refresh_chat():
	emit('refresh_chat', namespace='/', to=f'{SITE_FULL}/chat')
	return ''

@app.get("/chat")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def chat(v):
	if not v.allowed_in_chat:
		abort(403, CHAT_ERROR_MESSAGE)

	displayed_messages = {k: val for k, val in messages[f"{SITE_FULL}/chat"].items() if val["user_id"] not in v.userblocks}

	orgy = get_orgy(v)
	if orgy:
		m = md5()
		with open('files/assets/subtitles.vtt', "rb") as f:
			data = f.read()
		m.update(data)
		subtitles_hash = m.hexdigest()

		return render_template("orgy.html", v=v, messages=displayed_messages, orgy=orgy, subtitles_hash=subtitles_hash)

	return render_template("chat.html", v=v, messages=displayed_messages)

@socketio.on('speak')
@is_not_banned_socketio
def speak(data, v):
	if g.referrer not in ALLOWED_REFERRERS:
		return '', 400

	image = None
	if data['file']:
		name = f'/chat_images/{time.time()}'.replace('.','') + '.webp'
		with open(name, 'wb') as f:
			f.write(data['file'])
		image = process_image(name, v)

	if not v.allowed_in_chat:
		return '', 403

	global messages

	text = data['message'][:CHAT_LENGTH_LIMIT]
	if image: text += f'\n\n{image}'
	if not text: return '', 400

	text_html = sanitize(text, count_emojis=True, chat=True)
	if isinstance(text_html , tuple):
		return text_html

	quotes = data['quotes']
	id = secrets.token_urlsafe(5)

	self_only = False

	vname = v.username.lower()
	if vname in muted:
		if time.time() < muted[vname]:
			self_only = True
		else:
			del muted[vname]
			emit("online", [online[g.referrer], muted], room=g.referrer, broadcast=True)

	if SITE == 'rdrama.net' and v.admin_level < PERMS['BYPASS_ANTISPAM_CHECKS']:
		def shut_up():
			self_only = True
			muted_until = int(time.time() + 600)
			muted[vname] = muted_until
			emit("online", [online[g.referrer], muted], room=g.referrer, broadcast=True)

		if not self_only:
			identical = [x for x in list(messages[g.referrer].values())[-5:] if v.id == x['user_id'] and text == x['text']]
			if len(identical) >= 3: shut_up()

		if not self_only:
			count = len([x for x in list(messages[g.referrer].values())[-12:] if v.id == x['user_id']])
			if count >= 10: shut_up()

		if not self_only:
			count = len([x for x in list(messages[g.referrer].values())[-25:] if v.id == x['user_id']])
			if count >= 20: shut_up()

	data = {
		"id": id,
		"quotes": quotes if messages[g.referrer].get(quotes) else '',
		"hat": v.hat_active(v)[0],
		"user_id": v.id,
		"username": v.username,
		"namecolor": v.name_color,
		"patron": v.patron,
		"text": text,
		"text_censored": censor_slurs_profanities(text, 'chat', True),
		"text_html": text_html,
		"text_html_censored": censor_slurs_profanities(text_html, 'chat'),
		"time": int(time.time()),
	}


	if v.admin_level >= PERMS['USER_BAN']:
		text = text.lower()
		for i in mute_regex.finditer(text):
			username = i.group(1).lower()
			muted_until = int(int(i.group(2)) * 60 + time.time())
			muted[username] = muted_until
			emit("online", [online[g.referrer], muted], room=g.referrer, broadcast=True)
			self_only = True

	if self_only or v.shadowbanned or execute_blackjack(v, None, text, "chat"):
		emit('speak', data)
	else:
		emit('speak', data, room=g.referrer, broadcast=True)
		messages[g.referrer][id] = data
		messages[g.referrer] = dict(list(messages[g.referrer].items())[-250:])

	typing = []

	return '', 204

def refresh_online():
	emit("online", [online[g.referrer], muted], room=g.referrer, broadcast=True)
	cache.set('loggedin_chat', len(online[f'{SITE_FULL}/chat']), timeout=0)

def remove_from_online(v):
	for li in online.values():
		for entry in li:
			if entry[0] == v.id:
				li.remove(entry)

@socketio.on('connect')
@auth_required_socketio
def connect(v):
	if g.referrer not in ALLOWED_REFERRERS:
		return '', 400

	if g.referrer == f'{SITE_FULL}/notifications/messages':
		join_room(v.id)
		return ''

	join_room(g.referrer)

	remove_from_online(v)

	online[g.referrer].append([v.id, v.username, v.name_color, v.patron])

	refresh_online()

	emit('typing', typing[g.referrer], room=g.referrer)
	return '', 204

@socketio.on('disconnect')
@auth_required_socketio
def disconnect(v):
	if g.referrer != f'{SITE_FULL}/notifications/messages':
		remove_from_online(v)

	if g.referrer not in ALLOWED_REFERRERS:
		return '', 400
	elif g.referrer == f'{SITE_FULL}/notifications/messages':
		leave_room(v.id)
	else:
		leave_room(g.referrer)
		refresh_online()

	return '', 204

@socketio.on('typing')
@is_not_banned_socketio
def typing_indicator(data, v):
	if g.referrer not in ALLOWED_REFERRERS:
		return '', 400

	if data and v.username not in typing[g.referrer]:
		typing[g.referrer].append(v.username)
	elif not data and v.username in typing[g.referrer]:
		typing[g.referrer].remove(v.username)

	emit('typing', typing[g.referrer], room=g.referrer, broadcast=True)
	return '', 204


@socketio.on('delete')
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def delete(id, v):
	if g.referrer not in ALLOWED_REFERRERS:
		return '', 400

	for k, val in messages[g.referrer].items():
		if k == id:
			del messages[g.referrer][k]
			break

	emit('delete', id, room=g.referrer, broadcast=True)

	return '', 204


def close_running_threads():
	cache.set('messages', messages)
	cache.set('muted', muted)
atexit.register(close_running_threads)


@app.post("/reply")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("6/minute;50/hour;200/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("6/minute;50/hour;200/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def messagereply(v):
	body = request.values.get("body", "")
	body = body[:COMMENT_BODY_LENGTH_LIMIT].strip()

	id = request.values.get("parent_id")
	parent = get_comment(id, v=v)

	if parent.parent_post or parent.wall_user_id:
		abort(403, "You can only reply to messages!")

	user_id = parent.author.id

	if v.is_permabanned and parent.sentto != MODMAIL_ID:
		abort(403, "You are permabanned and may not reply to messages!")
	elif v.is_muted and parent.sentto == MODMAIL_ID:
		abort(403, "You are forbidden from replying to modmail!")

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
		body = body[:COMMENT_BODY_LENGTH_LIMIT].strip() #process_files potentially adds characters to the post

	if not body: abort(400, "Message is empty!")

	body_html = sanitize(body)

	if len(body_html) > COMMENT_BODY_HTML_LENGTH_LIMIT:
		abort(400, "Message too long!")

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

	if user_id and user_id not in {v.id, MODMAIL_ID} | BOT_IDs:
		notif = g.db.query(Notification).filter_by(comment_id=c.id, user_id=user_id).one_or_none()
		if not notif:
			notif = Notification(comment_id=c.id, user_id=user_id)
			g.db.add(notif)

		title = f'New message from @{c.author_name}'

		url = f'{SITE_FULL}/notifications/messages'

		push_notif({user_id}, title, body, url)

	top_comment = c.top_comment

	if top_comment.sentto == MODMAIL_ID:
		admin_ids = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS['NOTIFICATIONS_MODMAIL'], User.id != v.id)]

		if SITE == 'watchpeopledie.tv':
			if AEVANN_ID in admin_ids:
				admin_ids.remove(AEVANN_ID)
			if 'delete' in top_comment.body.lower() and 'account' in top_comment.body.lower():
				admin_ids.remove(15447)

		if parent.author.id not in admin_ids + [v.id]:
			admin_ids.append(parent.author.id)

		#Don't delete unread notifications, so the replies don't get collapsed and they get highlighted
		ids = [top_comment.id] + [x.id for x in top_comment.replies(sort="old")]
		notifications = g.db.query(Notification).filter(Notification.read == True, Notification.comment_id.in_(ids), Notification.user_id.in_(admin_ids))
		for n in notifications:
			g.db.delete(n)

		for admin in admin_ids:
			notif = Notification(comment_id=c.id, user_id=admin)
			g.db.add(notif)
	elif user_id and user_id not in {v.id, MODMAIL_ID} | BOT_IDs:
		c.unread = True
		rendered = render_template("comments.html", v=get_account(user_id), comments=[c])
		emit('insert_reply', [parent.id, rendered], namespace='/', to=user_id)

	return {"comment": render_template("comments.html", v=v, comments=[c])}
