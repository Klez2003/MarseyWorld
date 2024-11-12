import os
from collections import Counter
from shutil import copyfile
import random

import gevent

from files.classes import *
from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.media import *
from files.helpers.regex import *
from files.helpers.slots import *
from files.helpers.treasure import *
from files.helpers.can_see import *
from files.routes.front import comment_idlist
from files.routes.routehelpers import execute_shadowban_viewers_and_voters
from files.routes.wrappers import *
from files.__main__ import app, cache, limiter

def _mark_comment_as_read(cid, vid):
	db = db_session()

	notif = db.query(Notification).options(load_only(Notification.read)).filter_by(comment_id=cid, user_id=vid, read=False).one_or_none()

	if notif and not notif.read:
		notif.read = True
		db.add(notif)

	db.commit()
	db.close()
	stdout.flush()

@app.get("/comment/<int:cid>")
@app.get("/post/<int:pid>/<anything>/<int:cid>")
@app.get("/h/<hole>/comment/<int:cid>")
@app.get("/h/<hole>/post/<int:pid>/<anything>/<int:cid>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_desired_with_logingate
def post_pid_comment_cid(cid, v, pid=None, anything=None, hole=None):

	comment = get_comment(cid, v=v)

	if not can_see(v, comment): stop(403)

	if comment.parent_post:
		post = comment.parent_post
	elif comment.wall_user_id:
		return redirect(f"/id/{comment.wall_user_id}/wall/comment/{comment.id}")
	else:
		return redirect(f"/notification/{comment.id}")

	if v and request.values.get("read"):
		gevent.spawn(_mark_comment_as_read, comment.id, v.id)

	post = get_post(post, v=v)

	if not (v and v.client) and post.nsfw and not g.show_nsfw:
		return render_template("errors/nsfw.html", v=v), 403

	try: context = min(int(request.values.get("context", 8)), 8)
	except: context = 8
	focused_comment = comment
	c = comment

	if post.new: defaultsortingcomments = 'new'
	elif v: defaultsortingcomments = v.defaultsortingcomments
	else: defaultsortingcomments = "hot"
	sort = request.values.get("sort", defaultsortingcomments)

	while context and c.level > 1:
		parent = c.parent_comment
		replies = parent.replies(sort)
		replies.remove(c)
		parent.replies2 = [c] + replies
		c = parent
		context -= 1
	top_comment = c

	if v:
		# this is required because otherwise the vote and block
		# props won't save properly unless you put them in a list
		output = get_comments_v_properties(v, None, Comment.top_comment_id == c.top_comment_id)[1]
	post.replies=[top_comment]

	execute_shadowban_viewers_and_voters(v, post)
	execute_shadowban_viewers_and_voters(v, comment)

	if v and v.client: return comment.json
	else:
		if post.is_banned and not (v and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or post.author_id == v.id)):
			template = "post_banned.html"
		else:
			template = "post.html"
		return render_template(template, v=v, p=post, sort=sort, focused_comment=focused_comment, render_replies=True, hole=post.hole_obj)

@app.post("/comment")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("20/minute;400/hour;1000/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("20/minute;400/hour;1000/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def comment(v):
	parent_fullname = request.values.get("parent_fullname").strip()
	if len(parent_fullname) < 3: stop(400)
	id = parent_fullname[2:]
	parent_comment_id = None
	rts = False

	post_target = None
	parent = None

	notify_op = True

	if parent_fullname.startswith("u_"):
		parent = get_account(id, v=v)
		post_target = parent
		ghost = False
	elif parent_fullname.startswith("p_"):
		parent = get_post(id, v=v)
		post_target = parent
		if parent.id in ADMIGGER_THREADS and v.admin_level < PERMS['USE_ADMIGGER_THREADS']:
			stop(403, "You can't post top-level comments in this thread!")

		ghost = parent.ghost
	elif parent_fullname.startswith("c_"):
		parent = get_comment(id, v=v)
		post_target = get_post(parent.parent_post, v=v, graceful=True) or get_account(parent.wall_user_id, v=v, include_blocks=True)
		parent_comment_id = parent.id
		if parent.author_id == v.id: rts = True
		if not v.can_post_in_ghost_threads and isinstance(post_target, Post) and post_target.ghost:
			stop(403, f"You need {TRUESCORE_MINIMUM} truescore to post in ghost threads")
		ghost = parent.ghost
	else: stop(404)

	level = 1 if isinstance(parent, (Post, User)) else int(parent.level) + 1
	parent_user = parent if isinstance(parent, User) else parent.author
	posting_to_post = isinstance(post_target, Post)

	if posting_to_post and not can_see(v, parent):
		stop(403)

	if posting_to_post:
		commenters_ping_post_id = post_target.id
	else:
		commenters_ping_post_id = None

	if not isinstance(parent, User) and parent.deleted_utc != 0 and v.admin_level < PERMS['POST_COMMENT_MODERATION']:
		if isinstance(parent, Post):
			stop(403, "You can't reply to deleted posts!")
		else:
			stop(403, "You can't reply to deleted comments!")

	if posting_to_post:
		hole = post_target.hole
		if hole and v.exiler_username(hole): stop(403, f"You're exiled from /h/{hole}")
		if hole in {'furry','vampire','racist','femboy','edgy'} and not v.client and not v.house.lower().startswith(hole):
			stop(403, f"You need to be a member of House {hole.capitalize()} to comment in /h/{hole}")

	distinguished = request.values.get('distinguished') == 'true' and v.admin_level >= PERMS['POST_COMMENT_DISTINGUISH']

	if v.is_suspended and not (posting_to_post and hole == 'chudrama') and not distinguished:
		if SITE_NAME == 'rDrama':
			stop(403, "You can only comment in /h/chudrama when you're tempbanned!")
		stop(403, "You can't perform this action while banned!")

	if level > COMMENT_MAX_DEPTH:
		stop(400, f"Max comment level is {COMMENT_MAX_DEPTH}")

	body = request.values.get("body", "").strip()
	if len(body) > COMMENT_BODY_LENGTH_LIMIT:
		stop(400, f'Comment body is too long (max {COMMENT_BODY_LENGTH_LIMIT} characters)')

	body = body.replace('@jannies', '!jannies')

	if not distinguished and not (posting_to_post and post_target.id in ADMIGGER_THREADS):
		if v.longpost and (len(body) < 280 or ' [](' in body or body.startswith('[](')):
			stop(403, "You have to type more than 280 characters!")
		elif v.bird and len(body) > 140:
			stop(403, "You have to type less than 140 characters!")

	if not body and not request.files.get('file'):
		stop(400, "You need to actually write something!")

	if parent_user.has_blocked(v) or parent_user.has_muted(v):
		notify_op = False

	if posting_to_post and v.admin_level >= PERMS['USE_ADMIGGER_THREADS'] and post_target.id == BADGE_THREAD:
		is_badge_thread = True
		comment_body = body
	else:
		is_badge_thread = False
		comment_body = None

	body = process_files(request.files, v, body, is_badge_thread=is_badge_thread, comment_body=comment_body)
	if len(body) > COMMENT_BODY_LENGTH_LIMIT:
		stop(400, f'Comment body is too long (max {COMMENT_BODY_LENGTH_LIMIT} characters)')

	if v.admin_level >= PERMS['USE_ADMIGGER_THREADS'] and posting_to_post and post_target.id == SNAPPY_THREAD and level == 1:
		body = remove_cuniform(body)
		while '\n\n' in body:
			body = body.replace('\n\n', '\n')
		with open(f"snappy_{SITE_NAME}.txt", "r+") as f:
			body_for_checking = '\n[para]\n' + body.lower() + '\n[para]\n'
			if body_for_checking in f.read().lower() + '[para]\n':
				stop(400, "Snappy quote already exists!")
			f.write('[para]\n' + body + '\n')
			SNAPPY_QUOTES.append(body)

	is_bot = v.client is not None and v.id not in BOT_SYMBOL_HIDDEN

	chudded = v.chud and not (posting_to_post and post_target.hole == 'chudrama')

	c = Comment(author_id=v.id,
				parent_post=post_target.id if posting_to_post else None,
				wall_user_id=post_target.id if not posting_to_post else None,
				parent_comment_id=parent_comment_id,
				level=level,
				nsfw=post_target.nsfw if posting_to_post else False,
				is_bot=is_bot,
				app_id=v.client.application.id if v.client else None,
				body=body,
				ghost=ghost,
				chudded=chudded,
				rainbowed=bool(v.rainbow),
				queened=bool(v.queen),
				sharpened=bool(v.sharpen),
				distinguished=distinguished,
			)

	c.upvotes = 1

	g.db.add(c)
	body_html = sanitize(body, limit_pings=5, showmore=(not v.hieroglyphs), count_emojis=not v.marsify, commenters_ping_post_id=commenters_ping_post_id, obj=c, author=v)

	if post_target.id not in ADMIGGER_THREADS and not (v.chud and v.chud_phrase.lower() in body.lower()):
		existing = g.db.query(Comment.id).filter(
			Comment.author_id == v.id,
			Comment.deleted_utc == 0,
			Comment.parent_comment_id == parent_comment_id,
			Comment.parent_post == post_target.id if posting_to_post else None,
			Comment.wall_user_id == post_target.id if not posting_to_post else None,
			Comment.body_html == body_html
		).first()
		if existing: stop(409, f"You already made that comment: /comment/{existing.id}#context")

	execute_antispam_comment_check(body, v)
	execute_antispam_duplicate_comment_check(v, body_html)

	if v.hieroglyphs and not c.distinguished and marseyaward_body_regex.search(body_html) and not (posting_to_post and post_target.id in ADMIGGER_THREADS):
		stop(403, "You can only type emojis!")

	if len(body_html) > COMMENT_BODY_HTML_LENGTH_LIMIT:
		stop(400, "Rendered comment is too long!")

	c.body_html = body_html

	g.db.flush()

	if not posting_to_post and v.admin_level >= PERMS['ADMIN_NOTES'] and request.values.get('admin_note') == 'true' :
		c.pinned = "Admin Note"

	if c.parent_comment_id and c.parent_comment.pinned == "Admin Note":
		c.pinned = "Admin Note"

	process_options(v, c)

	execute_blackjack(v, c, c.body, "comment")

	kind = "normal comment" if posting_to_post else "wall comment"
	execute_under_siege(v, c, kind)

	if c.level == 1: c.top_comment_id = c.id
	else: c.top_comment_id = parent.top_comment_id

	if not complies_with_chud(c):
		c.is_banned = True

		for media_usage in c.media_usages:
			media_usage.removed_utc = time.time()
			g.db.add(media_usage)

		c.ban_reason = "AutoJanny for lack of chud phrase"
		g.db.add(c)

		body = random.choice(CHUD_MSGS).format(username=v.username, type='comment', CHUD_PHRASE=v.chud_phrase)
		body_jannied_html = sanitize(body)

		c_jannied = Comment(author_id=AUTOJANNY_ID,
			parent_post=post_target.id if posting_to_post else None,
			wall_user_id=post_target.id if not posting_to_post else None,
			distinguished=True,
			parent_comment_id=c.id,
			level=level+1,
			is_bot=True,
			body=body,
			body_html=body_jannied_html,
			top_comment_id=c.top_comment_id,
			ghost=c.ghost
			)

		g.db.add(c_jannied)
		g.db.flush()

		if posting_to_post:
			post_target.comment_count += 1
			g.db.add(post_target)

		n = Notification(comment_id=c_jannied.id, user_id=v.id)
		g.db.add(n)

		autojanny = g.db.get(User, AUTOJANNY_ID)
		autojanny.comment_count += 1
		g.db.add(autojanny)

	execute_longpostbot(c, level, body, body_html, post_target, v)
	execute_zozbot(c, level, post_target, v)

	notify_users = NOTIFY_USERS(body, v, ghost=c.ghost, obj=c, commenters_ping_post_id=commenters_ping_post_id)

	if notify_users == 'everyone':
		alert_everyone(c.id)
	else:
		push_notif(notify_users, f'New mention of you by @{c.author_name}', c.body, c)

		if c.level == 1 and posting_to_post:
			subscriber_ids = [x[0] for x in g.db.query(Subscription.user_id).filter(Subscription.post_id == post_target.id, Subscription.user_id != v.id)]

			notify_users.update(subscriber_ids)

			push_notif(subscriber_ids, f'New comment in subscribed thread by @{c.author_name}', c.body, c)

		if parent_user.id != v.id and notify_op and parent_user.id not in notify_users:
			notify_users.add(parent_user.id)
			if isinstance(parent, User):
				title = f"New comment on your wall by @{c.author_name}"
			else:
				title = f'New reply by @{c.author_name}'
			push_notif({parent_user.id}, title, c.body, c)

		notify_users -= BOT_IDs

		if v.shadowbanned or c.is_banned:
			notify_users = [x[0] for x in g.db.query(User.id).filter(User.id.in_(notify_users), User.admin_level >= PERMS['USER_SHADOWBAN']).all()]

		if c.pinned == "Admin Note":
			notify_users = [x[0] for x in g.db.query(User.id).filter(User.id.in_(notify_users), User.admin_level >= PERMS['ADMIN_NOTES']).all()]

		for x in notify_users:
			n = Notification(comment_id=c.id, user_id=x)
			g.db.add(n)

		if c.level >= 3 and c.parent_comment.author_id in notify_users:
			n = g.db.query(Notification).filter_by(
				comment_id=c.parent_comment.parent_comment_id,
				user_id=c.parent_comment.author_id,
				read=True,
			).one_or_none()
			if n: g.db.delete(n)

	vote = CommentVote(user_id=v.id,
						 comment_id=c.id,
						 vote_type=1,
						 coins=0
						 )
	g.db.add(vote)

	if c.distinguished:
		ma = ModAction(
			kind='distinguish_comment',
			user_id=v.id,
			target_comment_id=c.id
		)
		g.db.add(ma)

	cache.delete_memoized(comment_idlist)

	if not (c.parent_post in ADMIGGER_THREADS and c.level == 1):
		v.comment_count += 1
		g.db.add(v)

	c.voted = 1

	check_for_treasure(c, body)
	check_slots_command(c, v, v)

	# Increment post count if not self-reply and not a spammy comment game
	# Essentially a measure to make comment counts reflect "real" content
	if (posting_to_post and not rts and not c.slots_result):
		post_target.comment_count += 1
		post_target.bump_utc = c.created_utc
		g.db.add(post_target)

	g.db.commit()
	gevent.spawn(postprocess_comment, c.body, c.body_html, c.id)

	if c.parent_post:
		for sort in COMMENT_SORTS.keys():
			cache.delete(f'post_{c.parent_post}_{sort}')

	if v.client: return c.json
	return {"id": c.id, "comment": render_template("comments.html", v=v, comments=[c])}

@app.post("/delete/comment/<int:cid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DELETE_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DELETE_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def delete_comment(cid, v):
	c = get_comment(cid, v=v)
	if not c.deleted_utc:
		if c.author_id != v.id: stop(403)

		c.deleted_utc = int(time.time())
		g.db.add(c)

		c.author.truescore -= c.upvotes + c.downvotes - 1
		g.db.add(c.author)

		if c.pinned:
			c.pinned = None
			c.pinned_utc = None
			c.unpin_parents()

		if not (c.parent_post in ADMIGGER_THREADS and c.level == 1):
			v.comment_count -= 1
			g.db.add(v)

		for media_usage in c.media_usages:
			media_usage.deleted_utc = c.deleted_utc
			g.db.add(media_usage)

		cache.delete_memoized(comment_idlist)

		if c.parent_post:
			for sort in COMMENT_SORTS.keys():
				cache.delete(f'post_{c.parent_post}_{sort}')

		if v.admin_level >= PERMS['USE_ADMIGGER_THREADS'] and c.parent_post == SNAPPY_THREAD and c.level == 1 and c.body in SNAPPY_QUOTES:
			SNAPPY_QUOTES.remove(c.body)
			new_text = "\n[para]\n".join(SNAPPY_QUOTES)
			with open(f"snappy_{SITE_NAME}.txt", "w") as f:
				f.write(new_text + "\n")

	return {"message": "Comment deleted!"}

@app.post("/undelete/comment/<int:cid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def undelete_comment(cid, v):
	c = get_comment(cid, v=v)
	if c.deleted_utc:
		if c.author_id != v.id: stop(403)
		c.deleted_utc = 0
		g.db.add(c)

		c.author.truescore += c.upvotes + c.downvotes - 1
		g.db.add(c.author)

		if not (c.parent_post in ADMIGGER_THREADS and c.level == 1):
			v.comment_count += 1
			g.db.add(v)

		for media_usage in c.media_usages:
			media_usage.deleted_utc = None
			g.db.add(media_usage)

		cache.delete_memoized(comment_idlist)

		if c.parent_post:
			for sort in COMMENT_SORTS.keys():
				cache.delete(f'post_{c.parent_post}_{sort}')

	return {"message": "Comment undeleted!"}

@app.post("/pin_comment_op/<int:cid>")
@feature_required('PINS')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def pin_comment_op(cid, v):

	comment = get_comment(cid, v=v)

	if not comment.pinned:
		if v.id != comment.post.author_id: stop(403)

		if comment.post.ghost: comment.pinned = "(OP)"
		else: comment.pinned = v.username + " (OP)"

		g.db.add(comment)

		comment.pin_parents()

		if v.id != comment.author_id:
			if comment.post.ghost: message = f"OP has pinned {comment.textlink}"
			else: message = f"@{v.username} (OP) has pinned {comment.textlink}"
			send_repeatable_notification(comment.author_id, message)

	return {"message": "Comment pinned!"}


@app.post("/unpin_comment_op/<int:cid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def unpin_comment_op(cid, v):

	comment = get_comment(cid, v=v)

	if comment.pinned:
		if v.id != comment.post.author_id: stop(403)

		if not comment.pinned.endswith(" (OP)"):
			stop(403, "You can only unpin comments you have pinned!")

		comment.pinned = None
		comment.pinned_utc = None
		g.db.add(comment)

		comment.unpin_parents()

		if v.id != comment.author_id:
			message = f"@{v.username} (OP) has unpinned {comment.textlink}"
			send_repeatable_notification(comment.author_id, message)
	return {"message": "Comment unpinned!"}


@app.post("/pin_comment_wall_owner/<int:cid>")
@feature_required('PINS')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def pin_comment_wall_owner(cid, v):
	comment = get_comment(cid, v=v)

	if not comment.pinned:
		if v.id != comment.wall_user_id:
			stop(403, "You can't pin comments on the walls of other users!")

		existing = g.db.query(Comment.id).join(Comment.author).filter(
			Comment.wall_user_id == v.id,
			Comment.pinned.like('% (Wall Owner)'),
			User.shadowbanned == None,
		).one_or_none()

		if existing:
			abort(403, "You can only pin one comment on your wall!")

		comment.pinned = v.username + " (Wall Owner)"

		g.db.add(comment)

		comment.pin_parents()

	return {"message": "Comment pinned!"}


@app.post("/unpin_comment_wall_owner/<int:cid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def unpin_comment_wall_owner(cid, v):
	comment = get_comment(cid, v=v)

	if comment.pinned:
		if v.id != comment.wall_user_id:
			stop(403, "You can't unpin comments on the walls of other users!")

		if not comment.pinned.endswith(" (Wall Owner)"):
			stop(403, "You can only unpin comments you have pinned!")

		comment.pinned = None
		comment.pinned_utc = None
		g.db.add(comment)

		comment.unpin_parents()

	return {"message": "Comment unpinned!"}


@app.post("/save_comment/<int:cid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def save_comment(cid, v):

	comment = get_comment(cid)

	save = g.db.query(CommentSaveRelationship).filter_by(user_id=v.id, comment_id=comment.id).one_or_none()

	if not save:
		new_save=CommentSaveRelationship(user_id=v.id, comment_id=comment.id)
		g.db.add(new_save)


	return {"message": "Comment saved!"}

@app.post("/unsave_comment/<int:cid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def unsave_comment(cid, v):

	comment = get_comment(cid)

	save = g.db.query(CommentSaveRelationship).filter_by(user_id=v.id, comment_id=comment.id).one_or_none()

	if save:
		g.db.delete(save)

	return {"message": "Comment unsaved!"}


def diff_words(answer, guess):
	"""
	Return a list of numbers corresponding to the char's relevance.
	-1 means char is not in solution or the character appears too many times in the guess
	0 means char is in solution but in the wrong spot
	1 means char is in the correct spot
	"""
	diffs = [
			1 if cs == cg else -1 for cs, cg in zip(answer, guess)
		]
	char_freq = Counter(
		c_guess for c_guess, diff, in zip(answer, diffs) if diff == -1
	)
	for i, cg in enumerate(guess):
		if diffs[i] == -1 and cg in char_freq and char_freq[cg] > 0:
			char_freq[cg] -= 1
			diffs[i] = 0
	return diffs


@app.post("/toggle_comment_nsfw/<int:cid>")
@feature_required('NSFW_MARKING')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def toggle_comment_nsfw(cid, v):
	comment = get_comment(cid)

	if comment.author_id != v.id and v.admin_level < PERMS['POST_COMMENT_MODERATION'] and not (comment.post and v.mods_hole(comment.post.hole)) and comment.wall_user_id != v.id:
		stop(403)

	comment.nsfw = not comment.nsfw
	g.db.add(comment)

	if comment.author_id != v.id:
		if v.admin_level >= PERMS['POST_COMMENT_MODERATION']:
			ma = ModAction(
					kind = "set_nsfw_comment" if comment.nsfw else "unset_nsfw_comment",
					user_id = v.id,
					target_comment_id = comment.id,
				)
			g.db.add(ma)
		elif comment.post and v.mods_hole(comment.post.hole):
			ma = HoleAction(
					hole = comment.post.hole,
					kind = "set_nsfw_comment" if comment.nsfw else "unset_nsfw_comment",
					user_id = v.id,
					target_comment_id = comment.id,
				)
			g.db.add(ma)

	if comment.nsfw: return {"message": "Comment has been marked as NSFW!"}
	else: return {"message": "Comment has been unmarked as NSFW!"}

@app.post("/edit_comment/<int:cid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def edit_comment(cid, v):
	c = get_comment(cid, v=v)

	if time.time() - c.created_utc > 3*24*60*60 and not (c.post and c.post.draft) and v.admin_level < PERMS["IGNORE_EDITING_LIMIT"] and v.id not in EXEMPT_FROM_EDITING_LIMIT:
		stop(403, "You can't edit comments older than 3 days!")

	if c.is_banned:
		stop(403, "You can't edit comments that were removed by admins!")

	if c.author_id != v.id and v.admin_level < PERMS['POST_COMMENT_EDITING']:
		stop(403)

	if not c.parent_post and not c.wall_user_id:
		stop(403)

	body = request.values.get("body", "").strip()
	if len(body) > COMMENT_BODY_LENGTH_LIMIT:
		stop(400, f'Comment body is too long (max {COMMENT_BODY_LENGTH_LIMIT} characters)')

	if len(body) < 1 and not (request.files.get("file") and not g.is_tor):
		stop(400, "You have to actually type something!")

	body = body.replace('@jannies', '!jannies')

	if body != c.body or request.files.get("file") and not g.is_tor:
		if not c.distinguished:
			if c.author.longpost and (len(body) < 280 or ' [](' in body or body.startswith('[](')):
				stop(403, "You have to type more than 280 characters!")
			elif c.author.bird and len(body) > 140:
				stop(403, "You have to type less than 140 characters!")

		execute_antispam_comment_check(body, v)

		body = process_files(request.files, v, body)
		if len(body) > COMMENT_BODY_LENGTH_LIMIT:
			stop(400, f'Comment body is too long (max {COMMENT_BODY_LENGTH_LIMIT} characters)')

		body_html = sanitize(body, golden=False, limit_pings=5, showmore=(not v.hieroglyphs), commenters_ping_post_id=c.parent_post, obj=c, author=c.author)

		if len(body_html) > COMMENT_BODY_HTML_LENGTH_LIMIT:
			stop(400, "Rendered comment is too long!")

		if c.author.hieroglyphs and not c.distinguished and c.parent_post not in ADMIGGER_THREADS and marseyaward_body_regex.search(body_html):
			stop(403, "You can only type emojis!")

		if int(time.time()) - c.created_utc > 60 * 3:
			edit_log = CommentEdit(
				comment_id=c.id,
				old_body=c.body,
				old_body_html=c.body_html,
			)
			g.db.add(edit_log)

		oldtext = c.body

		c.body = body

		c.body_html = body_html

		execute_blackjack(v, c, c.body, "comment")

		if not complies_with_chud(c):
			stop(403, f'You have to include "{c.author.chud_phrase}" in your comment!')

		process_options(v, c)

		if v.id == c.author_id:
			if int(time.time()) - c.created_utc > 60 * 3:
				c.edited_utc = int(time.time())
		else:
			ma = ModAction(
				kind="edit_comment",
				user_id=v.id,
				target_comment_id=c.id
			)
			g.db.add(ma)

		g.db.add(c)

		notify_users = NOTIFY_USERS(body, v, oldtext=oldtext, ghost=c.ghost, obj=c, commenters_ping_post_id=c.parent_post)

		if notify_users == 'everyone':
			alert_everyone(c.id)
		else:
			notify_users -= BOT_IDs

			if c.pinned == "Admin Note":
				notify_users = [x[0] for x in g.db.query(User.id).filter(User.id.in_(notify_users), User.admin_level >= PERMS['ADMIN_NOTES']).all()]

			for x in notify_users:
				notif = g.db.query(Notification).filter_by(comment_id=c.id, user_id=x).one_or_none()
				if not notif:
					n = Notification(comment_id=c.id, user_id=x)
					g.db.add(n)
					push_notif({x}, f'New mention of you by @{c.author_name}', c.body, c)

		g.db.commit()
		gevent.spawn(postprocess_comment, c.body, c.body_html, c.id)
	else:
		stop(400, "You need to change something!")


	return {
			"body": c.body,
			"comment": c.realbody(v),
			"ping_cost": c.ping_cost,
			"edited_string": c.edited_string,
		}

@app.get("/!commenters/<int:pid>/<int:time>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def commenters(v, pid, time):
	p = get_post(pid)

	if p.ghost:
		stop(403, "You can't see commenters on ghost threads!")

	users = g.db.query(User, Comment.id, Comment.created_utc).distinct(User.id).join(
		Comment, Comment.author_id == User.id
	).filter(
		Comment.parent_post == pid,
		Comment.created_utc < time-1,
		User.id.notin_(BOT_IDs),
	).order_by(User.id, Comment.created_utc).all()

	users = sorted(users, key=lambda x: x[1])

	return render_template('commenters.html', v=v, users=users)



def postprocess_comment(comment_body, comment_body_html, cid):
	with app.app_context():
		li = list(reddit_s_url_regex.finditer(comment_body)) + list(tiktok_t_url_regex.finditer(comment_body))

		if not li: return

		for i in li:
			old = i.group(0)
			new = normalize_url_gevent(old)
			comment_body = comment_body.replace(old, new)
			comment_body_html = comment_body_html.replace(old, new)

		g.db = db_session()

		c = g.db.query(Comment).filter_by(id=cid).options(load_only(Comment.id)).one_or_none()
		c.body = comment_body
		c.body_html = comment_body_html
		g.db.add(c)

		g.db.commit()
		g.db.close()

	stdout.flush()


@app.post("/distinguish_comment/<int:c_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def admin_distinguish_comment(c_id, v):
	comment = get_comment(c_id, v=v)

	if v.admin_level < PERMS['POST_COMMENT_DISTINGUISH'] and not (comment.parent_post and v.mods_hole(comment.post.hole)):
		stop(403, "You can't distinguish this comment")

	if comment.distinguished:
		comment.distinguished = False
		kind = 'undistinguish_comment'
	else:
		comment.distinguished = True
		kind = 'distinguish_comment'

	g.db.add(comment)

	if v.admin_level >= PERMS['POST_COMMENT_DISTINGUISH']:
		cls = ModAction
	else:
		cls = HoleAction

	ma = cls(
		kind=kind,
		user_id=v.id,
		target_comment_id=comment.id
	)
	if cls == HoleAction:
		ma.hole = comment.post.hole
	g.db.add(ma)

	if comment.distinguished: return {"message": "Comment distinguished!"}
	else: return {"message": "Comment undistinguished!"}
