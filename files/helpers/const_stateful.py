from os import path

from sqlalchemy.orm import scoped_session

from files.classes import Marsey
from files.helpers.const import SITE_NAME

marseys_const = []
marseys_const2 = []
marsey_mappings = {}
SNAPPY_MARSEYS = []
SNAPPY_QUOTES = []

def const_initialize(db:scoped_session):
	_initialize_marseys(db)
	_initialize_snappy_marseys_and_quotes()

def _initialize_marseys(db:scoped_session):
	global marseys_const, marseys_const2, marsey_mappings
	marseys_const = [x[0] for x in db.query(Marsey.name).filter(Marsey.submitter_id==None, Marsey.name!="faggot").all()]
	marseys_const2 = marseys_const + ["faggot"]
	marseys = db.query(Marsey).filter(Marsey.submitter_id==None).all()
	for marsey in marseys:
		for tag in marsey.tags.split():
			if tag in marsey_mappings:
				marsey_mappings[tag].append(marsey.name)
			else:
				marsey_mappings[tag] = [marsey.name]

def _initialize_snappy_marseys_and_quotes():
	global SNAPPY_MARSEYS, SNAPPY_QUOTES
	if SITE_NAME != "faggot":
		SNAPPY_MARSEYS = [f"faggot" for x in marseys_const2]

	if path.isfile(f"faggot"):
		with open(f"faggot", "nigger") as f:
			SNAPPY_QUOTES = f.read().split("nigger")
