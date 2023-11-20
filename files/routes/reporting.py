from flask import g

from files.classes.reports import Report, CommentReport
from files.classes.mod_logs import ModAction
from files.classes.hole_logs import HoleAction
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
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def report_post(pid, v):
	post = get_post(pid)
	reason = request.values.get("reason", "").strip()
	execute_under_siege(v, post, reason, 'report')
	execute_blackjack(v, post, reason, 'report')
	reason = reason[:100]
	og_flair = reason[1:]
	reason_html = filter_emojis_only(reason)
	if len(reason_html) > 350:
		abort(400, "Report reason too long!")

	if reason.startswith('!') and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or post.hole and v.mods(post.hole)):
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
			ma = HoleAction(
				hole=post.hole,
				kind="flair_post",
				user_id=v.id,
				target_post_id=post.id,
				_note=f'"{post.flair}"'
			)
			g.db.add(ma)
			position = f'a /h/{post.hole} mod'

		if v.id != post.author_id:
			message = f'@{v.username} ({position}) has flaired [{post.title}]({post.shortlink}) with the flair: `"{og_flair}"`'
			send_repeatable_notification(post.author_id, message)

		return {"message": "Post flaired successfully!"}

	moved = move_post(post, v, reason)
	if moved: return {"message": moved}

	if v.is_muted: abort(403, "You are forbidden from making reports!")

	existing = g.db.query(Report.post_id).filter_by(user_id=v.id, post_id=post.id).one_or_none()
	if existing: abort(409, "You already reported this post!")
	report = Report(post_id=post.id, user_id=v.id, reason=reason_html)
	g.db.add(report)

	if v.id != post.author_id and not post.author.has_blocked(v) and not post.author.has_muted(v):
		message = f'@{v.username} reported [{post.title}]({post.shortlink})\n\n> {reason}'
		send_repeatable_notification(post.author_id, message)

	return {"message": "Post reported!"}


@app.post("/report/comment/<int:cid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def report_comment(cid, v):
	if v.is_muted: abort(403, "You are forbidden from making reports!")

	comment = get_comment(cid)

	existing = g.db.query(CommentReport.comment_id).filter_by(user_id=v.id, comment_id=comment.id).one_or_none()
	if existing: abort(409, "You already reported this comment!")

	reason = request.values.get("reason", "").strip()
	execute_under_siege(v, comment, reason, 'report')
	execute_blackjack(v, comment, reason, 'report')
	reason = reason[:100]
	reason_html = filter_emojis_only(reason)

	if len(reason_html) > 350: abort(400, "Too long!")

	report = CommentReport(comment_id=comment.id, user_id=v.id, reason=reason_html)
	g.db.add(report)

	if v.id != comment.author_id and not comment.author.has_blocked(v) and not comment.author.has_muted(v):
		message = f'@{v.username} reported your [comment]({comment.shortlink})\n\n> {reason}'
		send_repeatable_notification(comment.author_id, message)

	return {"message": "Comment reported!"}


@app.post('/del_report/post/<int:pid>/<int:uid>')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("100/minute;300/hour;2000/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("100/minute;300/hour;2000/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['REPORTS_REMOVE'])
def remove_report_post(v, pid, uid):
	report = g.db.query(Report).filter_by(post_id=pid, user_id=uid).one_or_none()

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
@limiter.limit("100/minute;300/hour;2000/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("100/minute;300/hour;2000/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['REPORTS_REMOVE'])
def remove_report_comment(v, cid, uid):
	report = g.db.query(CommentReport).filter_by(comment_id=cid, user_id=uid).one_or_none()

	if report:
		g.db.delete(report)

		ma=ModAction(
			kind="delete_report",
			user_id=v.id,
			target_comment_id=cid
		)

		g.db.add(ma)
	return {"message": "Report removed successfully!"}

def move_post(post, v, reason):
	if not reason.startswith('/h/') and not reason.startswith('h/'):
		return False

	if post.ghost:
		abort(403, "You can't move ghost posts into holes!")

	hole_from = post.hole
	hole_to = get_hole(reason, graceful=True)
	hole_to = hole_to.name if hole_to else None

	can_move_post = v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or (post.hole and v.mods(hole_from))
	if hole_from != 'chudrama': # posts can only be moved out of /h/chudrama by admins
		can_move_post = can_move_post or post.author_id == v.id
	if not can_move_post: return False

	if hole_to == None:
		if HOLE_REQUIRED:
			abort(403, "All posts are required to be flaired!")
		hole_to_in_notif = 'the main feed'
	else:
		hole_to_in_notif = f'/h/{hole_to}'

	if hole_from == hole_to: abort(409, f"Post is already in {hole_to_in_notif}")

	if post.author.exiler_username(hole_to):
		abort(403, f"User is exiled from this hole!")

	if hole_to == 'changelog':
		abort(403, "/h/changelog is archived!")

	if hole_to in {'furry','vampire','racist','femboy','edgy'} and not v.client and not post.author.house.lower().startswith(hole_to):
		if v.id == post.author_id:
			abort(403, f"You need to be a member of House {hole_to.capitalize()} to post in /h/{hole_to}")
		else:
			abort(403, f"@{post.author_name} needs to be a member of House {hole_to.capitalize()} for their post to be moved to /h/{hole_to}")

	post.hole = hole_to
	post.hole_pinned = None

	if hole_to == 'chudrama':
		post.bannedfor = None
		post.chuddedfor = None
		for c in post.comments:
			c.bannedfor = None
			c.chuddedfor = None
			g.db.add(c)

	g.db.add(post)

	if v.id != post.author_id:
		hole_from_str = 'main feed' if hole_from is None else \
			f'<a href="/h/{hole_from}">/h/{hole_from}</a>'
		hole_to_str = 'main feed' if hole_to is None else \
			f'<a href="/h/{hole_to}">/h/{hole_to}</a>'

		if v.admin_level >= PERMS['POST_COMMENT_MODERATION']:
			ma = ModAction(
				kind='move_hole',
				user_id=v.id,
				target_post_id=post.id,
				_note=f'{hole_from_str} → {hole_to_str}',
			)
			g.db.add(ma)
		else:
			ma = HoleAction(
				hole=hole_from,
				kind='move_hole',
				user_id=v.id,
				target_post_id=post.id,
				_note=f'{hole_from_str} → {hole_to_str}',
			)
			g.db.add(ma)

		if v.admin_level >= PERMS['POST_COMMENT_MODERATION']: position = 'a site admin'
		else: position = f'a /h/{hole_from} mod'

		if hole_from == None:
			hole_from_in_notif = 'the main feed'
		else:
			hole_from_in_notif = f'/h/{hole_from}'

		message = f"@{v.username} ({position}) has moved [{post.title}]({post.shortlink}) from {hole_from_in_notif} to {hole_to_in_notif}"
		send_repeatable_notification(post.author_id, message)

	cache.delete_memoized(frontlist)

	return f"Post moved to {hole_to_in_notif} successfully!"
