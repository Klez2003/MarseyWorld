from flask import g
from events import Event

def award_thing_event(v, kind, author):
	event_author = g.db.get(Event, author.id)
	event_v = g.db.get(Event, v.id)
	
	if not event_author:
		event_author = Event(id=author.id)
		g.db.add(event_author)

	if not event_v:
		event_v = Event(id=v.id)
		g.db.add(event_v)
	
	g.db.flush()
		
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
