from flask import g
from files.classes.award import AwardRelationship
from files.helpers.alerts import send_repeatable_notification
from files.helpers.useractions import badge_grant

from events.helpers.get import get_or_create_event_user

def award_thing_event(v, kind, author):
	event_author = get_or_create_event_user(author, g.db)
	event_v = get_or_create_event_user(v, g.db)

	if kind == "hw-bite":
		if event_author.hw_zombie < 0:
			event_author = event_v

		if event_author.hw_zombie == 0:
			event_author.hw_zombie = -1
			badge_grant(user=author, badge_id=181)

			award_object = AwardRelationship(user_id=author.id, kind='hw-bite')
			g.db.add(award_object)
			send_repeatable_notification(author.id,
				"As the zombie virus washes over your mind, you feel the urge "
				"to… BITE YUMMY BRAINS :marseyzombie:<br>"
				"You receive a free **Zombie Bite** award: pass it on!")

		elif event_author.hw_zombie > 0:
			event_author.hw_zombie -= 1
			if event_author.hw_zombie == 0:
				send_repeatable_notification(author.id, "You are no longer **VAXXMAXXED**! Time for another booster!")

				badge = author.has_badge(182)
				if badge: g.db.delete(badge)
	elif kind == "hw-vax":
		if event_author.hw_zombie < 0:
			event_author.hw_zombie = 0
			send_repeatable_notification(author.id, "You are no longer **INFECTED**! Praise Fauci!")

			badge = author.has_badge(181)
			if badge: g.db.delete(badge)
		elif event_author.hw_zombie >= 0:
			event_author.hw_zombie += 2
			event_author.hw_zombie = min(event_author.hw_zombie, 10)

			badge_grant(user=author, badge_id=182)
	elif kind == "jumpscare":
		event_author.jumpscare += 1

	g.db.add(event_author)
