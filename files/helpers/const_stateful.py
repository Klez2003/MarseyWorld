from os import path

from files.classes import Emoji, Hole
from files.helpers.config.const import *

SNAPPY_KONGS = []
MARSEYS_CONST = []
MARSEYS_CONST2 = []
MARSEY_MAPPINGS = {}
SNAPPY_MARSEYS = []
SNAPPY_QUOTES = []
SNAPPY_QUOTES_FISTMAS = []
SNAPPY_QUOTES_HOMOWEEN = []
STEALTH_HOLES = []
NSFW_EMOJIS = []

def const_initialize():
	global MARSEYS_CONST, MARSEYS_CONST2, MARSEY_MAPPINGS, SNAPPY_KONGS, SNAPPY_MARSEYS, SNAPPY_QUOTES, SNAPPY_QUOTES_FISTMAS, SNAPPY_QUOTES_HOMOWEEN, STEALTH_HOLES, NSFW_EMOJIS

	db = db_session()

	MARSEYS_CONST = [x[0] for x in db.query(Emoji.name).filter(Emoji.kind == "Marsey", Emoji.submitter_id == None, Emoji.name != 'chudsey', Emoji.nsfw == False)]
	MARSEYS_CONST2 = MARSEYS_CONST + ['chudsey','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9','exclamationpoint','period','questionmark']

	marseys = db.query(Emoji).filter(Emoji.kind=="Marsey", Emoji.submitter_id == None, Emoji.nsfw == False).all()
	for marsey in marseys:
		for tag in marsey.tags.split():
			if tag in MARSEY_MAPPINGS:
				MARSEY_MAPPINGS[tag].append(marsey.name)
			else:
				MARSEY_MAPPINGS[tag] = [marsey.name]

	SNAPPY_KONGS = db.query(Emoji.name).filter(Emoji.kind=="Donkey Kong", Emoji.submitter_id==None, Emoji.nsfw == False).all()
	SNAPPY_KONGS = [f':#{x[0]}:' for x in SNAPPY_KONGS]

	STEALTH_HOLES = [x[0] for x in db.query(Hole.name).filter_by(stealth=True)]

	NSFW_EMOJIS = [x[0] for x in db.query(Emoji.name).filter_by(nsfw=True)]

	db.commit()
	db.close()

	SNAPPY_MARSEYS = [f':#{x}:' for x in MARSEYS_CONST2]

	try:
		with open(f"snappy_{SITE_NAME}.txt", "r") as f:
			SNAPPY_QUOTES = f.read().strip().split("\n{[para]}\n")
		with open(f"snappy_fistmas_{SITE_NAME}.txt", "r") as f:
			SNAPPY_QUOTES_FISTMAS = f.read().strip().split("\n{[para]}\n")
		with open(f"snappy_homoween_{SITE_NAME}.txt", "r") as f:
			SNAPPY_QUOTES_HOMOWEEN = f.read().strip().split("\n{[para]}\n")
	except FileNotFoundError:
		pass
