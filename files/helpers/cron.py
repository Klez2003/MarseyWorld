import time
import os
import glob
from sys import stdout
from shutil import make_archive
from hashlib import md5
from collections import Counter
from sqlalchemy.orm import load_only, InstrumentedAttribute
from sqlalchemy.sql import text

import click
import requests
import ffmpeg

import files.helpers.offsitementions as offsitementions
import files.helpers.stats as stats
import files.routes.static as route_static
from files.routes.front import frontlist
from files.__main__ import cache
from files.classes import *
from files.helpers.alerts import send_repeatable_notification, notif_comment
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.lottery import check_if_end_lottery_task
from files.helpers.roulette import spin_roulette_wheel
from files.helpers.sanitize import filter_emojis_only, sanitize
from files.helpers.useractions import *
from files.cli import app, db_session, g

CRON_CACHE_TIMEOUT = 172800

def cron_fn(every_5m, every_1d, every_fri_12, every_fri_23, every_sat_03, every_sun_07, every_sun_19, every_sun_23, every_1mo):
	with app.app_context():
		g.db = db_session()
		g.v = None

		try:
			if every_5m:
				if FEATURES['GAMBLING']:
					check_if_end_lottery_task()
					g.db.commit()

					spin_roulette_wheel()
					g.db.commit()

				_award_timers_task()
				g.db.commit()

				_unpin_expired()
				g.db.commit()

				_grant_one_year_badges()
				g.db.commit()

				_grant_two_year_badges()
				g.db.commit()

				if not IS_LOCALHOST:
					offsitementions.offsite_mentions_task(cache)
					g.db.commit()

			if every_1d or (not cache.get('stats') and not IS_LOCALHOST):
				if IS_HOMOWEEN():
					g.db.execute(text(
						"INSERT INTO award_relationships (user_id, kind, created_utc) "
						f"SELECT id, 'bite', {int(time.time())} FROM users "
						"WHERE users.zombie < 0"))
					g.db.commit()

				_generate_emojis_zip()
				g.db.commit()

				if FEATURES['EMOJI_SUBMISSIONS']:
					_generate_emojis_original_zip()
					g.db.commit()

				_hole_inactive_purge_task()
				g.db.commit()

				stats.generate_charts_task(SITE)
				g.db.commit()

				cache.set('stats', stats.stats(), timeout=CRON_CACHE_TIMEOUT)
				g.db.commit()

				_leaderboard_task()
				g.db.commit()

			if every_fri_12:
				_create_post(f'Movie Night', f'''Our Movie Night today will show `{get_names()}`.\nThe movies will start at 12:00 AM UTC. [Here is a timezone converter for whoever needs it.](https://dateful.com/convert/utc?t=12am). You can also check this [countdown timer](https://www.tickcounter.com/countdown/4596164/movie-night) instead.\nThey will be shown [here](/chat).\nThere will be a 5-minute bathroom break at the 50:00 mark of each movie.\nRerun will be Sunday 8 PM UTC.''', 11)
				g.db.commit()

			if every_fri_23:
				_create_post(f'Movie Night in 60 minutes', 'It will be shown [here](/chat).\nThere will be a 5-minute bathroom break at the 50:00 mark of each movie.\nRerun will be Sunday 8 PM UTC.', 1)
				g.db.commit()

			if every_sun_07:
				_create_post(f'Movie Night Rerun', f'''Our Movie Night Rerun today will show `{get_names()}`.\nThe movies will start at 8 PM UTC. [Here is a timezone converter for whoever needs it.](https://dateful.com/convert/utc?t=8pm). You can also check this [countdown timer](https://www.tickcounter.com/countdown/4596177/movie-night-rerun) instead.\nThey will be shown [here](/chat).\nThere will be a 5-minute bathroom break at the 50:00 mark of each movie.''', 11)
				g.db.commit()

			if every_sun_19:
				_create_post(f'Movie Night Rerun in 60 minutes', 'It will be shown [here](/chat).\nThere will be a 5-minute bathroom break at the 50:00 mark of each movie.', 1)
				g.db.commit()

			if every_sat_03 or every_sun_23:
				_delete_all_posts()
				g.db.commit()

			if every_1mo:
				_give_marseybux_salary()
				g.db.commit()

		except:
			g.db.rollback()
			raise

		g.db.close()
		del g.db
		stdout.flush()

	if IS_LOCALHOST:
		print('Cron tasks Finished!', flush=True)

@app.cli.command('cron', help='Run scheduled tasks.')
@click.option('--every-5m', is_flag=True, help='Call every 5 minutes.')
@click.option('--every-1d', is_flag=True, help='Call every 1 day.')
@click.option('--every-fri-12', is_flag=True, help='Call every Friday.')
@click.option('--every-fri-23', is_flag=True, help='Call every Friday.')
@click.option('--every-sat-03', is_flag=True, help='Call every Saturday.')
@click.option('--every-sun-07', is_flag=True, help='Call every Sunday.')
@click.option('--every-sun-19', is_flag=True, help='Call every Sunday.')
@click.option('--every-sun-23', is_flag=True, help='Call every Sunday.')
@click.option('--every-1mo', is_flag=True, help='Call every 1 month.')
def cron(**kwargs):
	cron_fn(**kwargs)

def get_names():
	return ' and '.join([x[0] for x in g.db.query(Orgy.title).filter_by(type='file').order_by(Orgy.start_utc).limit(2)])

def _create_post(title, body, pin_hours):
	if not g.db.query(Orgy).filter_by(type='file').first():
		return

	_delete_all_posts()

	title += f': {get_names()}'

	title_html = filter_emojis_only(title)
	body_html = sanitize(body)

	stickied_utc = int(time.time()) + (3600 * pin_hours)

	p = Post(
		private=False,
		notify=True,
		author_id=AUTOJANNY_ID,
		nsfw=False,
		new=False,
		app_id=None,
		is_bot=False,
		url='/chat',
		body=body,
		body_html=body_html,
		embed=None,
		title=title,
		title_html=title_html,
		hole='countryclub',
		ghost=False,
		chudded=False,
		rainbowed=False,
		queened=False,
		sharpened=False,
		stickied_utc=stickied_utc,
		stickied="AutoJanny",
		distinguish_level=6,
	)
	g.db.add(p)

	if AEVANN_ID:
		g.db.flush()
		new_sub = Subscription(user_id=AEVANN_ID, post_id=p.id)
		g.db.add(new_sub)

	cache.delete_memoized(frontlist)

def _delete_all_posts():
	posts = g.db.query(Post).filter_by(author_id=AUTOJANNY_ID, deleted_utc=0).all()
	for p in posts:
		p.deleted_utc = int(time.time())
		p.is_pinned = False
		p.stickied = None
		p.stickied_utc = None
		g.db.add(p)

		cache.delete_memoized(frontlist)

		for sort in COMMENT_SORTS.keys():
			cache.delete(f'post_{p.id}_{sort}')

def _grant_one_year_badges():
	one_year_ago = int(time.time()) - 364 * 86400

	notif_text = f"@AutoJanny has given you the following profile badge:\n\n{SITE_FULL_IMAGES}/i/{SITE_NAME}/badges/134.webp\n\n**1 Year Old 🥰**\n\nThis user has wasted an ENTIRE YEAR of their life here! Happy birthday!"
	cid = notif_comment(notif_text)
	_notif_query = text(f"""insert into notifications
	select id, {cid}, false, extract(epoch from now())
	from users where created_utc < {one_year_ago} and id not in (select user_id from badges where badge_id=134);""")
	g.db.execute(_notif_query)

	_badge_query = text(f"""insert into badges
	select 134, id, null, null, extract(epoch from now())
	from users where created_utc < {one_year_ago} and id not in (select user_id from badges where badge_id=134);""")
	g.db.execute(_badge_query)

def _grant_two_year_badges():
	two_years_ago = int(time.time()) - 729 * 86400

	notif_text = f"@AutoJanny has given you the following profile badge:\n\n{SITE_FULL_IMAGES}/i/{SITE_NAME}/badges/237.webp\n\n**2 Years Old 🥰🥰**\n\nThis user has wasted TWO WHOLE BUTT YEARS of their life here! Happy birthday!"
	cid = notif_comment(notif_text)
	_notif_query = text(f"""insert into notifications
	select id, {cid}, false, extract(epoch from now())
	from users where created_utc < {two_years_ago} and id not in (select user_id from badges where badge_id=237);""")
	g.db.execute(_notif_query)

	_badge_query = text(f"""insert into badges
	select 237, id, null, null, extract(epoch from now())
	from users where created_utc < {two_years_ago} and id not in (select user_id from badges where badge_id=237);""")
	g.db.execute(_badge_query)

def _hole_inactive_purge_task():
	if not HOLE_INACTIVITY_DELETION:
		return False

	one_week_ago = time.time() - 604800
	active_holes = [x[0] for x in g.db.query(Post.hole).distinct() \
		.filter(Post.hole != None, Post.created_utc > one_week_ago,
			Post.private == False, Post.is_banned == False,
			Post.deleted_utc == 0)]
	active_holes.extend(['changelog','countryclub','museumofrdrama','highrollerclub','test']) # holes immune from deletion

	dead_holes = g.db.query(Hole).filter(Hole.name.notin_(active_holes)).all()
	names = [x.name for x in dead_holes]

	admins = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS['NOTIFICATIONS_HOLE_INACTIVITY_DELETION'])]

	mods = g.db.query(Mod).filter(Mod.hole.in_(names)).all()
	for x in mods:
		if x.user_id in admins: continue
		send_repeatable_notification(x.user_id, f":marseyrave: /h/{x.hole} has been deleted for inactivity after one week without new posts. All posts in it have been moved to the main feed :marseyrave:")

	for name in names:
		first_mod_id = g.db.query(Mod.user_id).filter_by(hole=name).order_by(Mod.created_utc).first()
		if first_mod_id:
			first_mod = get_account(first_mod_id[0])
			badge_grant(
				user=first_mod,
				badge_id=156,
				description=f'Let a hole they owned die (/h/{name})'
			)

		for admin in admins:
			send_repeatable_notification(admin, f":marseyrave: /h/{name} has been deleted for inactivity after one week without new posts. All posts in it have been moved to the main feed :marseyrave:")

	posts = g.db.query(Post).filter(Post.hole.in_(names)).all()
	for post in posts:
		if post.hole == 'programming':
			post.hole = 'slackernews'
		else:
			post.hole = None

		post.hole_pinned = None
		g.db.add(post)

	to_delete = mods \
		+ g.db.query(Exile).filter(Exile.hole.in_(names)).all() \
		+ g.db.query(HoleBlock).filter(HoleBlock.hole.in_(names)).all() \
		+ g.db.query(StealthHoleUnblock).filter(StealthHoleUnblock.hole.in_(names)).all() \
		+ g.db.query(HoleFollow).filter(HoleFollow.hole.in_(names)).all() \
		+ g.db.query(HoleAction).filter(HoleAction.hole.in_(names)).all()

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

def _generate_emojis_original_zip():
	make_archive('files/assets/emojis_original', 'zip', '/asset_submissions/emojis/original')

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
	uids = set(x.id for x in users)

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

	if attr == 'patron_utc':
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
	_process_timer(User.hieroglyphs, [98], "The hieroglyphs award you received has expired!")
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
	_process_timer(User.namechanged, [281], "The namelock/queen award you received has expired. You're now back to your old username!", {
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

def _give_marseybux_salary():
	for u in g.db.query(User).filter(User.admin_level > 0).all():
		marseybux_salary = u.admin_level * 10000
		u.pay_account('marseybux', marseybux_salary)
		send_repeatable_notification(u.id, f"You have received your monthly janny salary of {marseybux_salary} Marseybux!")
