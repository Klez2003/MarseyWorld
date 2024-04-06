
from files.classes.chats import *
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

	chat = Chat(owner_id=v.id, name=f"@{v.username}, @{user.username}")
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

	if chat.id == 1:
		if not v.allowed_in_chat:
			abort(403, f"To prevent spam, you'll need {TRUESCORE_MINIMUM} truescore (this is {TRUESCORE_MINIMUM} votes, either up or down, on any threads or comments you've made) in order to access chat. Sorry! I love you 💖")
	else:
		membership = g.db.query(ChatMembership).filter_by(user_id=v.id, chat_id=chat_id).one_or_none()
		if v.admin_level < PERMS['VIEW_CHATS'] and not membership:
			abort(403, "You're not a member of this chat!")

	displayed_messages = reversed(g.db.query(ChatMessage).filter_by(chat_id=chat.id).order_by(ChatMessage.id.desc()).limit(250).all())
	displayed_messages = {m.id: m for m in displayed_messages}

	if chat.id == 1:
		sorted_memberships = None
	else:
		if not session.get("GLOBAL") and membership:
			membership.notification = False
			g.db.add(membership)
			g.db.commit() #to clear notif count
		query = g.db.query(ChatMembership).filter_by(chat_id=chat.id)
		sorted_memberships = [query.filter_by(user_id=chat.owner_id).one()] + query.filter(ChatMembership.user_id != chat.owner_id).join(ChatMembership.user).order_by(func.lower(User.username)).all()

	return render_template("chat.html", v=v, messages=displayed_messages, chat=chat, sorted_memberships=sorted_memberships)


@app.post("/chat/<int:chat_id>/name")
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
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leave_chat(v, chat_id):
	chat = g.db.get(Chat, chat_id)
	if not chat:
		abort(404, "Chat not found!")

	if v.id == chat.owner_id:
		abort(403, "The chat owner can't leave it!")

	membership = g.db.query(ChatMembership).filter_by(user_id=v.id, chat_id=chat_id).one_or_none()
	if not membership:
		abort(400, "You're not a member of this chat!")

	g.db.delete(membership)

	chat_leave = ChatLeave(
		user_id=v.id,
		chat_id=chat_id,
	)
	g.db.add(chat_leave)

	return {"message": "Chat left successfully!"}
