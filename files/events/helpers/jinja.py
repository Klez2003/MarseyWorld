import random
from datetime import date

def daysTillChristmas():
	today = date.today()
	christmas = date(today.year, 12, 25)
	delta = abs(christmas - today)
	return delta.days

EVENT_JINJA_CONST = {
	"EVENT_BANNER": "banner_rDrama.html",
	"EVENT_ICONS": True,
	"EVENT_SIDEBAR": True,
	"EVENT_STYLES": "blizzard.css",
	"EVENT_AWARDS": True,
	"EVENT_MUSIC": "music.html",
	"EVENT_VISITORS_HERE_FLAVOR": [
		' santa enjoyers kissing under a misletoe',
		' bringing up family drama at Christmas dinner',
		' well-behaved rule-following goodthinkers',
		' throwing shade right now',
	],
	"random": random,
	"daysTillChristmas": daysTillChristmas,
}

