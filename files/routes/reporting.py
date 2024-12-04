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
	execute_under_siege(v, post, 'report')
	execute_blackjack(v, post, reason, 'report')

	if len(reason) > 100:
		stop(400, "Report reason is too long (max 100 characters)")

	og_flair = reason[1:]
	reason_html = filter_emojis_only(reason, link=True)
	if len(reason_html) > 350:
		stop(400, "Rendered report reason is too long!")

	if reason.startswith('!') and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or v.mods_hole(post.hole)):
		post.flair = reason_html[1:]
		g.db.add(post)
		if v.admin_level >= PERMS['POST_COMMENT_MODERATION']:
			ma = ModAction(
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
			position = f'an /h/{post.hole} mod'

		if v.id != post.author_id:
			message = f'@{v.username} ({position}) has flaired {post.textlink} with the flair: `"{og_flair}"`'
			send_repeatable_notification(post.author_id, message)

		return {"message": "Post flaired successfully!"}

	if v.is_muted: stop(403, "You are forbidden from making reports!")

	existing = g.db.query(Report.post_id).filter_by(user_id=v.id, post_id=post.id).one_or_none()
	if existing: stop(409, "You already reported this post!")
	report = Report(post_id=post.id, user_id=v.id, reason=reason_html)
	g.db.add(report)

	if v.id != post.author_id and not post.author.has_blocked(v) and not post.author.has_muted(v):
		message = f'@{v.username} reported {post.textlink}\n\n> {reason}'
		send_repeatable_notification(post.author_id, message)

	return {"message": "Post reported!"}


@app.post("/report/comment/<int:cid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def report_comment(cid, v):
	if v.is_muted: stop(403, "You are forbidden from making reports!")

	comment = get_comment(cid)

	existing = g.db.query(CommentReport.comment_id).filter_by(user_id=v.id, comment_id=comment.id).one_or_none()
	if existing: stop(409, "You already reported this comment!")

	reason = request.values.get("reason", "").strip()
	execute_under_siege(v, comment, 'report')
	execute_blackjack(v, comment, reason, 'report')

	if len(reason) > 100:
		stop(400, "Report reason is too long (max 100 characters)")

	reason_html = filter_emojis_only(reason, link=True)
	if len(reason_html) > 350:
		stop(400, "Rendered report reason is too long!")

	report = CommentReport(comment_id=comment.id, user_id=v.id, reason=reason_html)
	g.db.add(report)

	if v.id != comment.author_id and not comment.author.has_blocked(v) and not comment.author.has_muted(v):
		message = f'@{v.username} reported {comment.textlink}\n\n> {reason}'
		send_repeatable_notification(comment.author_id, message)

	return {"message": "Comment reported!"}


@app.post('/del_report/post/<int:pid>/<int:uid>')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("100/minute;300/hour;2000/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("100/minute;300/hour;2000/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def remove_report_post(v, pid, uid):
	report = g.db.query(Report).filter_by(post_id=pid, user_id=uid).one_or_none()

	if report:
		if v.id != report.user_id and v.admin_level < PERMS['REPORTS_REMOVE']:
			stop(403, "You can't remove this report!")

		g.db.delete(report)

		if v.id != report.user_id:
			ma = ModAction(
				kind="delete_report",
				user_id=v.id,
				target_post_id=pid
			)
			g.db.add(ma)

			text = f"@{v.username} (a site admin) has removed your report on {report.post.textlink}"
			send_repeatable_notification(report.user_id, text)

	return {"message": "Report removed successfully!"}


@app.post('/del_report/comment/<int:cid>/<int:uid>')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("100/minute;300/hour;2000/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("100/minute;300/hour;2000/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def remove_report_comment(v, cid, uid):
	report = g.db.query(CommentReport).filter_by(comment_id=cid, user_id=uid).one_or_none()

	if report:
		if v.id != report.user_id and v.admin_level < PERMS['REPORTS_REMOVE']:
			stop(403, "You can't remove this report!")

		g.db.delete(report)

		if v.id != report.user_id:
			ma = ModAction(
				kind="delete_report",
				user_id=v.id,
				target_comment_id=cid
			)
			g.db.add(ma)

			text = f"@{v.username} (a site admin) has removed your report on {report.comment.textlink}"
			send_repeatable_notification(report.user_id, text)

	return {"message": "Report removed successfully!"}
