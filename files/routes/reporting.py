from flask import g

from files.classes.flags import Flag, CommentFlag
from files.classes.mod_logs import ModAction
from files.classes.sub_logs import SubAction
from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.get import *
from files.helpers.sanitize import filter_emojis_only
from files.routes.front import frontlist
from files.routes.wrappers import *
from files.__main__ import app, limiter, cache

@app.post("/report/post/<int:pid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def flag_post(pid, v):
	if v.is_muted: abort(403, "You are forbidden from making reports!")

	post = get_post(pid)
	reason = request.values.get("reason", "").strip()
	execute_under_siege(v, post, reason, 'report')
	execute_blackjack(v, post, reason, 'report')
	reason = reason[:100]
	og_flair = reason[1:]
	reason_html = filter_emojis_only(reason)
	if len(reason_html) > 350:
		abort(400, "Report reason too long!")

	if reason.startswith('!') and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or post.sub and v.mods(post.sub)):
		post.flair = reason_html[1:]
		g.db.add(post)
		if v.admin_level >= PERMS['POST_COMMENT_MODERATION']:
			ma=ModAction(
				kind="flair_post",
				user_id=v.id,
				target_post_id=post.id,
				_note=f'"{post.flair}"'
			)
			g.db.add(ma)
			position = 'a site admin'
		else:
			ma = SubAction(
				sub=post.sub,
				kind="flair_post",
				user_id=v.id,
				target_post_id=post.id,
				_note=f'"{post.flair}"'
			)
			g.db.add(ma)
			position = f'a /h/{post.sub} mod'

		if v.id != post.author_id:
			message = f'@{v.username} ({position}) has flaired [{post.title}]({post.shortlink}) with the flair: `"{og_flair}"`'
			send_repeatable_notification(post.author_id, message)

		return {"message": "Post flaired successfully!"}

	moved = move_post(post, v, reason)
	if moved: return {"message": moved}

	existing = g.db.query(Flag.post_id).filter_by(user_id=v.id, post_id=post.id).one_or_none()
	if existing: abort(409, "You already reported this post!")
	flag = Flag(post_id=post.id, user_id=v.id, reason=reason_html)
	g.db.add(flag)

	if v.id != post.author_id and not v.shadowbanned and not post.author.has_blocked(v):
		message = f'@{v.username} reported [{post.title}]({post.shortlink})\n\n> {reason}'
		send_repeatable_notification(post.author_id, message)

	return {"message": "Post reported!"}


@app.post("/report/comment/<int:cid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def flag_comment(cid, v):
	if v.is_muted: abort(403, "You are forbidden from making reports!")

	comment = get_comment(cid)

	existing = g.db.query(CommentFlag.comment_id).filter_by(user_id=v.id, comment_id=comment.id).one_or_none()
	if existing: abort(409, "You already reported this comment!")

	reason = request.values.get("reason", "").strip()
	execute_under_siege(v, comment, reason, 'report')
	execute_blackjack(v, comment, reason, 'report')
	reason = reason[:100]
	reason_html = filter_emojis_only(reason)

	if len(reason_html) > 350: abort(400, "Too long!")

	flag = CommentFlag(comment_id=comment.id, user_id=v.id, reason=reason_html)
	g.db.add(flag)

	if v.id != comment.author_id and not v.shadowbanned and not comment.author.has_blocked(v):
		message = f'@{v.username} reported your [comment]({comment.shortlink})\n\n> {reason}'
		send_repeatable_notification(comment.author_id, message)

	return {"message": "Comment reported!"}


@app.post('/del_report/post/<int:pid>/<int:uid>')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("100/minute;300/hour;2000/day")
@limiter.limit("100/minute;300/hour;2000/day", key_func=get_ID)
@admin_level_required(PERMS['FLAGS_REMOVE'])
def remove_report_post(v, pid, uid):
	try:
		pid = int(pid)
		uid = int(uid)
	except: abort(404)
	report = g.db.query(Flag).filter_by(post_id=pid, user_id=uid).one_or_none()

	if report:
		g.db.delete(report)

		ma=ModAction(
			kind="delete_report",
			user_id=v.id,
			target_post_id=pid
		)

		g.db.add(ma)
	return {"message": "Report removed successfully!"}


@app.post('/del_report/comment/<int:cid>/<int:uid>')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("100/minute;300/hour;2000/day")
@limiter.limit("100/minute;300/hour;2000/day", key_func=get_ID)
@admin_level_required(PERMS['FLAGS_REMOVE'])
def remove_report_comment(v, cid, uid):
	try:
		cid = int(cid)
		uid = int(uid)
	except: abort(404)
	report = g.db.query(CommentFlag).filter_by(comment_id=cid, user_id=uid).one_or_none()

	if report:
		g.db.delete(report)

		ma=ModAction(
			kind="delete_report",
			user_id=v.id,
			target_comment_id=cid
		)

		g.db.add(ma)
	return {"message": "Report removed successfully!"}

def move_post(post:Post, v:User, reason:str) -> Union[bool, str]:
	if not reason.startswith('/h/') and not reason.startswith('h/'):
		return False

	sub_from = post.sub
	sub_to = get_sub_by_name(reason, graceful=True)
	sub_to = sub_to.name if sub_to else None

	can_move_post = v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or (post.sub and v.mods(sub_from))
	if sub_from != 'chudrama': # posts can only be moved out of /h/chudrama by admins
		can_move_post = can_move_post or post.author_id == v.id
	if not can_move_post: return False

	if sub_to == None:
		sub_to_in_notif = 'the main feed'
	else:
		sub_to_in_notif = f'/h/{sub_to}'

	if sub_from == sub_to: abort(409, f"Post is already in {sub_to_in_notif}")

	if post.author.exiled_from(sub_to):
		abort(403, f"User is exiled from this {HOLE_NAME}!")

	if sub_to == 'changelog':
		abort(403, "/h/changelog is archived!")

	if sub_to in {'furry','vampire','racist','femboy'} and not v.client and not post.author.house.lower().startswith(sub_to):
		if v.id == post.author_id:
			abort(403, f"You need to be a member of House {sub_to.capitalize()} to post in /h/{sub_to}")
		else:
			abort(403, f"@{post.author_name} needs to be a member of House {sub_to.capitalize()} for their post to be moved to /h/{sub_to}")

	post.sub = sub_to
	post.hole_pinned = None
	g.db.add(post)

	if sub_to == 'chudrama':
		post.bannedfor = None
		post.chuddedfor = None

	if v.id != post.author_id:
		sub_from_str = 'main feed' if sub_from is None else \
			f'<a href="/h/{sub_from}">/h/{sub_from}</a>'
		sub_to_str = 'main feed' if sub_to is None else \
			f'<a href="/h/{sub_to}">/h/{sub_to}</a>'

		if v.admin_level:
			ma = ModAction(
				kind='move_hole',
				user_id=v.id,
				target_post_id=post.id,
				_note=f'{sub_from_str} → {sub_to_str}',
			)
			g.db.add(ma)
		else:
			ma = SubAction(
				sub=sub_from,
				kind='move_hole',
				user_id=v.id,
				target_post_id=post.id,
				_note=f'{sub_from_str} → {sub_to_str}',
			)
			g.db.add(ma)

		if v.admin_level >= PERMS['POST_COMMENT_MODERATION']: position = 'a site admin'
		else: position = f'a /h/{sub_from} mod'

		if sub_from == None:
			sub_from_in_notif = 'the main feed'
		else:
			sub_from_in_notif = f'/h/{sub_from}'

		message = f"@{v.username} ({position}) has moved [{post.title}]({post.shortlink}) from {sub_from_in_notif} to {sub_to_in_notif}"
		send_repeatable_notification(post.author_id, message)

	cache.delete_memoized(frontlist)

	return f"Post moved to {sub_to_in_notif} successfully!"
