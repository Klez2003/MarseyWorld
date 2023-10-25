import json
import os

import gevent
import gevent_inotifyx as inotify

from files.helpers.config.const import *

_SETTINGS = {
	"under_attack": False,
	"login_required": False,
	"signups": True,
	"bots": True,
	"fart_mode": False,
	"read_only_mode": False,
	"offline_mode": False,
	"under_siege": False,
	"dm_media": True,
}

def get_setting(setting):
	if not setting or not isinstance(setting, str): raise TypeError()
	return _SETTINGS[setting]

def get_settings():
	return _SETTINGS

def toggle_setting(setting):
	val = not _SETTINGS[setting]
	_SETTINGS[setting] = val
	_save_settings()
	return val

def set_setting(setting, val):
	_SETTINGS[setting] = val
	_save_settings()

def reload_settings():
	global _SETTINGS
	if not os.path.isfile(SETTINGS_FILENAME):
		_save_settings()
	with open(SETTINGS_FILENAME, 'r') as f:
		x = f.read()
		if x:
			_SETTINGS = json.loads(x)

def _save_settings():
	with open(SETTINGS_FILENAME, "w") as f:
		json.dump(_SETTINGS, f)

def start_watching_settings():
	gevent.spawn(_settings_watcher, SETTINGS_FILENAME)

def _settings_watcher(filename):
	fd = inotify.init()
	try:
		inotify.add_watch(fd, filename, inotify.IN_CLOSE_WRITE)
		while True:
			for event in inotify.get_events(fd, 0):
				reload_settings()
				break
			gevent.sleep(0.5)
	finally:
		os.close(fd)
