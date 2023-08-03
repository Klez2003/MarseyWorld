import time
import os
from sys import stdout
from shutil import make_archive
from hashlib import md5
from collections import Counter
from sqlalchemy.orm import load_only, InstrumentedAttribute

import click
import requests
import traceback

import files.helpers.offsitementions as offsitementions
import files.helpers.stats as stats
import files.routes.static as route_static
from files.routes.front import frontlist
from files.__main__ import cache
from files.classes import *
from files.helpers.alerts import send_repeatable_notification
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.lottery import check_if_end_lottery_task
from files.helpers.roulette import spin_roulette_wheel
from files.helpers.useractions import *
from files.cli import app, db_session, g

CRON_CACHE_TIMEOUT = 172800

def cron_fn(every_5m, every_1d):
	with app.app_context():
		g.db = db_session()
		g.v = None

		try:
			if every_5m:
				if FEATURES['GAMBLING']:
					check_if_end_lottery_task()

					spin_roulette_wheel()
				#offsitementions.offsite_mentions_task(cache)
				_award_timers_task()
				_unpin_expired()

			if every_1d:
				stats.generate_charts_task(SITE)

				cache.set('stats', stats.stats(), timeout=CRON_CACHE_TIMEOUT)

				_generate_emojis_zip()

				if FEATURES['ASSET_SUBMISSIONS']:
					_generate_emojis_original_zip()

				_leaderboard_task()

				_sub_inactive_purge_task()
			g.db.commit()
		except:
			print(traceback.format_exc(), flush=True)
			g.db.rollback()

		g.db.close()
		del g.db
		stdout.flush()

@app.cli.command('cron', help='Run scheduled tasks.')
@click.option('--every-5m', is_flag=True, help='Call every 5 minutes.')
@click.option('--every-1d', is_flag=True, help='Call every 1 day.')
def cron(every_5m, every_1d):
	cron_fn(every_5m, every_1d)

def _sub_inactive_purge_task():
	if not HOLE_INACTIVITY_DELETION:
		return False

	one_week_ago = time.time() - 604800
	active_holes = [x[0] for x in g.db.query(Post.sub).distinct() \
		.filter(Post.sub != None, Post.created_utc > one_week_ago,
			Post.private == False, Post.is_banned == False,
			Post.deleted_utc == 0).all()]
	active_holes.extend(['changelog','countryclub','museumofrdrama','highrollerclub']) # holes immune from deletion

	dead_holes = g.db.query(Sub).filter(Sub.name.notin_(active_holes)).all()
	names = [x.name for x in dead_holes]

	admins = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS['NOTIFICATIONS_HOLE_INACTIVITY_DELETION']).all()]

	mods = g.db.query(Mod).filter(Mod.sub.in_(names)).all()
	for x in mods:
		if x.user_id in admins: continue
		send_repeatable_notification(x.user_id, f":marseyrave: /h/{x.sub} has been deleted for inactivity after one week without new posts. All posts in it have been moved to the main feed :marseyrave:")

	for name in names:
		first_mod_id = g.db.query(Mod.user_id).filter_by(sub=name).order_by(Mod.created_utc).first()
		if first_mod_id:
			first_mod = get_account(first_mod_id[0])
			badge_grant(
				user=first_mod,
				badge_id=156,
				description=f'Let a hole they owned die (/h/{name})'
			)

		for admin in admins:
			send_repeatable_notification(admin, f":marseyrave: /h/{name} has been deleted for inactivity after one week without new posts. All posts in it have been moved to the main feed :marseyrave:")

	posts = g.db.query(Post).filter(Post.sub.in_(names)).all()
	for post in posts:
		if post.sub == 'programming':
			post.sub = 'slackernews'
		else:
			post.sub = None

		post.hole_pinned = None
		g.db.add(post)

	to_delete = mods \
		+ g.db.query(Exile).filter(Exile.sub.in_(names)).all() \
		+ g.db.query(SubBlock).filter(SubBlock.sub.in_(names)).all() \
		+ g.db.query(SubJoin).filter(SubJoin.sub.in_(names)).all() \
		+ g.db.query(SubSubscription).filter(SubSubscription.sub.in_(names)).all() \
		+ g.db.query(SubAction).filter(SubAction.sub.in_(names)).all()

	for x in to_delete:
		g.db.delete(x)
	g.db.flush() #Necessary, following deletion errors out otherwise

	for x in dead_holes:
		g.db.delete(x)

	return True

def _generate_emojis_zip():
	make_archive('files/assets/emojis', 'zip', 'files/assets/images/emojis')

	m = md5()
	with open('files/assets/emojis.zip', "rb") as f:
		data = f.read()

	m.update(data)
	cache.set('emojis_hash', m.hexdigest(), timeout=CRON_CACHE_TIMEOUT)

	count = str(len(os.listdir('files/assets/images/emojis')))
	cache.set('emojis_count', count, timeout=CRON_CACHE_TIMEOUT)

	size = str(int(os.stat('files/assets/emojis.zip').st_size/1024/1024)) + ' MB'
	cache.set('emojis_size', size, timeout=CRON_CACHE_TIMEOUT)

def _generate_emojis_original_zip():
	make_archive('files/assets/emojis_original', 'zip', '/asset_submissions/emojis/original')

	m = md5()
	with open('files/assets/emojis_original.zip', "rb") as f:
		data = f.read()

	m.update(data)
	cache.set('emojis_original_hash', m.hexdigest(), timeout=CRON_CACHE_TIMEOUT)

	count = str(len(os.listdir('/asset_submissions/emojis/original')))
	cache.set('emojis_original_count', count, timeout=CRON_CACHE_TIMEOUT)

	size = str(int(os.stat('files/assets/emojis_original.zip').st_size/1024)) + ' GB'
	cache.set('emojis_original_size', size, timeout=CRON_CACHE_TIMEOUT)

def _leaderboard_task():
	votes1 = g.db.query(Vote.user_id, func.count(Vote.user_id)).filter(Vote.vote_type==1).group_by(Vote.user_id).order_by(func.count(Vote.user_id).desc()).all()
	votes2 = g.db.query(CommentVote.user_id, func.count(CommentVote.user_id)).filter(CommentVote.vote_type==1).group_by(CommentVote.user_id).order_by(func.count(CommentVote.user_id).desc()).all()
	votes3 = Counter(dict(votes1)) + Counter(dict(votes2))
	users14 = g.db.query(User).filter(User.id.in_(votes3.keys())).all()
	users13 = []
	for user in users14:
		users13.append((user.id, votes3[user.id]-user.post_count-user.comment_count))
	if not users13: users13 = [(None,None)]
	users13 = sorted(users13, key=lambda x: x[1], reverse=True)
	users13_1, users13_2 = zip(*users13[:25])

	cache.set("users13", list(users13), timeout=CRON_CACHE_TIMEOUT)
	cache.set("users13_1", list(users13_1), timeout=CRON_CACHE_TIMEOUT)
	cache.set("users13_2", list(users13_2), timeout=CRON_CACHE_TIMEOUT)

	votes1 = g.db.query(Post.author_id, func.count(Post.author_id)).join(Vote).filter(Vote.vote_type==-1).group_by(Post.author_id).order_by(func.count(Post.author_id).desc()).all()
	votes2 = g.db.query(Comment.author_id, func.count(Comment.author_id)).join(CommentVote).filter(CommentVote.vote_type==-1).group_by(Comment.author_id).order_by(func.count(Comment.author_id).desc()).all()
	votes3 = Counter(dict(votes1)) + Counter(dict(votes2))
	users8 = g.db.query(User.id).filter(User.id.in_(votes3.keys())).all()
	users9 = []
	for user in users8:
		users9.append((user.id, votes3[user.id]))
	if not users9: users9 = [(None,None)]
	users9 = sorted(users9, key=lambda x: x[1], reverse=True)
	users9_1, users9_2 = zip(*users9[:25])

	cache.set("users9", list(users9), timeout=CRON_CACHE_TIMEOUT)
	cache.set("users9_1", list(users9_1), timeout=CRON_CACHE_TIMEOUT)
	cache.set("users9_2", list(users9_2), timeout=CRON_CACHE_TIMEOUT)


def _process_timer(attr, badge_ids, text, extra_attrs={}):
	now = time.time()
	users = g.db.query(User).options(load_only(User.id)).filter(1 < attr, attr < now)
	uids = set([x.id for x in users])

	#set user attributes
	attr = str(attr).split('.')[1]
	for user in users:
		setattr(user, attr, 0)
		for k, val in extra_attrs.items():
			k = str(k).split('.')[1]
			if isinstance(val, InstrumentedAttribute):
				val = str(val).split('.')[1]
				val = getattr(user, val)
			setattr(user, k, val)

	#remove corresponding badges
	if badge_ids:
		g.db.query(Badge).options(load_only(Badge.badge_id)).filter(Badge.badge_id.in_(badge_ids), Badge.user_id.in_(uids)).delete()

	#notify users
	for uid in uids:
		send_repeatable_notification(uid, text)

	if attr == User.patron_utc:
		verifiedrich_memberships = g.db.query(GroupMembership).filter(
			GroupMembership.user_id.in_(uids),
			GroupMembership.group_name == 'verifiedrich'
		).all()

		for membership in verifiedrich_memberships:
			g.db.delete(membership)


def _award_timers_task():
	#only awards
	_process_timer(User.deflector, [], "The deflector award you received has expired!")
	_process_timer(User.progressivestack, [94], "The progressive stack award you received has expired!")
	_process_timer(User.bird, [95], "The bird site award you received has expired!")
	_process_timer(User.longpost, [97], "The pizzashill award you received has expired!")
	_process_timer(User.marseyawarded, [98], "The marsey award you received has expired!")
	_process_timer(User.rehab, [109], "The rehab award you received has expired!")
	_process_timer(User.owoify, [167], "The OwOify award you received has expired!")
	_process_timer(User.sharpen, [289], "The Sharpen award you received has expired!")
	_process_timer(User.bite, [168], "The bite award you received has expired! You're now back in your original house!", {
		User.house: User.old_house,
		User.old_house: '',
	})
	_process_timer(User.earlylife, [169], "The earlylife award you received has expired!")
	_process_timer(User.marsify, [170], "The marsify award you received has expired!")
	_process_timer(User.rainbow, [171], "The rainbow award you received has expired!")
	_process_timer(User.queen, [285], "The queen award you received has expired!")
	_process_timer(User.spider, [179], "The spider award you received has expired!")
	_process_timer(User.namechanged, [281], "The namelock award you received has expired. You're now back to your old username!", {
		User.username: User.prelock_username,
		User.prelock_username: None,
	})

	#both awards and janny powers
	_process_timer(User.unban_utc, [], "Your temporary ban has expired!", {
		User.is_banned: None,
		User.ban_reason: None,
	})
	_process_timer(User.patron_utc, [22,23,24,25,26,27,28], f"Your {patron} status has expired!", {
		User.patron: 0,
	})
	_process_timer(User.chud, [58], "Your temporary chud status has expired!", {
		User.chud_phrase: None,
		User.chudded_by: None,
	})
	_process_timer(User.flairchanged, [96], "Your temporary flair-lock has expired. You can now change your flair!")


def _unpin_expired():
	t = int(time.time())
	pins = []

	for cls in (Post, Comment):
		pins += g.db.query(cls).options(load_only(cls.id)).filter(cls.stickied_utc < t)

	for pin in pins:
		pin.stickied = None
		pin.stickied_utc = None
		g.db.add(pin)

	if pins:
		cache.delete_memoized(frontlist)
