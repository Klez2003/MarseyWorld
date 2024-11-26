import time

from sqlalchemy.sql.expression import not_, and_, or_
from sqlalchemy.orm import load_only

from files.classes.mod_logs import ModAction
from files.classes.hole_logs import HoleAction
from files.classes.chats import *
from files.helpers.config.const import *
from files.helpers.config.modaction_kinds import *
from files.helpers.get import *
from files.helpers.can_see import *
from files.routes.wrappers import *
from files.routes.comments import _mark_comment_as_read
from files.__main__ import app

@app.post("/clear")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def clear(v):
	notifs = g.db.query(Notification).join(Notification.comment).filter(
		Notification.read == False,
		Notification.user_id == v.id,
	).options(load_only(Notification.comment_id)).all()
	for n in notifs:
		n.read = True
		g.db.add(n)

	chat_memberships = g.db.query(ChatMembership).filter_by(user_id=v.id, notification=True)
	for membership in chat_memberships:
		membership.notification = False
		membership.mentions = 0
		g.db.add(membership)

	v.last_viewed_modmail_notifs = int(time.time())
	v.last_viewed_post_notifs = int(time.time())
	v.last_viewed_log_notifs = int(time.time())
	v.last_viewed_offsite_notifs = int(time.time())
	g.db.add(v)
	return {"message": "Notifications marked as read!"}


@app.get("/unread")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def unread(v):
	listing = g.db.query(Notification, Comment).join(Notification.comment).filter(
		Notification.read == False,
		Notification.user_id == v.id,
		Comment.is_banned == False,
		Comment.deleted_utc == 0,
	).order_by(Notification.created_utc.desc()).all()

	for n, c in listing:
		n.read = True
		g.db.add(n)

	return {"data":[x[1].json for x in listing]}


@app.get("/notifications/messages")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def notifications_messages(v):
	page = get_page()

	# All of these queries are horrible. For whomever comes here after me,
	# PLEASE just turn DMs into their own table and get them out of
	# Notifications & Comments. It's worth it. Save yourself.
	message_threads = g.db.query(Comment).filter(
		Comment.sentto != None,
		or_(Comment.author_id == v.id, Comment.sentto == v.id),
		Comment.parent_post == None,
		Comment.level == 1,
	)


	thread_order = g.db.query(Comment.top_comment_id, Comment.created_utc) \
		.distinct(Comment.top_comment_id) \
		.filter(
			Comment.sentto != None,
			or_(Comment.author_id == v.id, Comment.sentto == v.id),
		).order_by(
			Comment.top_comment_id.desc(),
			Comment.created_utc.desc()
		).subquery()

	message_threads = message_threads.join(thread_order,
						thread_order.c.top_comment_id == Comment.top_comment_id)

	# Clear notifications (used for unread indicator only) for all user messages.

	if not session.get("GLOBAL"):
		notifs_unread_row = g.db.query(Notification.comment_id).join(Comment).filter(
			Notification.user_id == v.id,
			Notification.read == False,
			or_(Comment.author_id == v.id, Comment.sentto == v.id),
		).all()

		notifs_unread = [n.comment_id for n in notifs_unread_row]
		notif_list = g.db.query(Notification).filter(
				Notification.user_id == v.id,
				Notification.comment_id.in_(notifs_unread),
			)

		for n in notif_list:
			n.read = True
			g.db.add(n)

		g.db.flush()

		list_to_perserve_unread_attribute = []
		comments_unread = g.db.query(Comment).filter(Comment.id.in_(notifs_unread))
		for c in comments_unread:
			c.unread = True
			list_to_perserve_unread_attribute.append(c)


	total = message_threads.count()
	listing = message_threads.order_by(thread_order.c.created_utc.desc()) \
					.offset(PAGE_SIZE*(page-1)).limit(PAGE_SIZE).all()

	if v.client: return {"data":[x.json for x in listing]}

	return render_template("notifications.html",
							v=v,
							notifications=listing,
							total=total,
							page=page,
							standalone=True,
							render_replies=True,
						)


@app.get("/notifications/chats")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def notifications_chats(v):
	sq = g.db.query(ChatMessage.created_utc, ChatMessage.chat_id).distinct(ChatMessage.chat_id).order_by(ChatMessage.chat_id, ChatMessage.created_utc.desc()).subquery()

	chats = g.db.query(Chat, ChatMembership.notification, ChatMembership.muted, ChatMembership.mentions) \
	.join(ChatMembership, and_(Chat.id == ChatMembership.chat_id, ChatMembership.user_id == v.id)) \
	.join(sq, Chat.id == sq.c.chat_id) \
	.order_by(ChatMembership.mentions.desc(), ChatMembership.notification.desc(), sq.c.created_utc.desc()).all()

	return render_template("notifications.html", v=v, notifications=chats)

def modmail_listing(v):
	page = get_page()

	sq = g.db.query(Comment.top_comment_id, Comment.created_utc).distinct(Comment.top_comment_id).filter_by(sentto=MODMAIL_ID).order_by(Comment.top_comment_id, Comment.created_utc.desc()).subquery()

	comments = g.db.query(Comment).filter(Comment.id == sq.c.top_comment_id).order_by(sq.c.created_utc.desc())

	if request.path == '/contact':
		comments = comments.filter_by(author_id=v.id)

	total = comments.count()
	listing = comments.order_by(Comment.id.desc()).offset(PAGE_SIZE*(page-1)).limit(PAGE_SIZE).all()

	for c in listing:
		c_and_children = [c] + c.replies('old')
		for c in c_and_children:
			if c.author_id == v.id: continue
			c.unread = c.created_utc > v.last_viewed_modmail_notifs

	if not session.get("GLOBAL"):
		v.last_viewed_modmail_notifs = int(time.time())
		g.db.add(v)

	return listing, total, page

@app.get("/notifications/modmail")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['VIEW_MODMAIL'])
def notifications_modmail(v):
	listing, total, page = modmail_listing(v)

	if v.client: return {"data":[x.json for x in listing]}

	return render_template("notifications.html",
							v=v,
							notifications=listing,
							total=total,
							page=page,
							standalone=True,
							render_replies=True,
						)


@app.get("/notifications/posts")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def notifications_posts(v):
	page = get_page()

	or_criteria = [
		Post.hole.in_(v.followed_holes),
		and_(
			Post.author_id.in_(v.followed_users),
			Post.notify == True,
			Post.ghost == False,
		)]

	if v.effortpost_notifs:
		or_criteria.append(Post.effortpost == True)

	listing = g.db.query(Post).filter(
		Post.deleted_utc == 0,
		Post.is_banned == False,
		Post.draft == False,
		Post.author_id != v.id,
		Post.author_id.notin_(v.userblocks),
		or_(Post.hole == None, Post.hole.notin_(v.hole_blocks)),
		or_(*or_criteria),
	).options(load_only(Post.id))

	if v.admin_level < PERMS['USER_SHADOWBAN']:
		listing = listing.join(Post.author).filter(User.shadowbanned == None)

	total = listing.count()

	listing = listing.order_by(Post.created_utc.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()
	listing = [x.id for x in listing]

	listing = get_posts(listing, v=v)

	for p in listing:
		p.unread = p.created_utc > v.last_viewed_post_notifs

	if not session.get("GLOBAL"):
		v.last_viewed_post_notifs = int(time.time())
		g.db.add(v)

	if v.client: return {"data":[x.json for x in listing]}

	return render_template("notifications.html",
							v=v,
							notifications=listing,
							total=total,
							page=page,
							standalone=True,
							render_replies=True,
						)


@app.get("/notifications/modactions")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def notifications_modactions(v):
	page = get_page()

	if v.admin_level >= PERMS['NOTIFICATIONS_MODERATOR_ACTIONS']:
		cls = ModAction
	elif v.moderated_holes:
		cls = HoleAction
	else:
		stop(403)

	listing = g.db.query(cls).filter(cls.user_id != v.id)

	if v.id == AEVANN_ID:
		listing = listing.filter(cls.kind.notin_(AEVANN_EXCLUDED_MODACTION_KINDS))

	if v.admin_level < PERMS['PROGSTACK']:
		listing = listing.filter(cls.kind.notin_(MODACTION_PRIVILEGED__KINDS))

	if cls == HoleAction:
		listing = listing.filter(cls.hole.in_(v.moderated_holes))

	total = listing.count()
	listing = listing.order_by(cls.id.desc())
	listing = listing.offset(100*(page-1)).limit(100).all()

	for ma in listing:
		ma.unread = ma.created_utc > v.last_viewed_log_notifs

	if not session.get("GLOBAL"):
		v.last_viewed_log_notifs = int(time.time())
		g.db.add(v)

	return render_template("notifications.html",
							v=v,
							notifications=listing,
							total=total,
							page=page,
							standalone=True,
							render_replies=True,
						)



@app.get("/notifications/offsite")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def notifications_offsite(v):
	page = get_page()

	if v.offsite_mentions == None:
		stop(403)

	listing = g.db.query(Comment).filter(
		Comment.body_html.like('<p>New site mention%'),
		Comment.parent_post == None,
		Comment.author_id == AUTOJANNY_ID
	)

	total = listing.count()
	listing = listing.order_by(Comment.created_utc.desc(), Comment.id.desc()).offset(PAGE_SIZE*(page-1)).limit(PAGE_SIZE).all()

	for ma in listing:
		ma.unread = ma.created_utc > v.last_viewed_offsite_notifs

	if not session.get("GLOBAL"):
		v.last_viewed_offsite_notifs = int(time.time())
		g.db.add(v)

	if v.client: return {"data":[x.json for x in listing]}

	return render_template("notifications.html",
							v=v,
							notifications=listing,
							total=total,
							page=page,
							standalone=True,
							render_replies=True,
						)




@app.get("/notifications")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def notifications(v):
	page = get_page()

	if not session.get("GLOBAL") and v.admin_level < PERMS['USER_SHADOWBAN']:
		unread_and_inaccessible = g.db.query(Notification).join(Notification.comment).join(Comment.author).filter(
			Notification.user_id == v.id,
			Notification.read == False,
			or_(
				User.shadowbanned != None,
				Comment.is_banned != False,
				Comment.deleted_utc != 0,
			)
		).options(load_only(Notification.comment_id)).all()
		for n in unread_and_inaccessible:
			n.read = True
			g.db.add(n)

	comments = g.db.query(Comment, Notification).options(load_only(Comment.id)).join(Notification.comment).filter(
		Notification.user_id == v.id,
		or_(Comment.sentto == None, Comment.sentto != v.id),
	)

	if v.admin_level < PERMS['USER_SHADOWBAN']:
		comments = comments.filter(
			Comment.is_banned == False,
			Comment.deleted_utc == 0,
		)

	total = comments.count()

	comments = comments.order_by(Notification.created_utc.desc(), Comment.id.desc())
	comments = comments.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()

	cids = [x[0].id for x in comments]

	listing = []
	all_items = [x[0] for x in comments]

	for c, n in comments:
		c.notified_utc = n.created_utc
		c.collapse = n.read

	for c, n in comments:
		if n.created_utc > 1620391248: c.notif_utc = n.created_utc

		if not n.read: c.unread = True
		c.is_notif = True

		if c.parent_post or c.wall_user_id:
			all_items.append(c)

			if c.replies2 == None:
				c.replies2 = g.db.query(Comment).filter_by(parent_comment_id=c.id).filter(or_(Comment.author_id == v.id, Comment.id.in_(cids))).order_by(Comment.id.desc()).all()
				all_items.extend(c.replies2)
				for x in c.replies2:
					if x.replies2 == None: x.replies2 = []

			count = 0
			while count < 30 and c.parent_comment and (c.parent_comment.author_id == v.id or c.parent_comment.id in cids):
				count += 1
				c = c.parent_comment

				if c.replies2 == None:
					c.replies2 = g.db.query(Comment).filter_by(parent_comment_id=c.id).filter(or_(Comment.author_id == v.id, Comment.id.in_(cids))).order_by(Comment.id.desc()).all()
					all_items.extend(c.replies2)
					for x in c.replies2:
						if x.replies2 == None:
							x.replies2 = g.db.query(Comment).filter_by(parent_comment_id=x.id).filter(or_(Comment.author_id == v.id, Comment.id.in_(cids))).order_by(Comment.id.desc()).all()
							all_items.extend(x.replies2)

				if not hasattr(c, "notified_utc") or n.created_utc > c.notified_utc:
					c.notified_utc = n.created_utc
					c.collapse = n.read

				c.replies2 = sorted(c.replies2, key=lambda x: x.notified_utc if hasattr(x, "notified_utc") else x.id, reverse=True)
		else:
			while c.parent_comment_id:
				c = c.parent_comment
			c.replies2 = g.db.query(Comment).filter_by(parent_comment_id=c.id).order_by(Comment.id).all()

		if c not in listing: listing.append(c)

		if not n.read and not session.get("GLOBAL"):
			n.read = True
			g.db.add(n)

	all_items.extend(listing)

	listing2 = {}

	for x in listing:
		if x.parent_comment_id:
			parent = x.parent_comment
			if parent.replies2 == None:
				parent.replies2 = g.db.query(Comment).filter_by(parent_comment_id=parent.id).filter(or_(Comment.author_id == v.id, Comment.id.in_(cids+[x.id]))).order_by(Comment.id.desc()).all()
				all_items.extend(parent.replies2)
				for y in parent.replies2:
					if y.replies2 == None:
						y.replies2 = []
			listing2[parent] = ''
		else:
			listing2[x] = ''

	listing = listing2.keys()

	all_items.extend(listing)

	all_cids = [x.id for x in all_items]
	all_cids.extend(cids)
	all_cids = set(all_cids)
	output = get_comments_v_properties(v, None, Comment.id.in_(all_cids))[1]

	g.db.flush()

	if v.client: return {"data":[x.json for x in listing]}

	return render_template("notifications.html",
							v=v,
							notifications=listing,
							total=total,
							page=page,
							standalone=True,
							render_replies=True,
						)


@app.get("/notification//<int:cid>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def notification(v, cid):
	comment = get_comment(cid, v=v)

	if not can_see(v, comment): stop(403)

	comment.unread = True

	gevent.spawn(_mark_comment_as_read, comment.id, v.id)

	if comment.level > 1:
		shown_comment = comment.top_comment
	else:
		shown_comment = comment

	return render_template("notifications.html",
							v=v,
							notifications=[shown_comment],
							total=1,
							page=1,
							standalone=True,
							render_replies=True,
							focused_comment=comment,
						)
