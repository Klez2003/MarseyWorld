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
		' least homoerotic dramanauts stroking their candy canes',
		" dramanauts jingling each other's balls",
		" average Santa deniers getting reamed by Rudolph the Red-Nosed Reindeer",
		" naughty listers getting coal for fistmas",
		" plus-sized dramanauts eating Santa's cookies",
		" dramatards having their chimneys stuffed by Santa",
	],
	"random": random,
	"daysTillChristmas": daysTillChristmas,
}

