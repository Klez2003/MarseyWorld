from os import path

from sqlalchemy.orm import scoped_session

from files.classes import Emoji
from files.helpers.config.const import *

SNAPPY_KONGS = []
marseys_const = []
marseys_const2 = []
marsey_mappings = {}
SNAPPY_MARSEYS = []
SNAPPY_QUOTES = []

def const_initialize(db:scoped_session):
	_initialize_marseys(db)
	_initialize_snappy_marseys_and_quotes()

def _initialize_marseys(db:scoped_session):
	global marseys_const, marseys_const2, marsey_mappings, SNAPPY_KONGS
	marseys_const = [x[0] for x in db.query(Emoji.name).filter(Emoji.kind=="Marsey", Emoji.submitter_id==None, Emoji.name!='chudsey').all()]
	marseys_const2 = marseys_const + ['chudsey','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','0','1','2','3','4','5','6','7','8','9','exclamationpoint','period','questionmark']
	marseys = db.query(Emoji).filter(Emoji.kind=="Marsey", Emoji.submitter_id==None).all()
	for marsey in marseys:
		for tag in marsey.tags.split():
			if tag in marsey_mappings:
				marsey_mappings[tag].append(marsey.name)
			else:
				marsey_mappings[tag] = [marsey.name]

	if IS_DKD():
		SNAPPY_KONGS = db.query(Emoji.name).filter(Emoji.kind=="Donkey Kong", Emoji.submitter_id==None).all()
		SNAPPY_KONGS = [f':#{x[0]}:' for x in SNAPPY_KONGS]

	db.commit()
	db.close()


def _initialize_snappy_marseys_and_quotes():
	global SNAPPY_MARSEYS, SNAPPY_QUOTES

	SNAPPY_MARSEYS = [f':#{x}:' for x in marseys_const2]

	if IS_FISTMAS():
		filename = f"snappy_fistmas_{SITE_NAME}.txt"
	else:
		filename = f"snappy_{SITE_NAME}.txt"

	try:
		with open(filename, "r", encoding="utf-8") as f:
			SNAPPY_QUOTES = f.read().split("\n{[para]}\n")
	except FileNotFoundError:
		pass
