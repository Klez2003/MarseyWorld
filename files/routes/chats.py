import isodate
import yt_dlp

from files.classes.chats import *
from files.classes.orgy import *
from files.routes.wrappers import *
from files.helpers.config.const import *
from files.helpers.get import *

from files.__main__ import app, limiter

@app.get("/chat")
@app.get("/orgy")
def chat_redirect():
	return redirect("/chat/1")

@app.post("/@<username>/chat")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("10/minute;20/hour;50/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("10/minute;20/hour;50/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def chat_user(v, username):
	user = get_user(username, v=v, include_blocks=True)

	if hasattr(user, 'is_blocking') and user.is_blocking:
		abort(403, f"You're blocking @{user.username}")

	if v.admin_level <= PERMS['MESSAGE_BLOCKED_USERS'] and hasattr(user, 'is_blocked') and user.is_blocked:
		abort(403, f"@{user.username} is blocking you!")

	if user.has_muted(v):
		abort(403, f"@{user.username} is muting notifications from you, so you can't chat with them!")


	sq = g.db.query(Chat.id).join(ChatMembership, ChatMembership.chat_id == Chat.id).filter(ChatMembership.user_id.in_((v.id, user.id))).group_by(Chat.id).having(func.count(Chat.id) == 2).subquery()
	existing = g.db.query(Chat.id).join(ChatMembership, ChatMembership.chat_id == Chat.id).filter(Chat.id == sq.c.id).group_by(Chat.id).having(func.count(Chat.id) == 2).one_or_none()
	if existing:
		return redirect(f"/chat/{existing.id}")

	chat = Chat(name=f"@{v.username}, @{user.username}")
	g.db.add(chat)
	g.db.flush()

	chat_membership = ChatMembership(
		user_id=v.id,
		chat_id=chat.id,
	)
	g.db.add(chat_membership)

	chat_membership = ChatMembership(
		user_id=user.id,
		chat_id=chat.id,
	)
	chat_membership.created_utc += 1
	g.db.add(chat_membership)

	return redirect(f"/chat/{chat.id}")


@app.get("/chat/<int:chat_id>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def chat(v, chat_id):
	chat = g.db.get(Chat, chat_id)
	if not chat:
		abort(404, "Chat not found!")

	muting_chat = False

	if chat.id == 1:
		if not v.allowed_in_chat:
			abort(403, f"To prevent spam, you'll need {TRUESCORE_MINIMUM} truescore (this is {TRUESCORE_MINIMUM} votes, either up or down, on any threads or comments you've made) in order to access chat. Sorry! I love you 💖")
	else:
		membership = g.db.query(ChatMembership).filter_by(user_id=v.id, chat_id=chat_id).one_or_none()
		if v.admin_level < PERMS['VIEW_CHATS'] and not membership:
			abort(403, "You're not a member of this chat!")
		if membership:
			muting_chat = (membership.notification == None)

	displayed_messages = g.db.query(ChatMessage).options(joinedload(ChatMessage.quoted_message)).filter(ChatMessage.chat_id == chat.id)

	if v.admin_level < PERMS['USER_SHADOWBAN']:
		displayed_messages = displayed_messages.join(ChatMessage.user).filter(or_(User.id == v.id, User.shadowbanned == None))

	displayed_messages = reversed(displayed_messages.order_by(ChatMessage.id.desc()).limit(250).all())
	displayed_messages = {m.id: m for m in displayed_messages}

	if chat.id == 1:
		sorted_memberships = None
	else:
		if not session.get("GLOBAL") and membership:
			membership.mentions = 0
			g.db.add(membership)
			g.db.commit() #to clear notif count

		query = g.db.query(ChatMembership).filter_by(chat_id=chat.id)

		sorted_memberships = query.filter(ChatMembership.user_id != chat.owner_id).join(ChatMembership.user).order_by(func.lower(User.username)).all()
		owner_membership = query.filter_by(user_id=chat.owner_id).one_or_none()
		if owner_membership:
			sorted_memberships = [owner_membership] + sorted_memberships


	orgy = get_running_orgy(v, chat_id)
	if orgy:
		orgies = g.db.query(Orgy).filter_by(chat_id=chat_id).order_by(Orgy.start_utc).all()
		return render_template("orgy.html", v=v, messages=displayed_messages, chat=chat, sorted_memberships=sorted_memberships, muting_chat=muting_chat, orgy=orgy, orgies=orgies)

	return render_template("chat.html", v=v, messages=displayed_messages, chat=chat, sorted_memberships=sorted_memberships, muting_chat=muting_chat)


@app.post("/chat/<int:chat_id>/name")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def change_chat_name(v, chat_id):
	chat = g.db.get(Chat, chat_id)
	if not chat:
		abort(404, "Chat not found!")

	if v.id != chat.owner_id:
		abort(403, "Only the chat owner can change its name!")

	new_name = request.values.get("new_name").strip()

	if len(new_name) > 40:
		abort(400, "New name is too long (max 40 characters)")

	chat.name = new_name
	g.db.add(chat)

	return redirect(f"/chat/{chat.id}")

@app.post("/chat/<int:chat_id>/leave")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leave_chat(v, chat_id):
	chat = g.db.get(Chat, chat_id)
	if not chat:
		abort(404, "Chat not found!")

	membership = g.db.query(ChatMembership).filter_by(user_id=v.id, chat_id=chat_id).one_or_none()
	if not membership:
		abort(400, "You're not a member of this chat!")

	g.db.delete(membership)

	return {"message": "Chat left successfully!"}

@app.post("/chat/<int:chat_id>/toggle_mute")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def mute_chat(v, chat_id):
	chat = g.db.get(Chat, chat_id)
	if not chat:
		abort(404, "Chat not found!")

	membership = g.db.query(ChatMembership).filter_by(user_id=v.id, chat_id=chat_id).one_or_none()
	if not membership:
		abort(400, "You're not a member of this chat!")

	if membership.notification == None:
		membership.notification = False
		msg = "Chat unmuted successfully (yayyy)"
		send_notification(chat.owner_id, f"@{v.username} unmuted your chat [{chat.name}](/chat/{chat.id}).")
	else:
		membership.notification = None
		msg = "Chat muted successfully (die)"
		send_notification(chat.owner_id, f"@{v.username} muted your chat [{chat.name}](/chat/{chat.id}), kick him now!")

	g.db.add(membership)

	return {"message": msg}

@app.get("/chat/<int:chat_id>/orgies")
@auth_required
def orgy_control(v, chat_id):
	chat = g.db.get(Chat, chat_id)
	if not chat:
		abort(404, "Chat not found!")

	if chat.id == 1:
		if v.admin_level < PERMS["ORGIES"]:
			abort(403, "Your admin-level is not sufficient enough for this action!")
	elif v.id != chat.owner_id:
		abort(403, "Only the chat owner can manage its orgies!")

	orgies = g.db.query(Orgy).filter_by(chat_id=chat_id).order_by(Orgy.start_utc).all()
	return render_template("orgy_control.html", v=v, orgies=orgies, chat=chat)

@app.post("/chat/<int:chat_id>/schedule_orgy")
@auth_required
def schedule_orgy(v, chat_id):
	chat = g.db.get(Chat, chat_id)
	if not chat:
		abort(404, "Chat not found!")

	if chat.id == 1:
		if v.admin_level < PERMS["ORGIES"]:
			abort(403, "Your admin-level is not sufficient enough for this action!")
	elif v.id != chat.owner_id:
		abort(403, "Only the chat owner can manage its orgies!")

	link = request.values.get("link", "").strip()
	title = request.values.get("title", "").strip()
	start_utc = request.values.get("start_utc", "").strip()

	if not link:
		abort(400, "A link is required!")

	if not title:
		abort(400, "A title is required!")

	if len(title) > 40:
		abort(400, 'Title is too long (max 40 characters)')

	normalized_link = normalize_url(link)

	if start_utc:
		start_utc = int(start_utc)
	else:
		last_orgy = g.db.query(Orgy).filter_by(chat_id=chat.id).order_by(Orgy.start_utc.desc()).first()
		if last_orgy and last_orgy.end_utc:
			start_utc = last_orgy.end_utc
		else:
			start_utc = int(time.time())

	end_utc = None

	if bare_youtube_regex.match(normalized_link):
		orgy_type = 'youtube'
		id, _ = get_youtube_id_and_t(normalized_link)
		data = f'https://cdpn.io/pen/debug/NWeVNRj?v={id}&autoplay=1'
		if YOUTUBE_KEY != DEFAULT_CONFIG_VALUE:
			req = requests.get(f"https://www.googleapis.com/youtube/v3/videos?id={id}&key={YOUTUBE_KEY}&part=contentDetails", headers=HEADERS, timeout=5).json()
			duration = req['items'][0]['contentDetails']['duration']
			if duration != 'P0D':
				duration = isodate.parse_duration(duration).total_seconds()
				end_utc = int(start_utc + duration)
				orgy_type = 'file'

				ydl_opts = {
					"quiet": True,
					"simulate": True,
					"forceurl": True,
					'format': 'b',
					'proxy': PROXY_URL
				}

				with yt_dlp.YoutubeDL(ydl_opts) as ydl:
					info = ydl.extract_info(f"https://www.youtube.com/watch?v={id}")
				data = info["url"]
	elif rumble_regex.match(normalized_link):
		orgy_type = 'rumble'
		data = normalized_link
	elif twitch_regex.match(normalized_link):
		orgy_type = 'twitch'
		data = twitch_regex.search(normalized_link).group(3)
		data = f'https://player.twitch.tv/?channel={data}&parent={SITE}'
	elif any((normalized_link.lower().endswith(f'.{x}') for x in VIDEO_FORMATS)):
		domain = tldextract.extract(normalized_link).registered_domain
		if domain != 'archive.org' and not is_safe_url(normalized_link):
			abort(400, "For linking an mp4 file, you can only use archive.org or one of the approved media hosts outlined in https://rdrama.net/formatting#approved")
		orgy_type = 'file'
		data = normalized_link
		video_info = ffmpeg.probe(data)
		duration = float(video_info['streams'][0]['duration'])
		if duration == 2.0: raise
		if duration > 3000:
			duration += 300 #account for break
		end_utc = int(start_utc + duration)
	else:
		abort(400)

	data = data.strip()

	orgy = Orgy(
			title=title,
			type=orgy_type,
			data=data,
			start_utc=start_utc,
			end_utc=end_utc,
			chat_id=chat_id,
		)
	g.db.add(orgy)

	if chat.id == 1:
		ma = ModAction(
			kind="schedule_orgy",
			user_id=v.id,
			_note=f'<a href="{orgy.data}" rel="nofollow noopener">{title}</a>',
		)
		g.db.add(ma)

	return redirect(f"/chat/{chat_id}/orgies")

@app.post("/chat/<int:chat_id>/remove_orgy/<int:created_utc>")
@auth_required
def remove_orgy(v, created_utc, chat_id):
	chat = g.db.get(Chat, chat_id)
	if not chat:
		abort(404, "Chat not found!")

	if chat.id == 1:
		if v.admin_level < PERMS["ORGIES"]:
			abort(403, "Your admin-level is not sufficient enough for this action!")
	elif v.id != chat.owner_id:
		abort(403, "Only the chat owner can manage its orgies!")

	orgy = g.db.query(Orgy).filter_by(created_utc=created_utc).one_or_none()

	if orgy:
		if chat.id == 1:
			ma = ModAction(
				kind="remove_orgy",
				user_id=v.id,
				_note=f'<a href="{orgy.data}" rel="nofollow noopener">{orgy.title}</a>',
			)
			g.db.add(ma)

		started = orgy.started
		g.db.delete(orgy)
		g.db.commit()
		if started:
			requests.post(f'http://localhost:5001/chat/{chat_id}/refresh_chat', headers={"User-Agent": "refreshing_chat", "Host": SITE})

	return {"message": "Orgy stopped successfully!"}
