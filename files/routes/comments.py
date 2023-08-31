import os
from collections import Counter
from json import loads
from shutil import copyfile

import gevent

from files.classes import *
from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.cloudflare import purge_files_in_cache
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.marsify import marsify
from files.helpers.media import *
from files.helpers.owoify import owoify
from files.helpers.sharpen import sharpen
from files.helpers.regex import *
from files.helpers.slots import *
from files.helpers.treasure import *
from files.routes.front import comment_idlist
from files.routes.routehelpers import execute_shadowban_viewers_and_voters
from files.routes.wrappers import *
from files.routes.static import badge_list
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
@app.get("/h/<sub>/comment/<int:cid>")
@app.get("/h/<sub>/post/<int:pid>/<anything>/<int:cid>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_desired_with_logingate
def post_pid_comment_cid(cid, v, pid=None, anything=None, sub=None):

	comment = get_comment(cid, v=v)

	if not User.can_see(v, comment): abort(403)

	if comment.parent_post:
		post = comment.parent_post
	elif comment.wall_user_id:
		return redirect(f"/id/{comment.wall_user_id}/wall/comment/{comment.id}")
	else:
		return redirect(f"/notification/{comment.id}")

	if v and request.values.get("read"):
		gevent.spawn(_mark_comment_as_read, comment.id, v.id)

	post = get_post(post, v=v)

	if not (v and v.client) and post.over_18 and not (v and v.over_18) and not session.get('over_18_cookies', 0) >= int(time.time()):
		return render_template("errors/nsfw.html", v=v), 403

	try: context = min(int(request.values.get("context", 8)), 8)
	except: context = 8
	comment_info = comment
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
		if post.is_banned and not (v and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or post.author_id == v.id)): template = "post_banned.html"
		else: template = "post.html"
		return render_template(template, v=v, p=post, sort=sort, comment_info=comment_info, render_replies=True, sub=post.subr)

@app.post("/comment")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("20/minute;200/hour;1000/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("20/minute;200/hour;1000/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@is_not_banned
def comment(v):
	parent_fullname = request.values.get("parent_fullname").strip()
	if len(parent_fullname) < 3: abort(400)
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
			abort(403, "You can't post top-level comments in this thread!")

		if SITE == 'rdrama.net' and parent.id == 33652:
			notify_op = False

		ghost = parent.ghost
	elif parent_fullname.startswith("c_"):
		parent = get_comment(id, v=v)
		post_target = get_post(parent.parent_post, v=v, graceful=True) or get_account(parent.wall_user_id, v=v, include_blocks=True)
		parent_comment_id = parent.id
		if parent.author_id == v.id: rts = True
		if not v.can_post_in_ghost_threads and isinstance(post_target, Post) and post_target.ghost:
			abort(403, f"You need {TRUESCORE_GHOST_MINIMUM} truescore to post in ghost threads")
		ghost = parent.ghost
	else: abort(404)

	level = 1 if isinstance(parent, (Post, User)) else int(parent.level) + 1
	parent_user = parent if isinstance(parent, User) else parent.author
	posting_to_post = isinstance(post_target, Post)



	if posting_to_post and not User.can_see(v, parent):
		abort(403)

	if not isinstance(parent, User) and parent.deleted_utc != 0:
		if isinstance(parent, Post):
			abort(403, "You can't reply to deleted posts!")
		else:
			abort(403, "You can't reply to deleted comments!")

	if posting_to_post:
		sub = post_target.sub
		if sub and v.exiler_username(sub): abort(403, f"You're exiled from /h/{sub}")
		if sub in {'furry','vampire','racist','femboy','edgy'} and not v.client and not v.house.lower().startswith(sub):
			abort(403, f"You need to be a member of House {sub.capitalize()} to comment in /h/{sub}")

	if level > COMMENT_MAX_DEPTH: abort(400, f"Max comment level is {COMMENT_MAX_DEPTH}")

	body = request.values.get("body", "")
	body = body[:COMMENT_BODY_LENGTH_LIMIT].strip()

	if not posting_to_post or post_target.id not in ADMIGGER_THREADS:
		if v.longpost and (len(body) < 280 or ' [](' in body or body.startswith('[](')):
			abort(403, "You have to type more than 280 characters!")
		elif v.bird and len(body) > 140:
			abort(403, "You have to type less than 140 characters!")

	if not body and not request.files.get('file'): abort(400, "You need to actually write something!")

	if v.admin_level < PERMS['POST_COMMENT_MODERATION'] and parent_user.any_block_exists(v):
		abort(403, "You can't reply to users who have blocked you or users that you have blocked!")

	if request.files.get("file") and not g.is_tor:
		files = request.files.getlist('file')[:20]


		if files:
			media_ratelimit(v)

		for file in files:
			if f'[{file.filename}]' not in body:
				continue

			if file.content_type.startswith('image/'):
				oldname = f'/images/{time.time()}'.replace('.','') + '.webp'
				file.save(oldname)
				image = process_image(oldname, v)
				if image == "": abort(400, "Image upload failed")
				if posting_to_post and v.admin_level >= PERMS['USE_ADMIGGER_THREADS']:
					def process_sidebar_or_banner(type, resize=0):
						li = sorted(os.listdir(f'files/assets/images/{SITE_NAME}/{type}'),
							key=lambda e: int(e.split('.webp')[0]))[-1]
						num = int(li.split('.webp')[0]) + 1
						filename = f'files/assets/images/{SITE_NAME}/{type}/{num}.webp'
						copyfile(oldname, filename)
						process_image(filename, v, resize=resize)

					if post_target.id == SIDEBAR_THREAD:
						process_sidebar_or_banner('sidebar', 400)
					elif post_target.id == BANNER_THREAD:
						banner_width = 1200
						process_sidebar_or_banner('banners', banner_width)
					elif post_target.id == BADGE_THREAD:
						try:
							json_body = '{' + body.split('{')[1].split('}')[0] + '}'
							badge_def = loads(json_body)
							name = badge_def["name"]

							if len(name) > 50:
								abort(400, "Badge name is too long!")

							if not badge_name_regex.fullmatch(name):
								abort(400, "Invalid badge name!")

							existing = g.db.query(BadgeDef).filter_by(name=name).one_or_none()
							if existing: abort(409, "A badge with this name already exists!")

							badge = BadgeDef(name=name, description=badge_def["description"])
							g.db.add(badge)
							g.db.flush()
							filename = f'files/assets/images/{SITE_NAME}/badges/{badge.id}.webp'
							copyfile(oldname, filename)
							process_image(filename, v, resize=300, trim=True)
							purge_files_in_cache(f"{SITE_FULL_IMAGES}/i/{SITE_NAME}/badges/{badge.id}.webp")
							cache.delete_memoized(badge_list)
						except Exception as e:
							abort(400, str(e))
				body = body.replace(f'[{file.filename}]', f' {image} ', 1)
			elif file.content_type.startswith('video/'):
				body = body.replace(f'[{file.filename}]', f' {process_video(file, v)} ', 1)
			elif file.content_type.startswith('audio/'):
				body = body.replace(f'[{file.filename}]', f' {SITE_FULL}{process_audio(file, v)} ', 1)
			else:
				abort(415)

	body = body.replace('\n ', '\n').replace('\r', '')
	body = body[:COMMENT_BODY_LENGTH_LIMIT].strip()

	if v.admin_level >= PERMS['USE_ADMIGGER_THREADS'] and posting_to_post and post_target.id == SNAPPY_THREAD and level == 1:
		with open(f"snappy_{SITE_NAME}.txt", "r+", encoding="utf-8") as f:
			body_for_checking = '\n{[para]}\n' + body + '\n{[para]}\n'
			if body_for_checking in f.read():
				abort(400, "Snappy quote already exists!")
			f.write('\n{[para]}\n' + body)

	body_for_sanitize = body
	if v.owoify: body_for_sanitize = owoify(body_for_sanitize)
	if v.marsify and not v.chud: body_for_sanitize = marsify(body_for_sanitize)
	if v.sharpen: body_for_sanitize = sharpen(body_for_sanitize)

	body_html = sanitize(body_for_sanitize, limit_pings=5, showmore=(not v.marseyawarded), count_emojis=not v.marsify)

	if post_target.id not in ADMIGGER_THREADS and not (v.chud and v.chud_phrase in body.lower()):
		existing = g.db.query(Comment.id).filter(
			Comment.author_id == v.id,
			Comment.deleted_utc == 0,
			Comment.parent_comment_id == parent_comment_id,
			Comment.parent_post == post_target.id if posting_to_post else None,
			Comment.wall_user_id == post_target.id if not posting_to_post else None,
			Comment.body_html == body_html
		).first()
		if existing: abort(409, f"You already made that comment: /comment/{existing.id}#context")

	execute_antispam_comment_check(body, v)
	execute_antispam_duplicate_comment_check(v, body_html)

	if v.marseyawarded and marseyaward_body_regex.search(body_html) and not (posting_to_post and post_target.id in ADMIGGER_THREADS):
		abort(403, "You can only type marseys!")

	if len(body_html) > COMMENT_BODY_HTML_LENGTH_LIMIT:
		abort(400, "Comment too long!")

	is_bot = v.client is not None and v.id not in BOT_SYMBOL_HIDDEN

	chudded = v.chud and not (posting_to_post and post_target.sub == 'chudrama')

	c = Comment(author_id=v.id,
				parent_post=post_target.id if posting_to_post else None,
				wall_user_id=post_target.id if not posting_to_post else None,
				parent_comment_id=parent_comment_id,
				level=level,
				over_18=post_target.over_18 if posting_to_post else False,
				is_bot=is_bot,
				app_id=v.client.application.id if v.client else None,
				body_html=body_html,
				body=body,
				ghost=ghost,
				chudded=chudded,
				rainbowed=bool(v.rainbow),
				queened=bool(v.queen),
				sharpened=bool(v.sharpen),
			)

	c.upvotes = 1
	g.db.add(c)
	g.db.flush()

	process_poll_options(v, c)

	execute_blackjack(v, c, c.body, "comment")
	execute_under_siege(v, c, c.body, "comment")

	if c.level == 1: c.top_comment_id = c.id
	else: c.top_comment_id = parent.top_comment_id

	if not complies_with_chud(c):
		c.is_banned = True
		c.ban_reason = "AutoJanny"
		g.db.add(c)

		body = CHUD_MSG.format(username=v.username, type='comment', CHUD_PHRASE=v.chud_phrase)
		body_jannied_html = sanitize(body)

		c_jannied = Comment(author_id=AUTOJANNY_ID,
			parent_post=post_target.id if posting_to_post else None,
			wall_user_id=post_target.id if not posting_to_post else None,
			distinguish_level=6,
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

	if not v.shadowbanned:
		notify_users = NOTIFY_USERS(body, v, ghost=c.ghost, log_cost=c)

		if notify_users == 'everyone':
			alert_everyone(c.id)
		else:
			push_notif(notify_users, f'New mention of you by @{c.author_name}', c.body, c)

			if c.level == 1 and posting_to_post:
				subscriber_ids = [x[0] for x in g.db.query(Subscription.user_id).filter(Subscription.post_id == post_target.id, Subscription.user_id != v.id)]

				notify_users.update(subscriber_ids)

				push_notif(subscriber_ids, f'New comment in subscribed thread by @{c.author_name}', c.body, c)

			if parent_user.id != v.id and notify_op:
				notify_users.add(parent_user.id)

			for x in notify_users-BOT_IDs:
				n = Notification(comment_id=c.id, user_id=x)
				g.db.add(n)

			if parent_user.id != v.id:
				if isinstance(parent, User):
					title = f"New comment on your wall by @{c.author_name}"
				else:
					title = f'New reply by @{c.author_name}'

				if len(c.body) > PUSH_NOTIF_LIMIT: notifbody = c.body[:PUSH_NOTIF_LIMIT] + '...'
				else: notifbody = c.body

				push_notif({parent_user.id}, title, notifbody, c)

	vote = CommentVote(user_id=v.id,
						 comment_id=c.id,
						 vote_type=1,
						 coins=0
						 )
	g.db.add(vote)
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

	if c.level > 5:
		n = g.db.query(Notification).filter_by(
			comment_id=c.parent_comment.parent_comment.parent_comment.parent_comment_id,
			user_id=c.parent_comment.author_id,
		).one_or_none()
		if n: g.db.delete(n)

	g.db.flush()

	if c.parent_post:
		for sort in COMMENT_SORTS:
			cache.delete(f'post_{c.parent_post}_{sort}')

	if v.client: return c.json
	return {"comment": render_template("comments.html", v=v, comments=[c])}

@app.post("/delete/comment/<int:cid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def delete_comment(cid, v):
	if v.id == 253: abort(403)
	c = get_comment(cid, v=v)
	if not c.deleted_utc:
		if c.author_id != v.id: abort(403)
		c.deleted_utc = int(time.time())
		g.db.add(c)

		if not (c.parent_post in ADMIGGER_THREADS and c.level == 1):
			v.comment_count -= 1
			g.db.add(v)

		cache.delete_memoized(comment_idlist)

		if c.parent_post:
			for sort in COMMENT_SORTS:
				cache.delete(f'post_{c.parent_post}_{sort}')

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
		if c.author_id != v.id: abort(403)
		c.deleted_utc = 0
		g.db.add(c)

		if not (c.parent_post in ADMIGGER_THREADS and c.level == 1):
			v.comment_count += 1
			g.db.add(v)

		cache.delete_memoized(comment_idlist)

		if c.parent_post:
			for sort in COMMENT_SORTS:
				cache.delete(f'post_{c.parent_post}_{sort}')

	return {"message": "Comment undeleted!"}

@app.post("/pin_comment/<int:cid>")
@feature_required('PINS')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def pin_comment(cid, v):

	comment = get_comment(cid, v=v)

	if not comment.stickied:
		if v.id != comment.post.author_id: abort(403)

		if comment.post.ghost: comment.stickied = "(OP)"
		else: comment.stickied = v.username + " (OP)"

		g.db.add(comment)

		if v.id != comment.author_id:
			if comment.post.ghost: message = f"OP has pinned your [comment]({comment.shortlink})"
			else: message = f"@{v.username} (OP) has pinned your [comment]({comment.shortlink})"
			send_repeatable_notification(comment.author_id, message)

	return {"message": "Comment pinned!"}


@app.post("/unpin_comment/<int:cid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def unpin_comment(cid, v):

	comment = get_comment(cid, v=v)

	if comment.stickied:
		if v.id != comment.post.author_id: abort(403)

		if not comment.stickied.endswith(" (OP)"):
			abort(403, "You can only unpin comments you have pinned!")

		comment.stickied = None
		g.db.add(comment)

		if v.id != comment.author_id:
			message = f"@{v.username} (OP) has unpinned your [comment]({comment.shortlink})"
			send_repeatable_notification(comment.author_id, message)
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

	if comment.author_id != v.id and v.admin_level < PERMS['POST_COMMENT_MODERATION'] and not (comment.post.sub and v.mods(comment.post.sub)):
		abort(403)

	if comment.over_18 and v.is_permabanned:
		abort(403)

	comment.over_18 = not comment.over_18
	g.db.add(comment)

	if comment.author_id != v.id:
		if v.admin_level >= PERMS['POST_COMMENT_MODERATION']:
			ma = ModAction(
					kind = "set_nsfw_comment" if comment.over_18 else "unset_nsfw_comment",
					user_id = v.id,
					target_comment_id = comment.id,
				)
			g.db.add(ma)
		else:
			ma = SubAction(
					sub = comment.post.sub,
					kind = "set_nsfw_comment" if comment.over_18 else "unset_nsfw_comment",
					user_id = v.id,
					target_comment_id = comment.id,
				)
			g.db.add(ma)

	if comment.over_18: return {"message": "Comment has been marked as +18!"}
	else: return {"message": "Comment has been unmarked as +18!"}

@app.post("/edit_comment/<int:cid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("10/minute;100/hour;200/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("10/minute;100/hour;200/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@is_not_permabanned
def edit_comment(cid, v):
	c = get_comment(cid, v=v)

	if time.time() - c.created_utc > 7*24*60*60 and not (c.post and c.post.private) \
	and v.admin_level < PERMS["IGNORE_1WEEk_EDITING_LIMIT"] and v.id not in EXEMPT_FROM_1WEEK_EDITING_LIMIT:
		abort(403, "You can't edit comments older than 1 week!")

	if c.author_id != v.id and v.admin_level < PERMS['POST_COMMENT_EDITING']:
		abort(403)

	if not c.parent_post and not c.wall_user_id:
		abort(403)

	body = request.values.get("body", "")
	body = body[:COMMENT_BODY_LENGTH_LIMIT].strip()

	if len(body) < 1 and not (request.files.get("file") and not g.is_tor):
		abort(400, "You have to actually type something!")

	if body != c.body or request.files.get("file") and not g.is_tor:

		if v.id == c.author_id:
			if v.longpost and (len(body) < 280 or ' [](' in body or body.startswith('[](')):
				abort(403, "You have to type more than 280 characters!")
			elif v.bird and len(body) > 140:
				abort(403, "You have to type less than 140 characters!")

		execute_antispam_comment_check(body, v)

		body = process_files(request.files, v, body)
		body = body[:COMMENT_BODY_LENGTH_LIMIT].strip() # process_files potentially adds characters to the post

		body_for_sanitize = body

		if v.id == c.author_id:
			if v.owoify:
				body_for_sanitize = owoify(body_for_sanitize)
			if v.marsify and not v.chud:
				body_for_sanitize = marsify(body_for_sanitize)

		if c.sharpened:
			body_for_sanitize = sharpen(body_for_sanitize)

		body_html = sanitize(body_for_sanitize, golden=False, limit_pings=5, showmore=(not v.marseyawarded))

		if len(body_html) > COMMENT_BODY_HTML_LENGTH_LIMIT: abort(400)

		if v.id == c.author_id and v.marseyawarded and marseyaward_body_regex.search(body_html):
			abort(403, "You can only type marseys!")

		oldtext = c.body

		c.body = body

		c.body_html = body_html

		execute_blackjack(v, c, c.body, "comment")

		if not complies_with_chud(c):
			abort(403, f'You have to include "{v.chud_phrase}" in your comment!')

		process_poll_options(v, c)

		if v.id == c.author_id:
			if int(time.time()) - c.created_utc > 60 * 3:
				c.edited_utc = int(time.time())
		else:
			ma=ModAction(
				kind="edit_comment",
				user_id=v.id,
				target_comment_id=c.id
			)
			g.db.add(ma)

		g.db.add(c)

		notify_users = NOTIFY_USERS(body, v, oldtext=oldtext, ghost=c.ghost, log_cost=c)

		if notify_users == 'everyone':
			alert_everyone(c.id)
		else:
			for x in notify_users-BOT_IDs:
				notif = g.db.query(Notification).filter_by(comment_id=c.id, user_id=x).one_or_none()
				if not notif:
					n = Notification(comment_id=c.id, user_id=x)
					g.db.add(n)
					push_notif({x}, f'New mention of you by @{c.author_name}', c.body, c)


	g.db.flush()
	return {
			"body": c.body,
			"comment": c.realbody(v),
			"ping_cost": c.ping_cost,
			"edited_string": c.edited_string,
		}
