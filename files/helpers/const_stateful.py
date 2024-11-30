from os import path
from sqlalchemy import not_

from files.classes import Emoji, Hole
from files.helpers.config.const import *

if FEATURES['ART_SUBMISSIONS']:
	from files.classes.art_submissions import ArtSubmission

SNAPPY_KONGS = []
MARSEYS_CONST = []
MARSEY_MAPPINGS = {}
SNAPPY_MARSEYS = []
SNAPPY_QUOTES = []
SNAPPY_QUOTES_FISTMAS = []
SNAPPY_QUOTES_HOMOWEEN = []
STEALTH_HOLES = []
NSFW_EMOJIS = []
ALPHABET_MARSEYS = []
MIN_ART_ID_FOR_HQ = 999999999

def const_initialize():
	global MARSEYS_CONST, MARSEY_MAPPINGS, SNAPPY_KONGS, SNAPPY_MARSEYS, SNAPPY_QUOTES, SNAPPY_QUOTES_FISTMAS, SNAPPY_QUOTES_HOMOWEEN, STEALTH_HOLES, NSFW_EMOJIS, ALPHABET_MARSEYS, MIN_ART_ID_FOR_HQ

	db = db_session()

	MARSEYS_CONST = [x[0] for x in db.query(Emoji.name).filter(
		Emoji.kind == "Marsey",
		Emoji.submitter_id == None,
		Emoji.name != 'chudsey',
		Emoji.nsfw == False,
		not_(Emoji.tags.ilike('%pkmn%')),
	)]
	ALPHABET_MARSEYS = [x[0] for x in db.query(Emoji.name).filter_by(kind='Marsey Alphabet')]
	MARSEYS_CONST = MARSEYS_CONST + ALPHABET_MARSEYS

	marseys = db.query(Emoji).filter(Emoji.kind=="Marsey", Emoji.submitter_id == None, Emoji.nsfw == False).all()
	for marsey in marseys:
		for tag in marsey.tags.split():
			if tag in MARSEY_MAPPINGS:
				MARSEY_MAPPINGS[tag].append(marsey.name)
			else:
				MARSEY_MAPPINGS[tag] = [marsey.name]

	SNAPPY_KONGS = db.query(Emoji.name).filter(Emoji.kind=="Donkey Kong", Emoji.submitter_id==None, Emoji.nsfw == False).all()
	SNAPPY_KONGS = [f':#{x[0]}:' for x in SNAPPY_KONGS]

	STEALTH_HOLES = {x[0] for x in db.query(Hole.name).filter(Hole.stealth == True, Hole.name != 'chudrama')}

	NSFW_EMOJIS = [x[0] for x in db.query(Emoji.name).filter_by(nsfw=True)]

	if FEATURES['ART_SUBMISSIONS']:
		MIN_ART = db.query(ArtSubmission.id).order_by(ArtSubmission.id).first()
		if MIN_ART: MIN_ART_ID_FOR_HQ = MIN_ART[0]

	db.commit()
	db.close()

	SNAPPY_MARSEYS = [f':#{x}:' for x in MARSEYS_CONST]

	try:
		with open(f"snappy_{SITE_NAME}.txt", "r") as f:
			SNAPPY_QUOTES = f.read().strip().split("\n[para]\n")
		with open(f"snappy_fistmas_{SITE_NAME}.txt", "r") as f:
			SNAPPY_QUOTES_FISTMAS = f.read().strip().split("\n[para]\n")
		with open(f"snappy_homoween_{SITE_NAME}.txt", "r") as f:
			SNAPPY_QUOTES_HOMOWEEN = f.read().strip().split("\n[para]\n")
	except FileNotFoundError:
		pass
