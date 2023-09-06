import atexit
import time
import uuid

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request

from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.config.const import *
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

sessions = []
muted = cache.get(f'muted') or {}

ALLOWED_REFERRERS = {f'{SITE_FULL}/chat', f'{SITE_FULL}/orgy'}

messages = cache.get(f'messages') or {
	f'{SITE_FULL}/chat': {},
	f'{SITE_FULL}/orgy': {},
}
typing = {
	f'{SITE_FULL}/chat': [],
	f'{SITE_FULL}/orgy': [],
}
online = {
	f'{SITE_FULL}/chat': [],
	f'{SITE_FULL}/orgy': [],
}

cache.set(CHAT_ONLINE_CACHE_KEY, len(online[f'{SITE_FULL}/chat']), timeout=0)

def is_not_banned_socketio(f):
	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		if not v: return '', 401
		if v.is_suspended: return '', 403
		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

def is_not_permabanned_socketio(f):
	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		if not v: return '', 401
		if v.is_permabanned: return '', 403
		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

CHAT_ERROR_MESSAGE = f"To prevent spam, you'll need {TRUESCORE_CC_CHAT_MINIMUM} truescore (this is {TRUESCORE_CC_CHAT_MINIMUM} votes, either up or down, on any threads or comments you've made) in order to access chat. Sorry! I love you 💖"

@app.get("/chat")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@is_not_permabanned
def chat(v):
	if not v.allowed_in_chat:
		abort(403, CHAT_ERROR_MESSAGE)

	displayed_messages = {k: val for k, val in messages[f"{SITE_FULL}/chat"].items() if val["user_id"] not in v.userblocks}

	return render_template("chat.html", v=v, messages=displayed_messages)

@app.get("/orgy")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@is_not_permabanned
def orgy(v):
	if not v.allowed_in_chat:
		abort(403, CHAT_ERROR_MESSAGE)

	orgy = get_orgy()

	if not orgy:
		abort(404, "An orgy isn't currently in progress!")

	displayed_messages = {k: val for k, val in messages[f"{SITE_FULL}/orgy"].items() if val["user_id"] not in v.userblocks}

	return render_template("orgy.html", v=v, messages=displayed_messages, orgy=orgy, site=SITE)

@socketio.on('speak')
@is_not_banned_socketio
def speak(data, v):
	if request.referrer not in ALLOWED_REFERRERS:
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
	id = str(uuid.uuid4())

	self_only = False

	vname = v.username.lower()
	if vname in muted:
		if time.time() < muted[vname]:
			self_only = True
		else:
			del muted[vname]
			emit("online", [online[request.referrer], muted], room=request.referrer, broadcast=True)

	if SITE == 'rdrama.net':
		def shut_up():
			self_only = True
			muted_until = int(time.time() + 600)
			muted[vname] = muted_until
			emit("online", [online[request.referrer], muted], room=request.referrer, broadcast=True)

		if not self_only:
			identical = [x for x in list(messages[request.referrer].values())[-5:] if v.id == x['user_id'] and text == x['text']]
			if len(identical) >= 3: shut_up()

		if not self_only:
			count = len([x for x in list(messages[request.referrer].values())[-12:] if v.id == x['user_id']])
			if count >= 10: shut_up()

		if not self_only:
			count = len([x for x in list(messages[request.referrer].values())[-25:] if v.id == x['user_id']])
			if count >= 20: shut_up()

	data = {
		"id": id,
		"quotes": quotes if messages[request.referrer].get(quotes) else '',
		"hat": v.hat_active(v)[0],
		"user_id": v.id,
		"username": v.username,
		"namecolor": v.name_color,
		"patron": v.patron,
		"text": text,
		"text_censored": censor_slurs(text, 'chat'),
		"text_html": text_html,
		"text_html_censored": censor_slurs(text_html, 'chat'),
		"time": int(time.time()),
	}


	if v.admin_level >= PERMS['USER_BAN']:
		text = text.lower()
		for i in mute_regex.finditer(text):
			username = i.group(1).lower()
			muted_until = int(int(i.group(2)) * 60 + time.time())
			muted[username] = muted_until
			emit("online", [online[request.referrer], muted], room=request.referrer, broadcast=True)
			self_only = True

	if self_only or v.shadowbanned or execute_blackjack(v, None, text, "chat"):
		emit('speak', data)
	else:
		emit('speak', data, room=request.referrer, broadcast=True)
		messages[request.referrer][id] = data
		messages[request.referrer] = dict(list(messages[request.referrer].items())[-250:])

	typing = []

	return '', 204

def refresh_online():
	emit("online", [online[request.referrer], muted], room=request.referrer, broadcast=True)
	if request.referrer == f'{SITE_FULL}/chat':
		cache.set(CHAT_ONLINE_CACHE_KEY, len(online[f'{SITE_FULL}/chat']), timeout=0)

@socketio.on('connect')
@is_not_permabanned_socketio
def connect(v):
	if request.referrer not in ALLOWED_REFERRERS:
		return '', 400

	join_room(request.referrer)

	if any(v.id in session for session in sessions) and [v.username, v.id, v.name_color, v.patron] not in online[request.referrer]:
		# user has previous running sessions with a different username or name_color
		for val in online.values():
			if [v.username, v.id, v.name_color, v.patron] in val:
				val.remove([v.username, v.id, v.name_color, v.patron])

	sessions.append([v.id, request.sid])
	if [v.username, v.id, v.name_color, v.patron] not in online[request.referrer]:
		online[request.referrer].append([v.username, v.id, v.name_color, v.patron])

	refresh_online()

	emit('typing', typing[request.referrer], room=request.referrer)
	return '', 204

@socketio.on('disconnect')
@is_not_permabanned_socketio
def disconnect(v):
	if request.referrer not in ALLOWED_REFERRERS:
		return '', 400

	leave_room(request.referrer)

	if ([v.id, request.sid]) in sessions:
		sessions.remove([v.id, request.sid])
		if any(v.id in session for session in sessions):
			# user has other running sessions
			return '', 204

	for val in online.values():
		if [v.username, v.id, v.name_color, v.patron] in val:
			val.remove([v.username, v.id, v.name_color, v.patron])

	for val in typing.values():
		if v.username in val:
			val.remove(v.username)

	refresh_online()
	
	return '', 204

@socketio.on('typing')
@is_not_banned_socketio
def typing_indicator(data, v):
	if request.referrer not in ALLOWED_REFERRERS:
		return '', 400

	if data and v.username not in typing[request.referrer]:
		typing[request.referrer].append(v.username)
	elif not data and v.username in typing[request.referrer]:
		typing[request.referrer].remove(v.username)

	emit('typing', typing[request.referrer], room=request.referrer, broadcast=True)
	return '', 204


@socketio.on('delete')
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def delete(id, v):
	if request.referrer not in ALLOWED_REFERRERS:
		return '', 400

	for k, val in messages[request.referrer].items():
		if k == id:
			del messages[request.referrer][k]
			break

	emit('delete', id, room=request.referrer, broadcast=True)

	return '', 204


def close_running_threads():
	cache.set(f'messages', messages)
	cache.set(f'muted', muted)
atexit.register(close_running_threads)
