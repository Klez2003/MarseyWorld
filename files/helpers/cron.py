import time
import datetime
import os
import glob
from sys import stdout
from shutil import make_archive
from hashlib import md5
from collections import Counter
from sqlalchemy.orm import load_only, InstrumentedAttribute
from sqlalchemy.sql import text
from sqlalchemy import or_

import click
import requests
import humanize

from files.helpers.stats import *
from files.routes.front import frontlist
from files.__main__ import cache
from files.classes import *
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.lottery import check_if_end_lottery_task
from files.helpers.roulette import spin_roulette_wheel
from files.helpers.sanitize import filter_emojis_only, sanitize
from files.helpers.useractions import *
from files.helpers.offsite_mentions import *
from files.helpers.media import *

from files.cli import app, db_session, g

CRON_CACHE_TIMEOUT = 172800

engine = create_engine(os.environ.get("DATABASE_URL").strip(), connect_args={"options": "-c statement_timeout=40000 -c idle_in_transaction_session_timeout=40000"})
db_session = scoped_session(sessionmaker(bind=engine, autoflush=False))

def cron_fn(every_5m, every_1d, every_1mo, manual):
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

				if not IS_LOCALHOST:
					reddit_mentions_task()
					g.db.commit()

					lemmy_mentions_task()
					g.db.commit()

					fourchan_mentions_task()
					g.db.commit()

					soyjak_mentions_task()
					g.db.commit()

			if every_1d or (not cache.get('stats') and not IS_LOCALHOST):
				if IS_HOMOWEEN():
					g.db.execute(text(
						"INSERT INTO award_relationships (user_id, kind, created_utc) "
						f"SELECT id, 'zombiebite', {int(time.time())} FROM users "
						"WHERE users.zombie < 0"))
					g.db.commit()

				_set_top_poster_of_the_day_id()
				g.db.commit()

				_generate_emojis_zip()
				g.db.commit()

				if FEATURES['EMOJI_SUBMISSIONS']:
					_generate_emojis_original_zip()
					g.db.commit()

				_hole_inactive_purge_task()
				g.db.commit()

				chart(kind='daily')
				chart(kind='weekly')
				g.db.commit()

				cache.set('stats', stats(), timeout=CRON_CACHE_TIMEOUT)
				g.db.commit()

				_leaderboard_task()
				g.db.commit()

				if FEATURES['BLOCK_MUTE_EXILE_EXPIRY']:
					_expire_restrictions()
					g.db.commit()

				_expire_blacklists()
				g.db.commit()

				if FEATURES['ACCOUNT_DELETION']:
					_delete_accounts()
					g.db.commit()

				_grant_one_year_badges()
				g.db.commit()

				_grant_two_year_badges()
				g.db.commit()

				_grant_three_year_badges()
				g.db.commit()

			if every_1mo:
				_give_marseybux_salary()
				g.db.commit()

				_cleanup_videos()
				g.db.commit()

			if manual:
				_get_real_sizes()
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
@click.option('--every-1mo', is_flag=True, help='Call every 1 month.')
@click.option('--manual', is_flag=True, help='Call manually.')
def cron(**kwargs):
	cron_fn(**kwargs)

def _grant_one_year_badges():
	today = datetime.datetime.today()
	try:
		one_year_ago = datetime.datetime(today.year - 1, today.month, today.day + 1).timestamp()
	except ValueError:
		one_year_ago = datetime.datetime(today.year - 1, today.month + 1, 1).timestamp()

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
	today = datetime.datetime.today()
	try:
		two_years_ago = datetime.datetime(today.year - 2, today.month, today.day + 1).timestamp()
	except ValueError:
		two_years_ago = datetime.datetime(today.year - 2, today.month + 1, 1).timestamp()

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

def _grant_three_year_badges():
	today = datetime.datetime.today()
	try:
		three_years_ago = datetime.datetime(today.year - 3, today.month, today.day + 1).timestamp()
	except ValueError:
		three_years_ago = datetime.datetime(today.year - 3, today.month + 1, 1).timestamp()

	notif_text = f"@AutoJanny has given you the following profile badge:\n\n{SITE_FULL_IMAGES}/i/{SITE_NAME}/badges/341.webp\n\n**3 Years Old 🥰🥰🥰**\n\nThis user has wasted THREE WHOLE BUTT YEARS of their life here! Happy birthday!"
	cid = notif_comment(notif_text)
	_notif_query = text(f"""insert into notifications
	select id, {cid}, false, extract(epoch from now())
	from users where created_utc < {three_years_ago} and id not in (select user_id from badges where badge_id=341);""")
	g.db.execute(_notif_query)

	_badge_query = text(f"""insert into badges
	select 341, id, null, null, extract(epoch from now())
	from users where created_utc < {three_years_ago} and id not in (select user_id from badges where badge_id=341);""")
	g.db.execute(_badge_query)

def _hole_inactive_purge_task():
	if not HOLE_INACTIVITY_DEATH:
		return False

	one_week_ago = time.time() - 86400 * 7
	active_holes = [x[0] for x in g.db.query(Post.hole).distinct() \
		.filter(Post.hole != None, Post.created_utc > one_week_ago,
			Post.draft == False, Post.is_banned == False,
			Post.deleted_utc == 0)]
	active_holes.extend(['changelog','countryclub','museumofrdrama','highrollerclub','test','truth','marsey','kappa','vlogs']) # holes immune from death

	dead_holes = g.db.query(Hole).filter(Hole.dead_utc == None, Hole.name.notin_(active_holes)).all()
	names = [x.name for x in dead_holes]

	for name in names:
		first_mod_id = g.db.query(Mod.user_id).filter_by(hole=name).order_by(Mod.created_utc).first()
		if first_mod_id:
			first_mod = get_account(first_mod_id[0])
			badge_grant(
				user=first_mod,
				badge_id=156,
				description=f'Let a hole they owned die (/h/{name})'
			)

		text = f':!marseydead: /h/{name} has died after 7 days without new posts. You can resurrect it at a cost if you wish :marseynecromancer:'
		mod_ids = (x[0] for x in g.db.query(Mod.user_id).filter_by(hole=name))
		extra_criteria = or_(User.hole_creation_notifs == True, User.id.in_(mod_ids))
		alert_active_users(text, None, extra_criteria)

	for x in dead_holes:
		x.dead_utc = time.time()
		g.db.add(x)

	to_delete = g.db.query(Mod).filter(Mod.hole.in_(names)).all() + g.db.query(Exile).filter(Exile.hole.in_(names)).all()
	for x in to_delete:
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
	votes1 = g.db.query(Vote.user_id, func.count(Vote.user_id)).filter(Vote.vote_type == 1).group_by(Vote.user_id).order_by(func.count(Vote.user_id).desc()).all()
	votes2 = g.db.query(CommentVote.user_id, func.count(CommentVote.user_id)).filter(CommentVote.vote_type == 1).group_by(CommentVote.user_id).order_by(func.count(CommentVote.user_id).desc()).all()
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

	votes1 = g.db.query(Post.author_id, func.count(Post.author_id)).join(Vote).filter(Vote.vote_type == -1).group_by(Post.author_id).order_by(func.count(Post.author_id).desc()).all()
	votes2 = g.db.query(Comment.author_id, func.count(Comment.author_id)).join(CommentVote).filter(CommentVote.vote_type == -1).group_by(Comment.author_id).order_by(func.count(Comment.author_id).desc()).all()
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
	uids = {x.id for x in users}

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

	if SITE_NAME != 'WPD':
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
		User.sig: None,
		User.sig_html: None,
		User.extra_username: None,
		User.keyword_notifs: None,
		User.snappy_quotes: None,
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
		pins += g.db.query(cls).options(load_only(cls.id)).filter(cls.pinned_utc < t)

	for pin in pins:
		pin.pinned = None
		pin.pinned_utc = None
		g.db.add(pin)
		if isinstance(pin, Comment):
			pin.unpin_parents()	

	if pins:
		cache.delete_memoized(frontlist)

def _give_marseybux_salary():
	for u in g.db.query(User).filter(User.admin_level > 0).all():
		if SITE == 'rdrama.net' and u.admin_level == 2:
			continue
		marseybux_salary = u.admin_level * 10000
		if SITE_NAME == 'WPD':
			marseybux_salary *= 2
		u.pay_account('marseybux', marseybux_salary, "Janny salary")
		send_repeatable_notification(u.id, f"You have received your monthly janny salary of {commas(marseybux_salary)} Marseybux!")

def _expire_restrictions():
	cutoff = time.time() - 2592000

	blocks = g.db.query(UserBlock).filter(UserBlock.created_utc < cutoff)
	for block in blocks:
		send_repeatable_notification(block.user_id, f"Your block of @{block.target.username} has passed 30 days and expired!")
		send_repeatable_notification(block.target_id, f"@{block.user.username}'s block of you has passed 30 days and expired!")
		g.db.delete(block)

	mutes = g.db.query(UserMute).filter(UserMute.created_utc < cutoff)
	for mute in mutes:
		send_repeatable_notification(mute.user_id, f"Your mute of @{mute.target.username} has passed 30 days and expired!")
		send_repeatable_notification(mute.target_id, f"@{mute.user.username}'s mute of you has passed 30 days and expired!")
		g.db.delete(mute)

	exiles = g.db.query(Exile).filter(Exile.created_utc < cutoff)
	for exile in exiles:
		send_repeatable_notification(exile.user_id, f"Your exile from /h/{exile.hole} has passed 30 days and expired!")
		g.db.delete(exile)

def _expire_blacklists():
	cutoff = time.time() - 2592000

	blacklists = g.db.query(GroupBlacklist).filter(GroupBlacklist.created_utc < cutoff)
	for blacklist in blacklists:
		send_repeatable_notification(blacklist.user_id, f"Your blacklisting from !{blacklist.group_name} has passed 30 days and expired!")
		g.db.delete(blacklist)

def _delete_accounts():
	cutoff = time.time() - 2592000

	account_deletions = g.db.query(AccountDeletion).filter(AccountDeletion.created_utc < cutoff)
	for account_deletion in account_deletions:
		account_deletion.deleted_utc = time.time()
		g.db.add(account_deletion)
		account_deletion.user.username = f'deleted~{account_deletion.user.id}'
		account_deletion.user.passhash = ''
		g.db.add(account_deletion.user)

def _set_top_poster_of_the_day_id():
	t = int(time.time()) - 86400

	db = db_session()

	user = db.query(User, func.sum(Post.upvotes)).join(Post, Post.author_id == User.id).filter(
		Post.created_utc > t,
		Post.hole != 'chudrama',
		User.admin_level == 0,
	).group_by(User).order_by(func.sum(Post.upvotes).desc()).first()

	if not user: return

	user = user[0]

	date = time.strftime("%B %d, %Y", time.gmtime())
	send_notification(user.id, f":marseyjam: Congratulations! You're the Top Poster of the Day for {date}! :!marseyjam:")
	badge_grant(badge_id=327, user=user)

	cache.set("top_poster_of_the_day_id", user.id, timeout=86400)

def _cleanup_videos():
	subprocess.call("scripts/cleanup_videos.sh", timeout=3000)

	db = db_session()

	cutoff = time.time() - (2592000 * 6)




	unpublished_drafts = g.db.query(Post).filter(
		Post.draft == True,
		Post.created_utc < cutoff,
		Post.deleted_utc == 0,
	)
	for post in unpublished_drafts:
		post_marked = False
		for media_usage in post.media_usages:
			if not media_usage.removed_utc:
				post_marked = True
				media_usage.removed_utc = time.time()
				g.db.add(media_usage)
		
		if post_marked:
			print(f'marked videos for deletion in draft post: {post.id}', flush=True)

		for comment in post.comments:
			comment_marked = False
			for media_usage in comment.media_usages:
				if not media_usage.removed_utc:
					comment_marked = True
					media_usage.removed_utc = time.time()
					g.db.add(media_usage)

			if comment_marked:
				print(f'marked videos for deletion in draft comment: {comment.id}', flush=True)



	shadowbanned_media_usages_posts = db.query(MediaUsage).join(MediaUsage.post).join(Post.author).filter(
		MediaUsage.post_id != None,
		User.shadowbanned != None,
		MediaUsage.created_utc < cutoff,
		MediaUsage.removed_utc == None,
	).order_by(Post.id).all()

	shadowbanned_media_usages_comments = db.query(MediaUsage).join(MediaUsage.comment).join(Comment.author).filter(
		MediaUsage.comment_id != None,
		User.shadowbanned != None,
		MediaUsage.created_utc < cutoff,
		MediaUsage.removed_utc == None,
	).order_by(Comment.id).all()

	shadowbanned_media_usages = shadowbanned_media_usages_posts + shadowbanned_media_usages_comments

	for media_usage in shadowbanned_media_usages:
		print(f'shadowbanned: {media_usage.filename} - {media_usage.post_id} - {media_usage.comment_id}', flush=True)
		media_usage.removed_utc = media_usage.created_utc
		g.db.add(media_usage)




	clean = [x[0] for x in db.query(MediaUsage.filename).filter(
		or_(MediaUsage.deleted_utc == None, MediaUsage.deleted_utc > cutoff),
		or_(MediaUsage.removed_utc == None, MediaUsage.removed_utc > cutoff),
	)]


	to_delete = db.query(Media).outerjoin(Media.usages).filter(
		Media.filename.notin_(clean),
		Media.purged_utc == None,
		Media.user_id.notin_({218,380983}),
		or_(
			MediaUsage.deleted_utc < cutoff,
			MediaUsage.removed_utc < cutoff,
			and_(
				Media.referrer == f'{SITE_FULL}/chat/1',
				Media.created_utc < cutoff,
			),
		),
	).order_by(Media.size.desc())

	total_saved = 0
	for media in to_delete:
		total_saved += media.size
		print('deleted: ', media.filename, humanize.naturalsize(media.size, binary=True), flush=True)
		media.purged_utc = time.time()
		g.db.add(media)
		if os.path.isfile(media.filename):
			os.remove(media.filename)
		if media.posterurl and os.path.isfile(media.posterurl):
			os.remove(media.posterurl)
		if SITE == 'watchpeopledie.tv' and media.kind == 'video':
			gevent.spawn(rclone_delete, f'no:{media.filename}')

	total_saved = humanize.naturalsize(total_saved, binary=True)
	print(f"Total saved: {total_saved}")

	subprocess.call("scripts/run_fclones.sh", timeout=3000)
	print(f"fclones run succesfully!")


def _get_real_sizes():
	size_1 = g.db.query(Media).filter_by(size=1)
	for media in size_1:
		try:
			media.size = os.stat(media.filename).st_size
			g.db.add(media)
		except FileNotFoundError:
			for media_usage in media.usages:
				g.db.delete(media_usage)
			g.db.delete(media)