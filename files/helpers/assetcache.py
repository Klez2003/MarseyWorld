import os
import zlib
from collections import defaultdict
from sys import argv

import gevent
import gevent_inotifyx as inotify

from files.helpers.config.const import *

ASSET_DIR = 'files/assets'
ASSET_URL = '/assets/'
ASSET_CACHE = defaultdict(lambda: None)

ASSET_SUBDIRS = [
		'/css', '/js',
		'/events/shared/js',
		'/events/fistmas/css', '/events/fistmas/js',
		'/events/homoween/css', '/events/homoween/js',
	]

new_dirs = []
for directory in ASSET_SUBDIRS:
	new_dirs += [x[0].split(ASSET_DIR)[1] for x in os.walk(f'{ASSET_DIR}{directory}')]
ASSET_SUBDIRS = new_dirs

def assetcache_build(asset_dir, subdirs):
	for subdir in subdirs:
		for root, dirs, files in os.walk(asset_dir + subdir):
			for fname in files:
				fpath = root + '/' + fname
				relpath = fpath[len(asset_dir) + 1:].replace('\\', '/')
				with open(fpath, 'rb') as f:
					fhash = zlib.crc32(f.read())
					ASSET_CACHE[relpath] = '%x' % fhash

def assetcache_hash(asset_path):
	return ASSET_CACHE[asset_path]

def assetcache_path(asset_path):
	cachehash = assetcache_hash(asset_path)

	url = ASSET_URL + asset_path
	if cachehash:
		url += '?x=' + cachehash

	return url

def assetcache_watch_directories(asset_dir, subdirs):
	fd = inotify.init()
	try:
		for sd in subdirs:
			inotify.add_watch(fd, asset_dir + sd, inotify.IN_CLOSE_WRITE)
		while True:
			for event in inotify.get_events(fd, 0):
				print("Rebuilding assetcache: " + event.name, flush=True)
				assetcache_build(asset_dir, subdirs)
				break
			gevent.sleep(0.5)
	finally:
		os.close(fd)

assetcache_build(ASSET_DIR, ASSET_SUBDIRS)

if "cron" not in argv:
	gevent.spawn(assetcache_watch_directories, ASSET_DIR, ASSET_SUBDIRS)
