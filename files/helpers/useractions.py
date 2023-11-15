from flask import g

from files.classes.badges import Badge
from files.helpers.alerts import send_repeatable_notification

def badge_grant(user, badge_id, description=None, url=None, notify=True):
	g.db.flush()
	existing = g.db.query(Badge).filter_by(user_id=user.id, badge_id=badge_id).one_or_none()
	if existing: return

	if description and len(description) > 256:
		abort(400, "Custom description is too long, max 256 characters!")

	if url and len(url) > 256:
		abort(400, "URL is too long, max 256 characters!")

	badge = Badge(
		badge_id=int(badge_id),
		user_id=user.id,
		description=description,
		url=url,
	)

	g.db.add(badge)
	g.db.flush()

	if notify:
		send_repeatable_notification(user.id,
			"@AutoJanny has given you the following profile badge:\n\n" +
			f"{badge.path}\n\n**{badge.name}**\n\n{badge.badge.description}").created_utc -= 1
