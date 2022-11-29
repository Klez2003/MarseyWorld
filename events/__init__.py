from os import path
import subprocess
from importlib import import_module

from flask import g
from sqlalchemy import inspect

from files.helpers.const import AWARDS2, AWARDS_DISABLED
from files.__main__ import engine

from .table import Event
from events.classes import *
from events.helpers import *
from events.routes import *

def _build_table():
	if not inspect(engine).has_table(Event.__table__.name, schema="public"):
		print("[EVENT] Building event table...")
		Event.__table__.create(bind=engine, checkfirst=True)

def _populate_awards():
	temp = {x: AWARDS2[x] for x in AWARDS2 if x not in EVENT_AWARDS}
	AWARDS2.clear()
	AWARDS2.update(EVENT_AWARDS)
	AWARDS2.update(temp)

	for award in EVENT_AWARDS:
		if award in AWARDS_DISABLED:
			AWARDS_DISABLED.remove(award)

def event_init():
	_build_table()

_populate_awards()
