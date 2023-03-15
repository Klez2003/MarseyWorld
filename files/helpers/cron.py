import datetime
import time
import os
from sys import stdout
from shutil import make_archive
from hashlib import md5
import secrets

import click
import requests

import files.helpers.awards as awards
import files.helpers.offsitementions as offsitementions
import files.helpers.stats as stats
import files.routes.static as route_static
from files.__main__ import cache
from files.classes import *
from files.helpers.alerts import send_repeatable_notification
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.lottery import check_if_end_lottery_task
from files.helpers.roulette import spin_roulette_wheel
from files.helpers.useractions import *
from files.cli import app, g

db.commit()
db.close()

@app.cli.command('cron', help='Run scheduled tasks.')
@click.option('--every-5m', is_flag=True, help='Call every 5 minutes.')
@click.option('--every-1h', is_flag=True, help='Call every 1 hour.')
@click.option('--every-1d', is_flag=True, help='Call every 1 day.')
@click.option('--every-1mo', is_flag=True, help='Call every 1 month.')
def cron(every_5m, every_1h, every_1d, every_1mo):
	db = db_session()
	g.v = None
	g.nonce = secrets.token_urlsafe(31)

	if every_5m:
		if FEATURES['GAMBLING']:
			check_if_end_lottery_task()
			spin_roulette_wheel()
		offsitementions.offsite_mentions_task(cache)

	if every_1h:
		awards.award_timers_bots_task()
		_generate_emojis_zip()

	if every_1d:
		stats.generate_charts_task(SITE)
		_sub_inactive_purge_task()
		site_stats = stats.stats(SITE_NAME)
		cache.set(f'{SITE}_stats', site_stats)

	db.commit()
	db.close()
	stdout.flush()

def _sub_inactive_purge_task():
	if not HOLE_INACTIVITY_DELETION:
		return False

	one_week_ago = time.time() - 604800
	active_holes = [x[0] for x in db.query(Submission.sub).distinct() \
		.filter(Submission.sub != None, Submission.created_utc > one_week_ago,
			Submission.private == False, Submission.is_banned == False,
			Submission.deleted_utc == 0).all()]
	active_holes.extend(['changelog','countryclub']) # holes immune from deletion

	dead_holes = db.query(Sub).filter(Sub.name.notin_(active_holes)).all()
	names = [x.name for x in dead_holes]

	admins = [x[0] for x in db.query(User.id).filter(User.admin_level >= PERMS['NOTIFICATIONS_HOLE_INACTIVITY_DELETION']).all()]

	mods = db.query(Mod).filter(Mod.sub.in_(names)).all()
	for x in mods:
		if x.user_id in admins: continue
		send_repeatable_notification(x.user_id, f":marseyrave: /h/{x.sub} has been deleted for inactivity after one week without new posts. All posts in it have been moved to the main feed :marseyrave:")

	for name in names:
		first_mod_id = db.query(Mod.user_id).filter_by(sub=name).order_by(Mod.created_utc).first()
		if first_mod_id:
			first_mod = get_account(first_mod_id[0])
			badge_grant(
				user=first_mod,
				badge_id=156,
				description=f'Let a hole they owned die (/h/{name})'
			)

		for admin in admins:
			send_repeatable_notification(admin, f":marseyrave: /h/{name} has been deleted for inactivity after one week without new posts. All posts in it have been moved to the main feed :marseyrave:")

	posts = db.query(Submission).filter(Submission.sub.in_(names)).all()
	for post in posts:
		if post.sub == 'programming':
			post.sub = 'slackernews'
		else:
			post.sub = None

		post.hole_pinned = None
		db.add(post)

	to_delete = mods \
		+ db.query(Exile).filter(Exile.sub.in_(names)).all() \
		+ db.query(SubBlock).filter(SubBlock.sub.in_(names)).all() \
		+ db.query(SubJoin).filter(SubJoin.sub.in_(names)).all() \
		+ db.query(SubSubscription).filter(SubSubscription.sub.in_(names)).all() \
		+ db.query(SubAction).filter(SubAction.sub.in_(names)).all()

	for x in to_delete:
		db.delete(x)
	db.flush()

	for x in dead_holes:
		db.delete(x)

	return True

def _generate_emojis_zip():
	make_archive('files/assets/emojis', 'zip', 'files/assets/images/emojis')

	m = md5()
	with open('files/assets/emojis.zip', "rb") as f:
		data = f.read()
	
	m.update(data)
	cache.set('emojis_hash', m.hexdigest())

	count = str(len(os.listdir('files/assets/images/emojis')))
	cache.set('emojis_count', count)

	size = str(int(os.stat('files/assets/emojis.zip').st_size/1024/1024)) + ' MB'
	cache.set('emojis_size', size)
