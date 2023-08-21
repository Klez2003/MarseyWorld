from flask import g

from files.classes.badges import Badge
from files.helpers.alerts import send_repeatable_notification

def badge_grant(user, badge_id, notify=True, check_if_exists=True):
	g.db.flush()
	existing = g.db.query(Badge).filter_by(user_id=user.id, badge_id=badge_id).one_or_none()
	if existing: return

	badge = Badge(
		badge_id=int(badge_id),
		user_id=user.id,
	)

	g.db.add(badge)
	g.db.flush()

	if notify:
		send_repeatable_notification(user.id,
			"@AutoJanny has given you the following profile badge:\n\n" +
			f"{badge.path}\n\n**{badge.name}**\n\n{badge.badge.description}")
