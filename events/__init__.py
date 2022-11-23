from os import path
import subprocess
from importlib import import_module

from files.__main__ import app, db_session, engine
from flask import g
from sqlalchemy import inspect

from files.helpers.const import AWARDS2, AWARDS_DISABLED

from .table import Event
from .columns import *

from events.classes import *
from events.helpers import *
from events.routes import *

def link_assets():
	asset_dirs = { # We assume WD is always in root of repository
		"files/assets/css": "../../../events/assets/css",
		"files/assets/js": "../../../events/assets/js",
		"files/assets/fonts": "../../../events/assets/fonts",
		"files/assets/images": "../../../events/assets/images",
		"files/assets/media": "../../../events/assets/media",
		"files/templates": "../../events/templates",
	}

	print("[EVENT] Linking event assets...")

	for link_dir in asset_dirs:
		target = asset_dirs[link_dir]
		link = link_dir + "/event"

		try:
			if path.exists(link):
				subprocess.run(["rm", link])

			subprocess.run(["ln", "-s", target, link])
			print("[EVENT] Linked " + link + " -> " + target)
		except Exception as e:
			print(e)

def build_table():
	if not inspect(engine).has_table("event", schema="public"):
		print("[EVENT] Building event table...")

		with app.app_context():
			g.db = db_session()

			Event.__table__.create(bind=g.db.bind, checkfirst=True)
			g.db.commit()

def populate_awards():
	temp = {x: AWARDS2[x] for x in AWARDS2 if x not in EVENT_AWARDS}
	AWARDS2.clear()
	AWARDS2.update(EVENT_AWARDS)
	AWARDS2.update(temp)

	for award in EVENT_AWARDS:
		if award in AWARDS_DISABLED:
			AWARDS_DISABLED.remove(award)

def init_event():
	link_assets()
	build_table()
	populate_awards()
