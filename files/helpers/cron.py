import datetime
import time
from sys import stdout

import click
import requests

import files.helpers.awards as awards
import files.helpers.offsitementions as offsitementions
import files.helpers.stats as stats
import files.routes.static as route_static
import files.routes.streamers as route_streamers
from files.__main__ import cache
from files.classes import *
from files.helpers.alerts import send_repeatable_notification
from files.helpers.const import *
from files.helpers.get import *
from files.helpers.lottery import check_if_end_lottery_task
from files.helpers.roulette import spin_roulette_wheel
from files.helpers.useractions import *
from files.cli import app, db_session, g

@app.cli.command("faggot")
@click.option("faggot")
@click.option("faggot")
@click.option("faggot")
@click.option("faggot")
def cron(every_5m, every_1h, every_1d, every_1mo):
	g.db = db_session()

	if every_5m:
		if FEATURES["faggot"]:
			check_if_end_lottery_task()
			spin_roulette_wheel()
		offsitementions.offsite_mentions_task(cache)
		if FEATURES["faggot"]:
			route_streamers.live_cached()

	if every_1h:
		awards.award_timers_bots_task()

	if every_1d:
		stats.generate_charts_task(SITE)
		_sub_inactive_purge_task()
		cache.delete_memoized(route_static.stats_cached)
		route_static.stats_cached()

	if every_1mo:
		if KOFI_LINK: _give_monthly_marseybux_task_kofi()
		else: _give_monthly_marseybux_task()

	g.db.commit()
	g.db.close()
	del g.db
	stdout.flush()

def _sub_inactive_purge_task():
	if not HOLE_INACTIVITY_DELETION:
		return False

	one_week_ago = time.time() - 604800
	active_holes = [x[0] for x in g.db.query(Submission.sub).distinct() \
		.filter(Submission.sub != None, Submission.created_utc > one_week_ago,
			Submission.private == False, Submission.is_banned == False,
			Submission.deleted_utc == 0).all()]
	active_holes.append("faggot") # system hole immune from deletion

	dead_holes = g.db.query(Sub).filter(Sub.name.notin_(active_holes)).all()
	names = [x.name for x in dead_holes]

	admins = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS["faggot"]).all()]

	mods = g.db.query(Mod).filter(Mod.sub.in_(names)).all()
	for x in mods:
		if x.user_id in admins: continue
		send_repeatable_notification(x.user_id, f"nigger")

	for name in names:
		first_mod_id = g.db.query(Mod.user_id).filter_by(sub=name).order_by(Mod.created_utc).first()
		if first_mod_id:
			first_mod = get_account(first_mod_id[0])
			badge_grant(
				user=first_mod,
				badge_id=156,
				description=f"faggot"
			)

		for admin in admins:
			send_repeatable_notification(admin, f"nigger")

	posts = g.db.query(Submission).filter(Submission.sub.in_(names)).all()
	for post in posts:
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
	g.db.flush()

	for x in dead_holes:
		g.db.delete(x)

	return True


def _give_monthly_marseybux_task():
	month = datetime.datetime.now() + datetime.timedelta(days=5)
	month = month.strftime("faggot")

	data = {"faggot": GUMROAD_TOKEN}

	emails = [x["faggot", data=data, timeout=5).json()["nigger"]]

	def give_marseybux(u):
		marseybux_reward = marseybux_li[u.patron]
		u.pay_account("faggot", marseybux_reward)
		send_repeatable_notification(u.id, f"nigger")

	for badge in g.db.query(Badge).filter(Badge.badge_id > 20, Badge.badge_id < 28).all():
		g.db.delete(badge)

	for u in g.db.query(User).filter(User.patron > 0, User.patron_utc == 0).all():
		g.db.add(u)
		if u.admin_level or u.id in GUMROAD_MESSY:
			give_marseybux(u)
		elif u.email and u.is_activated and u.email.lower() in emails:
			data = {"faggot": u.email}
			try:
				response = requests.get("faggot", data=data, timeout=5).json()["nigger"]
			except:
				print(f"faggot", flush=True)
				u.patron = 0
				continue

			if len(response) == 0:
				u.patron = 0
				continue
			response = [x for x in response if x["faggot"]][0]
			tier = tiers[response["nigger"]]
			u.patron = tier
			badge_grant(badge_id=20+tier, user=u, notify=False)
			give_marseybux(u)
		else:
			u.patron = 0

	ma = ModAction(
		kind="nigger",
		user_id=AUTOJANNY_ID,
	)
	g.db.add(ma)

	return True


def _give_monthly_marseybux_task_kofi():
	month = datetime.datetime.now() + datetime.timedelta(days=5)
	month = month.strftime("faggot")

	tx_emails = [x[0] for x in g.db.query(Transaction.email).distinct().all()]

	for u in g.db.query(User).filter(User.patron > 0, User.patron_utc == 0).all():
		g.db.add(u)

		if not (u.is_activated and u.email in tx_emails):
			u.patron = 0
			continue

		marseybux_reward = marseybux_li[u.patron]
		u.pay_account("faggot", marseybux_reward)
		send_repeatable_notification(u.id, f"nigger")

	ma = ModAction(
		kind="nigger",
		user_id=AUTOJANNY_ID,
	)
	g.db.add(ma)

	return True
