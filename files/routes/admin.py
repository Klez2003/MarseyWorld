import time
from math import floor
import os
import random

from sqlalchemy.orm import load_only
from sqlalchemy.sql import func

from files.__main__ import app, cache, limiter
from files.classes import *
from files.classes.orgy import *
from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.cloudflare import *
from files.helpers.config.const import *
from files.helpers.slurs_and_profanities import censor_slurs_profanities
from files.helpers.get import *
from files.helpers.media import *
from files.helpers.sanitize import *
from files.helpers.security import *
from files.helpers.settings import *
from files.helpers.useractions import *
from files.routes.routehelpers import check_for_alts
from files.routes.wrappers import *
from files.routes.routehelpers import get_alt_graph, get_alt_graph_ids
from files.routes.users import claim_rewards_all_users
from files.routes.votes import get_coin_mul

from .front import frontlist, comment_idlist

@app.get('/admin/loggedin')
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['VIEW_ACTIVE_USERS'])
def loggedin_list(v):
	ids = [x for x,val in cache.get('loggedin').items() if time.time()-val < LOGGEDIN_ACTIVE_TIME]
	users = g.db.query(User).filter(User.id.in_(ids)).order_by(User.admin_level.desc(), User.truescore.desc()).all()
	return render_template("admin/loggedin.html", v=v, users=users)

@app.get('/admin/loggedout')
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['VIEW_ACTIVE_USERS'])
def loggedout_list(v):
	users = sorted([val[1] for x,val in cache.get('loggedout').items() if time.time()-val[0] < LOGGEDIN_ACTIVE_TIME])
	return render_template("admin/loggedout.html", v=v, users=users)

@app.get('/admin/dm_media')
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['ENABLE_DM_MEDIA'])
def dm_media(v):
	with open(f"{LOG_DIRECTORY}/dm_media.log", "r") as f:
		items=f.read().split("\n")[:-1]

	total = len(items)
	items = [x.split(", ") for x in items]
	items.reverse()

	try: page = int(request.values.get('page', 1))
	except: page = 1

	firstrange = PAGE_SIZE * (page - 1)
	secondrange = firstrange + PAGE_SIZE
	items = items[firstrange:secondrange]

	return render_template("admin/dm_media.html", v=v, items=items, total=total, page=page)

@app.get('/admin/edit_rules')
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['EDIT_RULES'])
def edit_rules_get(v):
	try:
		with open(f'files/templates/rules_{SITE_NAME}.html', 'r') as f:
			rules = f.read()
	except:
		rules = None
	return render_template('admin/edit_rules.html', v=v, rules=rules)


@app.post('/admin/edit_rules')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['EDIT_RULES'])
def edit_rules_post(v):
	rules = request.values.get('rules', '').strip()
	rules = sanitize(rules, blackjack="rules")

	with open(f'files/templates/rules_{SITE_NAME}.html', 'w+') as f:
		f.write(rules)

	ma = ModAction(
		kind="edit_rules",
		user_id=v.id,
	)
	g.db.add(ma)
	return {"message": "Rules edited successfully!"}

@app.post("/@<username>/make_admin")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['ADMIN_ADD'])
def make_admin(v, username):
	user = get_user(username)

	user.admin_level = 1
	g.db.add(user)

	ma = ModAction(
		kind="make_admin",
		user_id=v.id,
		target_user_id=user.id
	)
	g.db.add(ma)

	send_repeatable_notification(user.id, f"@{v.username} (a site admin) added you as an admin!")

	return {"message": f"@{user.username} has been made admin!"}


@app.post("/@<username>/remove_admin")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['ADMIN_REMOVE'])
def remove_admin(v, username):
	if SITE == 'devrama.net':
		stop(403, "You can't remove admins on devrama!")

	user = get_user(username)

	if user.admin_level > v.admin_level:
		stop(403, "You can't remove an admin with higher level than you.")

	if user.admin_level:
		user.admin_level = 0
		g.db.add(user)

		ma = ModAction(
			kind="remove_admin",
			user_id=v.id,
			target_user_id=user.id
		)
		g.db.add(ma)

		send_repeatable_notification(user.id, f"@{v.username} (a site admin) removed you as an admin!")

	return {"message": f"@{user.username} has been removed as admin!"}

@app.post("/distribute/<kind>/<int:option_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['POST_BETS_DISTRIBUTE'])
def distribute(v, kind, option_id):
	if kind == 'post': cls = PostOption
	else: cls = CommentOption

	option = g.db.get(cls, option_id)

	if option.exclusive != 2:
		stop(400, "This is not a bet.")

	option.exclusive = 3
	g.db.add(option)

	parent = option.parent

	pool = 0
	for o in parent.options:
		if o.exclusive >= 2: pool += o.upvotes
	pool *= POLL_BET_COINS

	votes = option.votes

	text = f"You lost the {POLL_BET_COINS} coins you bet on {parent.textlink} :marseylaugh:"
	cid = notif_comment(text)
	losing_voters = []
	for o in parent.options:
		if o.exclusive == 2:
			losing_voters.extend([x.user_id for x in o.votes])
	for uid in losing_voters:
		add_notif(cid, uid, text, pushnotif_url=parent.permalink)

	if isinstance(parent, Post):
		ma = ModAction(
			kind="distribute",
			user_id=v.id,
			target_post_id=parent.id
		)
	else:
		ma = ModAction(
			kind="distribute",
			user_id=v.id,
			target_comment_id=parent.id
		)

	g.db.add(ma)

	if not votes:
		return {"message": "Nobody won lmao"}

	coinsperperson = int(pool / len(votes))

	text = f"You won {commas(coinsperperson)} coins betting on {parent.textlink} :marseyparty:"
	cid = notif_comment(text)
	for vote in votes:
		u = vote.user
		u.pay_account('coins', coinsperperson, f"Bet winnings on {parent.textlink}")
		add_notif(cid, u.id, text, pushnotif_url=parent.permalink)

	return {"message": f"Each winner has received {coinsperperson} coins!"}

@app.post("/@<username>/revert_actions")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['ADMIN_ACTIONS_REVERT'])
def revert_actions(v, username):
	revertee = get_user(username)

	if revertee.admin_level > v.admin_level:
		stop(403, "You can't revert the actions of an admin with higher level that you.")

	ma = ModAction(
		kind="revert",
		user_id=v.id,
		target_user_id=revertee.id
	)
	g.db.add(ma)

	cutoff = int(time.time()) - 86400

	posts = [x[0] for x in g.db.query(ModAction.target_post_id).filter(ModAction.user_id == revertee.id, ModAction.created_utc > cutoff, ModAction.kind == 'remove_post')]
	posts = g.db.query(Post).filter(Post.id.in_(posts)).all()

	comments = [x[0] for x in g.db.query(ModAction.target_comment_id).filter(ModAction.user_id == revertee.id, ModAction.created_utc > cutoff, ModAction.kind == 'remove_comment')]
	comments = g.db.query(Comment).filter(Comment.id.in_(comments)).all()

	for item in posts + comments:
		item.is_banned = False

		for media_usage in item.media_usages:
			media_usage.removed_utc = None
			g.db.add(media_usage)

		item.ban_reason = None
		item.is_approved = v.id
		g.db.add(item)

	users = (x[0] for x in g.db.query(ModAction.target_user_id).filter(ModAction.user_id == revertee.id, ModAction.created_utc > cutoff, ModAction.kind.in_(('shadowban', 'ban_user'))))
	users = g.db.query(User).filter(User.id.in_(users)).all()

	for user in users:
		user.shadowbanned = None
		user.unban_utc = None
		user.ban_reason = None
		user.shadowban_reason = None
		if user.is_banned:
			user.is_banned = None
			send_repeatable_notification(user.id, f"@{v.username} (a site admin) has unbanned you!")
		g.db.add(user)

		for u in get_alt_graph(user.id, unban=True):
			u.shadowbanned = None
			u.unban_utc = None
			u.ban_reason = None
			u.shadowban_reason = None
			if u.is_banned:
				u.is_banned = None
				one_month_ago = time.time() - 2592000
				if u.last_active > one_month_ago:
					send_repeatable_notification(u.id, f"@{v.username} (a site admin) has unbanned you!")
			g.db.add(u)

	return {"message": f"@{revertee.username}'s admin actions have been reverted!"}

@app.get("/admin/shadowbanned")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['USER_SHADOWBAN'])
def shadowbanned(v):
	sort = request.values.get("sort")

	page = get_page()

	users = g.db.query(User).filter(User.shadowbanned != None)

	total = users.count()

	if sort == "name":
		key = func.lower(User.username)
	elif sort == "truescore":
		key = User.truescore.desc()
	elif sort == "shadowban_reason":
		users1 = users.filter(User.shadowban_reason.like('Under Siege%')).all()
		users2 = users.filter(not_(User.shadowban_reason.like('Under Siege%'))).order_by(func.lower(User.shadowban_reason)).all()
		users = users1 + users2
		users = users[PAGE_SIZE*(page-1):]
		users = users[:PAGE_SIZE]
	elif sort == "shadowbanned_by":
		key = User.shadowbanned
	else:
		sort = "last_active"
		key = User.last_active.desc()

	if not isinstance(users, list):
		users = users.order_by(key).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE)

	return render_template("admin/shadowbanned.html", v=v, users=users, sort=sort, total=total, page=page)


@app.get("/admin/image_posts")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def image_posts_listing(v):

	try: page = int(request.values.get('page', 1))
	except: page = 1

	posts = g.db.query(Post).options(
			load_only(Post.id, Post.url)
		).order_by(Post.id.desc())

	posts = [x.id for x in posts if x.is_image]

	total = len(posts)

	firstrange = PAGE_SIZE * (page - 1)
	secondrange = firstrange + PAGE_SIZE
	posts = posts[firstrange:secondrange]

	posts = get_posts(posts, v=v)

	return render_template("admin/image_posts.html", v=v, listing=posts, total=total, page=page, sort="new")


@app.get("/admin/reported/posts")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def reported_posts(v):
	page = get_page()

	listing = g.db.query(Post).distinct(Post.id).options(load_only(Post.id)).filter_by(
				is_approved=None,
				is_banned=False,
			).join(Post.reports).join(User, User.id == Report.user_id).filter(User.shadowbanned == None, User.is_muted == False, User.id != SNAPPY_ID)

	total = listing.count()

	listing = listing.order_by(Post.id.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE)
	listing = [p.id for p in listing]
	listing = get_posts(listing, v=v)

	return render_template("admin/reported_posts.html",
						total=total, listing=listing, page=page, v=v)


@app.get("/admin/reported/comments")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def reported_comments(v):
	page = get_page()

	listing = g.db.query(Comment).distinct(Comment.id).options(load_only(Comment.id)).filter_by(
				is_approved=None,
				is_banned=False,
			).join(Comment.reports).join(User, User.id == CommentReport.user_id).filter(User.shadowbanned == None, User.is_muted == False)

	total = listing.count()

	listing = listing.order_by(Comment.id.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE)
	listing = [c.id for c in listing]
	listing = get_comments(listing, v=v)

	return render_template("admin/reported_comments.html",
						total=total,
						listing=listing,
						page=page,
						v=v,
						standalone=True)

@app.get("/admin")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['ADMIN_HOME_VISIBLE'])
def admin_home(v):
	if CLOUDFLARE_AVAILABLE:
		try: under_attack = (requests.get(f"{CLOUDFLARE_API_URL}/zones/{CF_ZONE}/settings/security_level", headers=CF_HEADERS, timeout=CLOUDFLARE_REQUEST_TIMEOUT_SECS).json()['result']['value'] == "under_attack")
		except: return render_template("admin/admin_home.html", v=v)
		set_setting('under_attack', under_attack)
	return render_template("admin/admin_home.html", v=v)

@app.post("/admin/site_settings/<setting>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['SITE_SETTINGS'])
def change_settings(v, setting):
	if setting not in get_settings().keys():
		stop(404, f"Setting '{setting}' not found")

	if setting == "offline_mode" and v.admin_level < PERMS["SITE_OFFLINE_MODE"]:
		stop(403, "You can't change this setting!")

	val = toggle_setting(setting)
	if val: word = 'enable'
	else: word = 'disable'

	if setting == "login_required" and word == "enable" and SITE == 'watchpeopledie.tv' and v.id != AEVANN_ID:
		stop(403, "You can't enable this setting!")

	if setting == "under_attack":
		new_security_level = 'under_attack' if val else 'high'
		if not set_security_level(new_security_level):
			stop(400, f'Failed to {word} under attack mode')

	ma = ModAction(
		kind=f"{word}_{setting}",
		user_id=v.id,
	)
	g.db.add(ma)

	return {'message': f"{setting.replace('_', ' ').title()} {word}d successfully!"}

@app.post("/admin/clear_cloudflare_cache")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['SITE_CACHE_PURGE_CDN'])
def clear_cloudflare_cache(v):
	if not clear_entire_cache():
		stop(400, 'Failed to clear cloudflare cache!')
	ma = ModAction(
		kind="clear_cloudflare_cache",
		user_id=v.id
	)
	g.db.add(ma)
	return {"message": "Cloudflare cache cleared!"}

@app.post("/admin/claim_rewards_all_users")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['CLAIM_REWARDS_ALL_USERS'])
def admin_claim_rewards_all_users(v):
	claim_rewards_all_users()
	return {"message": "User rewards claimed!"}

def admin_badges_grantable_list(v):
	query = g.db.query(BadgeDef)

	if BADGE_BLACKLIST and v.admin_level < PERMS['IGNORE_BADGE_BLACKLIST']:
		query = query.filter(BadgeDef.id.notin_(BADGE_BLACKLIST))

	badge_types = query.order_by(BadgeDef.id).all()
	return badge_types

@app.get("/admin/badge_grant")
@app.get("/admin/badge_remove")
@feature_required('BADGES')
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['USER_BADGES'])
def badge_grant_get(v):
	grant = request.path.endswith("grant")
	badge_types = admin_badges_grantable_list(v)

	return render_template("admin/badge_admin.html", v=v,
		badge_types=badge_types, grant=grant)

@app.post("/admin/badge_grant")
@feature_required('BADGES')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['USER_BADGES'])
def badge_grant_post(v):
	badges = admin_badges_grantable_list(v)

	usernames = request.values.get("usernames", "").strip()
	if not usernames:
		stop(400, "You must enter usernames!")

	for username in usernames.split():
		user = get_user(username)

		try: badge_id = int(request.values.get("badge_id"))
		except: stop(400, "Invalid badge id.")

		if badge_id not in [b.id for b in badges]:
			stop(403, "You can't grant this badge!")

		description = request.values.get("description")
		url = request.values.get("url", "").strip()

		if badge_id in {63,74,149,178,180,240,241,242,248,286,291,293,335} and not url:
			stop(400, "This badge requires a url!")

		if url:
			if '\\' in url: stop(400, "Nice try nigger.")
		else:
			url = None

		existing = user.has_badge(badge_id)
		if existing:
			if url or description:
				existing.url = url
				existing.description = description
				g.db.add(existing)
			continue

		new_badge = Badge(
			badge_id=badge_id,
			user_id=user.id,
			url=url,
			description=description
			)

		g.db.add(new_badge)
		g.db.flush()

		if v.id != user.id:
			text = f"@{v.username} (a site admin) has given you the following profile badge:\n\n{new_badge.path}\n\n**{new_badge.name}**\n\n{new_badge.badge.description}"
			if new_badge.description:
				text += f'\n\n> {new_badge.description}'
			if new_badge.url:
				text += f'\n\n> {new_badge.url}'
			send_repeatable_notification(user.id, text)

		note = new_badge.name
		if new_badge.description:
			note += f' - {new_badge.description}'
		if new_badge.url:
			note += f' - {new_badge.url}'

		ma = ModAction(
			kind="badge_grant",
			user_id=v.id,
			target_user_id=user.id,
			_note=note,
		)
		g.db.add(ma)

	return {"message": "Badge granted to users successfully!"}

@app.post("/admin/badge_remove")
@feature_required('BADGES')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['USER_BADGES'])
def badge_remove_post(v):
	badges = admin_badges_grantable_list(v)

	usernames = request.values.get("usernames", "").strip()
	if not usernames:
		stop(400, "You must enter usernames!")

	for username in usernames.split():
		user = get_user(username)

		try: badge_id = int(request.values.get("badge_id"))
		except: stop(400, "Invalid badge id.")

		if badge_id not in [b.id for b in badges]:
			stop(403, "You're not allowed to remove this badge.")

		badge = user.has_badge(badge_id)
		if not badge: continue

		if v.id != user.id:
			text = f"@{v.username} (a site admin) has removed the following profile badge from you:\n\n{badge.path}\n\n**{badge.name}**\n\n{badge.badge.description}"
			send_repeatable_notification(user.id, text)

		ma = ModAction(
			kind="badge_remove",
			user_id=v.id,
			target_user_id=user.id,
			_note=badge.name
		)
		g.db.add(ma)
		g.db.delete(badge)

	return {"message": "Badge removed from users successfully!"}


@app.get("/admin/alt_votes")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['VIEW_ALT_VOTES'])
def alt_votes_get(v):
	u1 = request.values.get("u1")
	u2 = request.values.get("u2")

	if not u1 or not u2:
		return render_template("admin/alt_votes.html", v=v)

	u1 = get_user(u1)
	u2 = get_user(u2)

	u1_post_ups = g.db.query(
		Vote.post_id).filter_by(
		user_id=u1.id,
		vote_type=1).all()
	u1_post_downs = g.db.query(
		Vote.post_id).filter_by(
		user_id=u1.id,
		vote_type=-1).all()
	u1_comment_ups = g.db.query(
		CommentVote.comment_id).filter_by(
		user_id=u1.id,
		vote_type=1).all()
	u1_comment_downs = g.db.query(
		CommentVote.comment_id).filter_by(
		user_id=u1.id,
		vote_type=-1).all()
	u2_post_ups = g.db.query(
		Vote.post_id).filter_by(
		user_id=u2.id,
		vote_type=1).all()
	u2_post_downs = g.db.query(
		Vote.post_id).filter_by(
		user_id=u2.id,
		vote_type=-1).all()
	u2_comment_ups = g.db.query(
		CommentVote.comment_id).filter_by(
		user_id=u2.id,
		vote_type=1).all()
	u2_comment_downs = g.db.query(
		CommentVote.comment_id).filter_by(
		user_id=u2.id,
		vote_type=-1).all()

	data = {}
	data['u1_only_post_ups'] = len(
		[x for x in u1_post_ups if x not in u2_post_ups])
	data['u2_only_post_ups'] = len(
		[x for x in u2_post_ups if x not in u1_post_ups])
	data['both_post_ups'] = len(list(set(u1_post_ups) & set(u2_post_ups)))

	data['u1_only_post_downs'] = len(
		[x for x in u1_post_downs if x not in u2_post_downs])
	data['u2_only_post_downs'] = len(
		[x for x in u2_post_downs if x not in u1_post_downs])
	data['both_post_downs'] = len(
		list(set(u1_post_downs) & set(u2_post_downs)))

	data['u1_only_comment_ups'] = len(
		[x for x in u1_comment_ups if x not in u2_comment_ups])
	data['u2_only_comment_ups'] = len(
		[x for x in u2_comment_ups if x not in u1_comment_ups])
	data['both_comment_ups'] = len(
		list(set(u1_comment_ups) & set(u2_comment_ups)))

	data['u1_only_comment_downs'] = len(
		[x for x in u1_comment_downs if x not in u2_comment_downs])
	data['u2_only_comment_downs'] = len(
		[x for x in u2_comment_downs if x not in u1_comment_downs])
	data['both_comment_downs'] = len(
		list(set(u1_comment_downs) & set(u2_comment_downs)))

	data['u1_post_ups_unique'] = 100 * \
		data['u1_only_post_ups'] // len(u1_post_ups) if u1_post_ups else 0
	data['u2_post_ups_unique'] = 100 * \
		data['u2_only_post_ups'] // len(u2_post_ups) if u2_post_ups else 0
	data['u1_post_downs_unique'] = 100 * \
		data['u1_only_post_downs'] // len(
			u1_post_downs) if u1_post_downs else 0
	data['u2_post_downs_unique'] = 100 * \
		data['u2_only_post_downs'] // len(
			u2_post_downs) if u2_post_downs else 0

	data['u1_comment_ups_unique'] = 100 * \
		data['u1_only_comment_ups'] // len(
			u1_comment_ups) if u1_comment_ups else 0
	data['u2_comment_ups_unique'] = 100 * \
		data['u2_only_comment_ups'] // len(
			u2_comment_ups) if u2_comment_ups else 0
	data['u1_comment_downs_unique'] = 100 * \
		data['u1_only_comment_downs'] // len(
			u1_comment_downs) if u1_comment_downs else 0
	data['u2_comment_downs_unique'] = 100 * \
		data['u2_only_comment_downs'] // len(
			u2_comment_downs) if u2_comment_downs else 0

	return render_template("admin/alt_votes.html",
						u1=u1,
						u2=u2,
						v=v,
						data=data
						)

@app.get("/admin/alts")
@app.get("/@<username>/alts")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['USER_LINK'])
def admin_view_alts(v, username=None):
	u = get_user(username or request.values.get('username'), graceful=True)
	return render_template('admin/alts.html', v=v, u=u, alts=u.alts if u else None)

@app.post('/@<username>/alts')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['USER_LINK'])
def admin_add_alt(v, username):
	user1 = get_user(username)
	user2 = get_user(request.values.get('other_username'))
	if user1.id == user2.id: stop(400, "Can't add the same account as alts of each other")

	ids = [user1.id, user2.id]
	a = g.db.query(Alt).filter(Alt.user1.in_(ids), Alt.user2.in_(ids)).one_or_none()
	if a: stop(409, f"@{user1.username} and @{user2.username} are already known alts!")
	a = Alt(
		user1=user1.id,
		user2=user2.id,
		is_manual=True,
	)
	g.db.add(a)

	cache.delete_memoized(get_alt_graph_ids, user1.id)
	cache.delete_memoized(get_alt_graph_ids, user2.id)

	check_for_alts(user1)
	check_for_alts(user2)

	ma = ModAction(
		kind=f"link_accounts",
		user_id=v.id,
		target_user_id=user1.id,
		_note=f'with @{user2.username}'
	)
	g.db.add(ma)
	return {"message": f"Linked @{user1.username} and @{user2.username} successfully!"}

@app.post('/@<username>/alts/<int:other>/deleted')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['USER_LINK'])
def admin_delink_relink_alt(v, username, other):
	user1 = get_user(username)
	user2 = get_account(other)
	ids = [user1.id, user2.id]
	a = g.db.query(Alt).filter(Alt.user1.in_(ids), Alt.user2.in_(ids)).one_or_none()
	if not a: stop(404, "Alt doesn't exist.")
	g.db.delete(a)

	cache.delete_memoized(get_alt_graph_ids, user1.id)
	cache.delete_memoized(get_alt_graph_ids, user2.id)

	check_for_alts(user1)
	check_for_alts(user2)

	ma = ModAction(
		kind=f"delink_accounts",
		user_id=v.id,
		target_user_id=user1.id,
		_note=f'from @{user2.username}'
	)
	g.db.add(ma)

	return {"message": f"Delinked @{user1.username} and @{user2.username} successfully!"}


@app.get("/admin/removed/posts")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def admin_removed(v):
	page = get_page()

	listing = g.db.query(Post).options(load_only(Post.id)).join(Post.author).filter(
			or_(Post.is_banned==True, User.shadowbanned != None))

	total = listing.count()
	listing = listing.order_by(Post.id.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()
	listing = [x.id for x in listing]

	posts = get_posts(listing, v=v)

	return render_template("admin/removed_posts.html",
						v=v,
						listing=posts,
						page=page,
						total=total
						)


@app.get("/admin/removed/comments")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def admin_removed_comments(v):
	page = get_page()

	listing = g.db.query(Comment).options(load_only(Comment.id)).join(Comment.author).filter(
			or_(Comment.is_banned==True, User.shadowbanned != None))

	total = listing.count()
	listing = listing.order_by(Comment.id.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()
	listing = [x.id for x in listing]

	comments = get_comments(listing, v=v)

	return render_template("admin/removed_comments.html",
						v=v,
						listing=comments,
						page=page,
						total=total
						)


@app.post("/unchud_user/<fullname>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['USER_CHUD'])
def unchud(fullname, v):

	if fullname.startswith('p_'):
		post_id = fullname.split('p_')[1]
		post = g.db.get(Post, post_id)
		user = post.author
	elif fullname.startswith('c_'):
		comment_id = fullname.split('c_')[1]
		comment = g.db.get(Comment, comment_id)
		user = comment.author
	else:
		user = get_account(fullname)

	if not user.chudded_by:
		stop(403, "Jannies can't undo chud awards!")

	user.chud = 0
	user.chud_phrase = None
	user.chudded_by = None
	g.db.add(user)

	ma = ModAction(
		kind="unchud",
		user_id=v.id,
		target_user_id=user.id
	)

	g.db.add(ma)

	badge = user.has_badge(58)
	if badge: g.db.delete(badge)

	send_repeatable_notification(user.id, f"@{v.username} (a site admin) has unchudded you.")

	return {"message": f"@{user.username} has been unchudded!"}


@app.post("/shadowban/<int:user_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['USER_SHADOWBAN'])
def shadowban(user_id, v):
	user = get_account(user_id)
	if user.admin_level > v.admin_level:
		stop(403, "You can't shadowban an admin with higher level than you.")
	reason = request.values.get("reason", "").strip()

	if not reason:
		stop(400, "You need to submit a reason for shadowbanning!")

	if len(reason) > BAN_REASON_LENGTH_LIMIT:
		stop(400, f"Shadowban reason is too long (max {BAN_REASON_LENGTH_LIMIT} characters)")

	reason = filter_emojis_only(reason)

	if len(reason) > BAN_REASON_HTML_LENGTH_LIMIT:
		stop(400, "Rendered shadowban reason is too long!")

	reason = reason_regex_post.sub(r'<a href="\1">\1</a>', reason)
	reason = reason_regex_comment.sub(r'<a href="\1#context">\1</a>', reason)

	user.shadowban(admin=v, reason=reason)
	check_for_alts(user)


	cache.delete_memoized(frontlist)

	return {"message": f"@{user.username} has been shadowbanned!"}

@app.post("/unshadowban/<int:user_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['USER_SHADOWBAN'])
def unshadowban(user_id, v):
	user = get_account(user_id)
	user.shadowbanned = None
	user.shadowban_reason = None
	g.db.add(user)

	for alt in get_alt_graph(user.id, unban=True):
		alt.shadowbanned = None
		alt.shadowban_reason = None
		g.db.add(alt)

	ma = ModAction(
		kind="unshadowban",
		user_id=v.id,
		target_user_id=user.id,
	)
	g.db.add(ma)

	cache.delete_memoized(frontlist)

	return {"message": f"@{user.username} has been unshadowbanned!"}


@app.post("/admin/change_flair/<int:user_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['USER_CHANGE_FLAIR'])
def admin_change_flair(user_id, v):

	user = get_account(user_id)

	new_flair = request.values.get("flair", "").strip()

	if len(new_flair) > 256:
		stop(400, "New flair is too long (max 256 characters)")

	user.flair = new_flair
	new_flair = filter_emojis_only(new_flair, link=True)
	new_flair = censor_slurs_profanities(new_flair, None)

	user = get_account(user.id)
	user.flair_html = new_flair
	if request.values.get("locked"):
		user.flairchanged = int(time.time()) + 2629746
		badge_grant(user=user, badge_id=96)
	else:
		user.flairchanged = 0
		badge = user.has_badge(96)
		if badge: g.db.delete(badge)

	g.db.add(user)

	if user.flairchanged: kind = "set_flair_locked"
	else: kind = "set_flair_notlocked"

	ma = ModAction(
		kind=kind,
		user_id=v.id,
		target_user_id=user.id,
		_note=f'"{new_flair}"'
		)
	g.db.add(ma)

	if user.flairchanged:
		message = f"@{v.username} (a site admin) has locked your flair to `{user.flair}`."
	else:
		message = f"@{v.username} (a site admin) has changed your flair to `{user.flair}`. You can change it back in the settings."

	send_repeatable_notification(user.id, message)

	return {"message": f"@{user.username}'s flair has been changed!"}

@app.post("/ban_user/<fullname>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['USER_BAN'])
def ban_user(fullname, v):

	post = None
	comment = None

	if fullname.startswith('p_'):
		post_id = fullname.split('p_')[1]
		post = g.db.get(Post, post_id)
		user = post.author
	elif fullname.startswith('c_'):
		comment_id = fullname.split('c_')[1]
		comment = g.db.get(Comment, comment_id)
		user = comment.author
	else:
		user = get_account(fullname)

	if user.admin_level > v.admin_level:
		stop(403, "You can't ban an admin with higher level than you.")

	if user.is_permabanned:
		stop(403, f"@{user.username} is already banned permanently!")

	days = 0.0
	try:
		days = float(request.values.get("days"))
	except:
		pass

	if days < 0:
		stop(400, "You can't bans people for negative days!")

	reason = request.values.get("reason", "").strip()

	if not reason:
		stop(400, "You need to submit a reason for banning!")

	if len(reason) > BAN_REASON_LENGTH_LIMIT:
		stop(400, f"Ban reason is too long (max {BAN_REASON_LENGTH_LIMIT} characters)")

	reason = filter_emojis_only(reason)

	if len(reason) > BAN_REASON_HTML_LENGTH_LIMIT:
		stop(400, "Rendered ban reason is too long!")

	reason = reason_regex_post.sub(r'<a href="\1">\1</a>', reason)
	reason = reason_regex_comment.sub(r'<a href="\1#context">\1</a>', reason)

	if days:
		days_txt = str(days)
		if days_txt.endswith('.0'): days_txt = days_txt[:-2]
		duration = f"for {days_txt} day"
		if days != 1: duration += "s"
	else:
		duration = "permanently"

	text = f"@{v.username} (a site admin) has banned you {duration} for the following reason:\n\n> {reason}"

	user.ban(admin=v, reason=reason, days=days)
	send_repeatable_notification(user.id, text)

	if SITE_NAME == 'WPD' or request.values.get("alts"):
		for x in get_alt_graph(user.id):
			if x.admin_level > v.admin_level:
				continue
			x.ban(admin=v, reason=reason, days=days, modlog=False, original_user=user)
			one_month_ago = time.time() - 2592000
			if x.last_active > one_month_ago:
				send_repeatable_notification(x.id, text)

	if 'reason' in request.values:
		reason = request.values["reason"]
		if post:
			actual_reason = reason.replace(f'/post/{post.id}', '').strip()
			post.bannedfor = f'{duration} by @{v.username}'
			if actual_reason:
				post.bannedfor += f' for "{actual_reason}"'
			g.db.add(post)
		elif comment:
			actual_reason = reason.replace(f'/comment/{comment.id}', '').strip()
			comment.bannedfor = f'{duration} by @{v.username}'
			if actual_reason:
				comment.bannedfor += f' for "{actual_reason}"'
			g.db.add(comment)

	return {"message": f"@{user.username} has been banned {duration}!"}


@app.post("/chud_user/<fullname>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['USER_CHUD'])
def chud(fullname, v):

	if fullname.startswith('p_'):
		post_id = fullname.split('p_')[1]
		post = g.db.get(Post, post_id)
		post.chudded = True
		user = post.author
	elif fullname.startswith('c_'):
		comment_id = fullname.split('c_')[1]
		comment = g.db.get(Comment, comment_id)
		comment.chudded = True
		g.db.add(comment)
		user = comment.author
	else:
		user = get_account(fullname)

	if user.admin_level > v.admin_level:
		stop(403)

	if user.chud == 1:
		stop(403, f"@{user.username} is already chudded permanently!")

	days = 0.0
	try:
		days = float(request.values.get("days"))
	except:
		pass

	if days < 0:
		stop(400, "You can't chud people for negative days!")

	reason = request.values.get("reason", "").strip()

	reason = filter_emojis_only(reason)

	reason = reason_regex_post.sub(r'<a href="\1">\1</a>', reason)
	reason = reason_regex_comment.sub(r'<a href="\1#context">\1</a>', reason)

	if days:
		if user.chud:
			user.chud += days * 86400
		else:
			user.chud = int(time.time()) + (days * 86400)

		days_txt = str(days)
		if days_txt.endswith('.0'): days_txt = days_txt[:-2]
		duration = f"for {days_txt} day"
		if days != 1: duration += "s"
	else:
		user.chud = 1
		duration = "permanently"

	user.chud_phrase = request.values.get("chud_phrase", "Trans lives matter").strip()

	text = f"@{v.username} (a site admin) has chudded you **{duration}**"
	if reason: text += f" for the following reason:\n\n> {reason}"
	text += f"\n\n**You now have to say this phrase in all posts and comments you make {duration}:**\n\n> {user.chud_phrase}"
	if SITE_NAME == 'rDrama':
		text += f"\n\nPlease keep your chud behavior to /h/chudrama in the future!"

	user.chudded_by = v.id
	g.db.add(user)

	send_repeatable_notification(user.id, text)

	note = f'duration: {duration}'
	if reason: note += f', reason: "{reason}"'
	note += f', chud phrase: "{user.chud_phrase}"'

	ma = ModAction(
		kind="chud",
		user_id=v.id,
		target_user_id=user.id,
		_note=note
		)
	g.db.add(ma)

	badge_grant(user=user, badge_id=58)

	if 'reason' in request.values:
		reason = request.values["reason"]
		if reason.startswith("/post/"):
			try: post = int(reason.split("/post/")[1].split(None, 1)[0])
			except: stop(400)
			post = get_post(post)
			if post.hole == 'chudrama':
				stop(403, "You can't chud people in /h/chudrama")
			post.chuddedfor = f'{duration} by @{v.username}'
			g.db.add(post)
		elif reason.startswith("/comment/"):
			try: comment = int(reason.split("/comment/")[1].split(None, 1)[0])
			except: stop(400)
			comment = get_comment(comment)
			if comment.parent_post and comment.post.hole == 'chudrama':
				stop(403, "You can't chud people in /h/chudrama")
			comment.chuddedfor = f'{duration} by @{v.username}'
			g.db.add(comment)

	return {"message": f"@{user.username} has been chudded {duration}!"}


@app.post("/unban_user/<fullname>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['USER_BAN'])
def unban_user(fullname, v):

	if fullname.startswith('p_'):
		post_id = fullname.split('p_')[1]
		post = g.db.get(Post, post_id)
		user = post.author
	elif fullname.startswith('c_'):
		comment_id = fullname.split('c_')[1]
		comment = g.db.get(Comment, comment_id)
		user = comment.author
	else:
		user = get_account(fullname)

	if not user.is_banned:
		stop(400)

	if FEATURES['AWARDS'] and user.ban_reason and user.ban_reason.startswith('Ban award'):
		stop(403, "You can't undo a ban award!")

	user.is_banned = None
	user.unban_utc = None
	user.ban_reason = None
	send_repeatable_notification(user.id, f"@{v.username} (a site admin) has unbanned you!")
	g.db.add(user)

	for x in get_alt_graph(user.id, unban=True):
		if x.is_banned:
			one_month_ago = time.time() - 2592000
			if x.last_active > one_month_ago:
				send_repeatable_notification(x.id, f"@{v.username} (a site admin) has unbanned you!")
		x.is_banned = None
		x.unban_utc = None
		x.ban_reason = None
		g.db.add(x)

	ma = ModAction(
		kind="unban_user",
		user_id=v.id,
		target_user_id=user.id,
		)
	g.db.add(ma)

	return {"message": f"@{user.username} has been unbanned!"}

@app.post("/mute_user/<int:user_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['USER_BAN'])
def mute_user(v, user_id):
	user = get_account(user_id)

	if not user.is_muted:
		user.is_muted = True
		ma = ModAction(
				kind='mute_user',
				user_id=v.id,
				target_user_id=user.id,
				)
		g.db.add(user)
		g.db.add(ma)
		check_for_alts(user)

		send_repeatable_notification(user.id, f"@{v.username} (a site admin) has muted you!")

	return {"message": f"@{user.username} has been muted!"}


@app.post("/unmute_user/<int:user_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['USER_BAN'])
def unmute_user(v, user_id):
	user = get_account(user_id)

	if user.is_muted:
		user.is_muted = False
		ma = ModAction(
				kind='unmute_user',
				user_id=v.id,
				target_user_id=user.id,
				)
		g.db.add(user)
		g.db.add(ma)

		for x in get_alt_graph(user.id):
			if x.is_muted:
				x.is_muted = False
				g.db.add(x)

		send_repeatable_notification(user.id, f"@{v.username} (a site admin) has unmuted you!")

	return {"message": f"@{user.username} has been unmuted!"}

@app.post("/admin/progstack/post/<int:post_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['PROGSTACK'])
def progstack_post(post_id, v):
	post = get_post(post_id)
	post.is_approved = PROGSTACK_ID
	post.realupvotes = floor(post.realupvotes * PROGSTACK_MUL)
	g.db.add(post)

	ma = ModAction(
		kind="progstack_post",
		user_id=v.id,
		target_post_id=post.id,
		)
	g.db.add(ma)

	cache.delete_memoized(frontlist)
	return {"message": "Progressive stack applied on post!"}

@app.post("/admin/unprogstack/post/<int:post_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['PROGSTACK'])
def unprogstack_post(post_id, v):
	post = get_post(post_id)
	post.is_approved = None
	g.db.add(post)

	ma = ModAction(
		kind="unprogstack_post",
		user_id=v.id,
		target_post_id=post.id,
		)
	g.db.add(ma)

	return {"message": "Progressive stack removed from post!"}

@app.post("/admin/progstack/comment/<int:comment_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['PROGSTACK'])
def progstack_comment(comment_id, v):
	comment = get_comment(comment_id)
	comment.is_approved = PROGSTACK_ID
	comment.realupvotes = floor(comment.realupvotes * PROGSTACK_MUL)
	g.db.add(comment)

	ma = ModAction(
		kind="progstack_comment",
		user_id=v.id,
		target_comment_id=comment.id,
		)
	g.db.add(ma)

	cache.delete_memoized(comment_idlist)
	return {"message": "Progressive stack applied on comment!"}

@app.post("/admin/unprogstack/comment/<int:comment_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['PROGSTACK'])
def unprogstack_comment(comment_id, v):
	comment = get_comment(comment_id)
	comment.is_approved = None
	g.db.add(comment)

	ma = ModAction(
		kind="unprogstack_comment",
		user_id=v.id,
		target_comment_id=comment.id,
		)
	g.db.add(ma)

	return {"message": "Progressive stack removed from comment!"}

@app.post("/remove_post/<int:post_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def remove_post(post_id, v):
	post = get_post(post_id)
	post.is_banned = True

	for media_usage in post.media_usages:
		media_usage.removed_utc = time.time()
		g.db.add(media_usage)

	post.is_approved = None

	if not FEATURES['AWARDS'] or not post.pinned or not post.pinned.endswith(PIN_AWARD_TEXT):
		post.pinned = None
		post.pinned_utc = None

	post.profile_pinned = False
	post.ban_reason = v.username
	g.db.add(post)

	ma = ModAction(
		kind="remove_post",
		user_id=v.id,
		target_post_id=post.id,
		)
	g.db.add(ma)

	post.author.charge_account('coins', post.coins, should_check_balance=False)
	post.author.truescore -= post.coins
	g.db.add(post.author)

	cache.delete_memoized(frontlist)

	for sort in COMMENT_SORTS.keys():
		cache.delete(f'post_{post.id}_{sort}')

	return {"message": "Post removed!"}


@app.post("/approve_post/<int:post_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def approve_post(post_id, v):
	post = get_post(post_id)

	if post.chudded and post.author.chud and post.ban_reason == 'AutoJanny for lack of chud phrase':
		stop(400, "You can't bypass the chud award!")

	if post.is_banned:
		ma = ModAction(
			kind="approve_post",
			user_id=v.id,
			target_post_id=post.id,
		)
		g.db.add(ma)

	post.is_banned = False

	for media_usage in post.media_usages:
		media_usage.removed_utc = None
		g.db.add(media_usage)

	post.ban_reason = None
	post.is_approved = v.id

	g.db.add(post)

	post.author.pay_account('coins', post.coins)
	post.author.truescore += post.coins
	g.db.add(post.author)

	cache.delete_memoized(frontlist)

	for sort in COMMENT_SORTS.keys():
		cache.delete(f'post_{post.id}_{sort}')

	return {"message": "Post approved!"}


@app.post("/pin_post/<int:post_id>")
@feature_required('PINS')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['PINNING_POSTS'])
def pin_post(post_id, v):
	post = get_post(post_id)

	if post.is_banned:
		stop(403, "Can't pin removed posts!")

	if FEATURES['AWARDS'] and post.pinned and post.pinned.endswith(PIN_AWARD_TEXT) and v.admin_level < PERMS["UNDO_AWARD_PINS"]:
		stop(403, "Can't pin award pins!")

	permapinned = g.db.query(Post).filter(
		Post.pinned != None,
		Post.pinned_utc == None,
		Post.is_banned == False,
	).count()

	if not post.pinned_utc:
		post.pinned_utc = int(time.time()) + 3600
		pin_time = 'for 1 hour'
		code = 200
		if v.id != post.author_id:
			send_repeatable_notification(post.author_id, f"@{v.username} (a site admin) has pinned {post.textlink}")
	else:
		if permapinned >= PIN_LIMIT:
			stop(403, f"Can't have more than {PIN_LIMIT} permapinned posts!")
		post.pinned_utc = None
		pin_time = 'permanently'
		code = 201

	post.pinned = v.username

	g.db.add(post)

	ma = ModAction(
		kind="pin_post",
		user_id=v.id,
		target_post_id=post.id,
		_note=pin_time
	)
	g.db.add(ma)

	cache.delete_memoized(frontlist)

	return {"message": f"Post pinned {pin_time}!"}, code


@app.post("/unpin_post/<int:post_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['PINNING_POSTS'])
def unpin_post(post_id, v):
	post = get_post(post_id)
	if post.pinned:
		if FEATURES['AWARDS'] and post.pinned.endswith(PIN_AWARD_TEXT) and v.admin_level < PERMS["UNDO_AWARD_PINS"]:
			stop(403, "Can't unpin award pins!")

		post.pinned = None
		post.pinned_utc = None
		g.db.add(post)

		ma = ModAction(
			kind="unpin_post",
			user_id=v.id,
			target_post_id=post.id
		)
		g.db.add(ma)

		if v.id != post.author_id:
			send_repeatable_notification(post.author_id, f"@{v.username} (a site admin) has unpinned {post.textlink}")

		cache.delete_memoized(frontlist)
	return {"message": "Post unpinned!"}

@app.post("/pin_comment_admin/<int:cid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['PINNING_COMMENTS'])
def pin_comment_admin(cid, v):
	comment = get_comment(cid, v=v)

	if comment.is_banned:
		stop(403, "Can't pin removed comments!")

	if FEATURES['AWARDS'] and comment.pinned and comment.pinned.endswith(PIN_AWARD_TEXT) and v.admin_level < PERMS["UNDO_AWARD_PINS"]:
		stop(403, "Can't pin award pins!")

	if not comment.pinned:
		comment.pinned = v.username
		g.db.add(comment)

		ma = ModAction(
			kind="pin_comment",
			user_id=v.id,
			target_comment_id=comment.id
		)
		g.db.add(ma)

		if v.id != comment.author_id:
			message = f"@{v.username} (a site admin) has pinned {comment.textlink}"
			send_repeatable_notification(comment.author_id, message)

		comment.pin_parents()

	return {"message": "Comment pinned!"}


@app.post("/unpin_comment_admin/<int:cid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['PINNING_COMMENTS'])
def unpin_comment_admin(cid, v):
	comment = get_comment(cid, v=v)

	if comment.pinned:
		if FEATURES['AWARDS'] and comment.pinned.endswith(PIN_AWARD_TEXT) and v.admin_level < PERMS["UNDO_AWARD_PINS"]:
			stop(403, "Can't unpin award pins!")

		comment.pinned = None
		comment.pinned_utc = None
		g.db.add(comment)

		ma = ModAction(
			kind="unpin_comment",
			user_id=v.id,
			target_comment_id=comment.id
		)
		g.db.add(ma)

		if v.id != comment.author_id:
			message = f"@{v.username} (a site admin) has unpinned {comment.textlink}"
			send_repeatable_notification(comment.author_id, message)

		comment.unpin_parents()

	return {"message": "Comment unpinned!"}


@app.post("/remove_comment/<int:c_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def remove_comment(c_id, v):
	comment = get_comment(c_id)

	comment.is_banned = True

	if comment.pinned:
		comment.pinned = None
		comment.pinned_utc = None
		comment.unpin_parents()

	for media_usage in comment.media_usages:
		media_usage.removed_utc = time.time()
		g.db.add(media_usage)

	comment.is_approved = None
	comment.ban_reason = v.username
	g.db.add(comment)
	ma = ModAction(
		kind="remove_comment",
		user_id=v.id,
		target_comment_id=comment.id,
		)
	g.db.add(ma)

	comment.author.charge_account('coins', comment.coins, should_check_balance=False)
	comment.author.truescore -= comment.coins
	g.db.add(comment.author)

	if comment.parent_post:
		for sort in COMMENT_SORTS.keys():
			cache.delete(f'post_{comment.parent_post}_{sort}')

	return {"message": "Comment removed!"}


@app.post("/approve_comment/<int:c_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['POST_COMMENT_MODERATION'])
def approve_comment(c_id, v):
	comment = get_comment(c_id)

	if comment.chudded and comment.author.chud and comment.ban_reason == 'AutoJanny for lack of chud phrase':
		stop(400, "You can't bypass the chud award!")

	if comment.is_banned:
		ma = ModAction(
			kind="approve_comment",
			user_id=v.id,
			target_comment_id=comment.id,
			)
		g.db.add(ma)

	comment.is_banned = False

	for media_usage in comment.media_usages:
		media_usage.removed_utc = None
		g.db.add(media_usage)

	comment.ban_reason = None
	comment.is_approved = v.id

	g.db.add(comment)

	comment.author.pay_account('coins', comment.coins)
	comment.author.truescore += comment.coins
	g.db.add(comment.author)

	if comment.parent_post:
		for sort in COMMENT_SORTS.keys():
			cache.delete(f'post_{comment.parent_post}_{sort}')

	return {"message": "Comment approved!"}

@app.get("/admin/banned_domains")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['DOMAINS_BAN'])
def admin_banned_domains(v):
	banned_domains = g.db.query(BannedDomain) \
		.order_by(BannedDomain.created_utc).all()
	return render_template("admin/banned_domains.html", v=v, banned_domains=banned_domains)

@app.post("/admin/ban_domain")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['DOMAINS_BAN'])
def ban_domain(v):

	domain = request.values.get("domain", "").strip().lower()
	if not domain: stop(400)

	reason = request.values.get("reason", "").strip()
	if not reason: stop(400, 'Reason is required!')

	if len(reason) > 100:
		stop(400, 'Reason is too long (max 100 characters)')

	existing = g.db.get(BannedDomain, domain)
	if not existing:
		d = BannedDomain(domain=domain, reason=reason)
		g.db.add(d)
		ma = ModAction(
			kind="ban_domain",
			user_id=v.id,
			_note=f'{domain}, reason: {reason}'
		)
		g.db.add(ma)

	return {"message": "Domain banned successfully!"}


@app.post("/admin/unban_domain/<path:domain>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['DOMAINS_BAN'])
def unban_domain(v, domain):
	existing = g.db.get(BannedDomain, domain)
	if not existing: stop(400, 'Domain is not banned!')

	g.db.delete(existing)
	ma = ModAction(
		kind="unban_domain",
		user_id=v.id,
		_note=domain
	)
	g.db.add(ma)

	return {"message": f"{domain} has been unbanned!"}



@app.post("/admin/nuke_user")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['NUKE_USER'])
def admin_nuke_user(v):

	user = get_user(request.values.get("user"))

	for post in g.db.query(Post).filter_by(author_id=user.id):
		if post.is_banned:
			continue

		post.is_banned = True

		for media_usage in post.media_usages:
			media_usage.removed_utc = time.time()
			g.db.add(media_usage)

		post.ban_reason = f'{v.username} (Mass Removal)'
		g.db.add(post)

	for comment in g.db.query(Comment).filter_by(author_id=user.id):
		if comment.is_banned:
			continue

		comment.is_banned = True

		for media_usage in comment.media_usages:
			media_usage.removed_utc = time.time()
			g.db.add(media_usage)

		comment.ban_reason = f'{v.username} (Mass Removal)'
		g.db.add(comment)

	ma = ModAction(
		kind="nuke_user",
		user_id=v.id,
		target_user_id=user.id,
		)
	g.db.add(ma)

	return {"message": f"@{user.username}'s content has been removed!"}


@app.post("/admin/unnuke_user")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['NUKE_USER'])
def admin_nunuke_user(v):

	user = get_user(request.values.get("user"))

	objs = g.db.query(Post).filter(
				Post.author_id == user.id,
				Post.is_banned == True,
				Post.ban_reason.like('%(Mass Removal)'),
			).all() + \
			g.db.query(Comment).filter(
				Comment.author_id == user.id,
				Comment.is_banned == True,
				Comment.ban_reason.like('%(Mass Removal)'),
			).all()

	if not objs:
		stop(400, "There is no previous mass content removal to revert!")

	for obj in objs:
		obj.is_banned = False

		for media_usage in obj.media_usages:
			media_usage.removed_utc = None
			g.db.add(media_usage)

		obj.ban_reason = None
		obj.is_approved = v.id
		g.db.add(obj)

	ma = ModAction(
		kind="unnuke_user",
		user_id=v.id,
		target_user_id=user.id,
		)
	g.db.add(ma)

	return {"message": "Previous mass content removal reverted successfully!"}

@app.post("/blacklist/<int:user_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['USER_BLACKLIST'])
def blacklist_user(user_id, v):
	user = get_account(user_id)
	if user.admin_level > v.admin_level:
		stop(403)
	user.blacklisted_by = v.id
	g.db.add(user)
	check_for_alts(user)

	ma = ModAction(
		kind="blacklist_user",
		user_id=v.id,
		target_user_id=user.id
	)
	g.db.add(ma)

	return {"message": f"@{user.username} has been blacklisted from restricted holes!"}

@app.post("/unblacklist/<int:user_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['USER_BLACKLIST'])
def unblacklist_user(user_id, v):
	user = get_account(user_id)
	user.blacklisted_by = None
	g.db.add(user)

	for alt in get_alt_graph(user.id):
		alt.blacklisted_by = None
		g.db.add(alt)

	ma = ModAction(
		kind="unblacklist_user",
		user_id=v.id,
		target_user_id=user.id
	)
	g.db.add(ma)

	return {"message": f"@{user.username} has been unblacklisted from restricted holes!"}

@app.get('/admin/delete_media')
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['DELETE_MEDIA'])
def delete_media_get(v):
	return render_template("admin/delete_media.html", v=v)

@app.post("/admin/delete_media")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("50/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("50/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['DELETE_MEDIA'])
def delete_media_post(v):
	url = request.values.get("url")
	if not url:
		stop(400, "No url provided!")

	url = url.replace('https://videos2.watchpeopledie.tv/', 'https://videos.watchpeopledie.tv/')

	if not image_link_regex.fullmatch(url) and not video_link_regex.fullmatch(url) and not asset_image_link_regex.fullmatch(url):
		stop(400, "Invalid url")

	path = url.split(SITE)[1]

	if path.startswith('/1'):
		path = '/videos' + path

	if path.startswith('/assets/images'):
		path = 'files' + path.split('?x=')[0]

	if os.path.isfile(path):
		os.remove(path)

	to_delete = g.db.query(Post.thumburl, Post.posterurl).filter_by(url=url).all()
	for tup in to_delete:
		for extra_url in tup:
			if extra_url:
				remove_image_using_link(extra_url)
				purge_files_in_cloudflare_cache(extra_url)

	media = g.db.query(Media).filter_by(filename=path).one()
	media.purged_utc = time.time()
	g.db.add(media)

	if media.posterurl:
		remove_image_using_link(media.posterurl)
		purge_files_in_cloudflare_cache(media.posterurl)

	ma = ModAction(
		kind="delete_media",
		user_id=v.id,
		_note=f'<a href="{url}">{url}</a>',
		)
	g.db.add(ma)

	if SITE == 'watchpeopledie.tv' and url.startswith(SITE_FULL_VIDEOS):
		filename = url.split(SITE_FULL_VIDEOS)[1]
		gevent.spawn(rclone_delete, f'no:/videos{filename}')
	else:
		purge_files_in_cloudflare_cache(url)

	return {"message": "Media deleted successfully!"}

@app.post("/admin/reset_password/<int:user_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['USER_RESET_PASSWORD'])
def admin_reset_password(user_id, v):
	user = get_account(user_id)
	new_password = secrets.token_urlsafe(random.randint(27, 33))
	user.passhash = hash_password(new_password)
	g.db.add(user)

	ma = ModAction(
		kind="reset_password",
		user_id=v.id,
		target_user_id=user.id
	)
	g.db.add(ma)

	text = f"At your request, @{v.username} (a site admin) has reset your password to `{new_password}`, please change this to something else for personal security reasons. And be sure to save it this time, retard."
	send_repeatable_notification(user.id, text)

	text = f"@{user.username}'s new password is `{new_password}`"
	send_repeatable_notification(v.id, text)

	return {"message": f"@{user.username}'s password has been reset! The new password has been messaged to them and to you!"}

@app.get("/admin/insert_transaction")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['INSERT_TRANSACTION'])
def insert_transaction(v):
	return render_template("admin/insert_transaction.html", v=v)

@app.post("/admin/insert_transaction")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['INSERT_TRANSACTION'])
def insert_transaction_post(v):
	type = request.values.get("type", "").strip()
	id = request.values.get("id", "").strip()
	amount = request.values.get("amount", "").strip()
	username = request.values.get("username", "").strip()

	if type not in {DONATE_SERVICE, 'BTC', 'ETH', 'XMR', 'SOL', 'DOGE', 'LTC'}:
		stop(400, "Invalid transaction currency!")

	if type == DONATE_SERVICE:
		id = f'{DONATE_SERVICE}-' + str(int(time.time()))

	if not id:
		stop(400, "A transaction ID is required!")

	if not amount:
		stop(400, "A transaction amount is required!")

	if not username:
		stop(400, "A username is required!")

	amount = int(amount)

	existing = g.db.get(Transaction, id)
	if existing:
		stop(400, "This transaction is already registered!")

	user = get_user(username)

	transaction = Transaction(
		id=id,
		created_utc=time.time(),
		type=type,
		amount=amount,
		user_id=user.id,
	)
	g.db.add(transaction)

	ma = ModAction(
		kind="insert_transaction",
		user_id=v.id,
		target_user_id=user.id,
		_note=f'Transaction ID: {id}',
	)
	g.db.add(ma)

	claim_rewards_all_users()
	return {"message": "Transaction inserted successfully!"}

@app.get("/admin/under_siege")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['CHANGE_UNDER_SIEGE'])
def change_under_siege(v):
	thresholds = cache.get("under_siege_thresholds")
	if not thresholds:
		thresholds = DEFAULT_UNDER_SIEGE_THRESHOLDS
		cache.set("under_siege_thresholds", thresholds)

	return render_template('admin/under_siege.html', v=v, thresholds=thresholds)

@app.post("/admin/under_siege")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['CHANGE_UNDER_SIEGE'])
def change_under_siege_post(v):
	thresholds = {}
	for key in DEFAULT_UNDER_SIEGE_THRESHOLDS.keys():
		thresholds[key] = int(request.values.get(key))

	cache.set("under_siege_thresholds", thresholds)

	ma = ModAction(
		kind="change_under_siege",
		user_id=v.id,
	)
	g.db.add(ma)

	return {"message": "Thresholds changed successfully!"}

if FEATURES['IP_LOGGING']:
	@app.get("/@<username>/ips")
	@limiter.limit("2000/day", deduct_when=lambda response: response.status_code < 400)
	@limiter.limit("2000/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
	@admin_level_required(PERMS['VIEW_IPS'])
	def view_user_ips(v, username):
		u = get_user(username, v=v)
		ip_logs = g.db.query(IPLog).filter_by(user_id=u.id).order_by(IPLog.last_used.desc()).all()
		ips = {x.ip for x in ip_logs}
		ip_counts = {x[0]: x[1] for x in g.db.query(IPLog.ip, func.count(IPLog.ip)).filter(IPLog.ip.in_(ips)).group_by(IPLog.ip).all()}
		return render_template('admin/user_ips.html', v=v, u=u, ip_logs=ip_logs, ip_counts=ip_counts)

	@app.get("/ip_users/<ip>")
	@limiter.limit("2000/day", deduct_when=lambda response: response.status_code < 400)
	@limiter.limit("2000/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
	@admin_level_required(PERMS['VIEW_IPS'])
	def view_ip_users(v, ip):
		ip_logs = g.db.query(IPLog).filter_by(ip=ip).order_by(IPLog.last_used.desc())
		return render_template('admin/ip_users.html', v=v, ip=ip, ip_logs=ip_logs)


@app.post("/mark_effortpost/<int:pid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['MARK_EFFORTPOST'])
def mark_effortpost(pid, v):
	p = get_post(pid)

	if p.effortpost:
		stop(400, "Post is already marked as an effortpost!")

	if not p.can_be_effortpost:
		stop(403, "Post is too short!")

	p.effortpost = True
	g.db.add(p)

	if p.author.effortposts_made >= 99:
		badge_grant(badge_id=330, user=p.author)
	elif p.author.effortposts_made >= 9:
		badge_grant(badge_id=329, user=p.author)
	else:
		badge_grant(badge_id=328, user=p.author)

	ma = ModAction(
		kind = "mark_effortpost",
		user_id = v.id,
		target_post_id = p.id,
	)
	g.db.add(ma)

	coin_mul = get_coin_mul(Post, p)
	new_coins = (p.upvotes - 1 + p.downvotes) * coin_mul
	coins = new_coins - p.coins

	p.author.pay_account('coins', coins, f"Retroactive effortpost gains from {p.textlink}")

	if v.id != p.author_id:
		p.coins += coins
		send_repeatable_notification(p.author_id, f":marseyclapping: @{v.username} (a site admin) has marked {p.textlink} as an effortpost, it now gets x{coin_mul} coins from votes. You have received {coins} coins retroactively, thanks! :!marseyclapping:")

	return {"message": "Post has been marked as an effortpost!"}


@app.post("/unmark_effortpost/<int:pid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['MARK_EFFORTPOST'])
def unmark_effortpost(pid, v):
	p = get_post(pid)

	if not p.effortpost:
		stop(400, "Post is already not marked as an effortpost!")

	p.effortpost = False
	g.db.add(p)

	ma = ModAction(
		kind = "unmark_effortpost",
		user_id = v.id,
		target_post_id = p.id,
	)
	g.db.add(ma)

	coin_mul = get_coin_mul(Post, p)
	new_coins = (p.upvotes - 1 + p.downvotes) * coin_mul
	coins = p.coins - new_coins

	p.author.charge_account('coins', coins, f"Revocation of effortpost gains from {p.textlink}")

	if v.id != p.author_id:
		p.coins -= coins
		send_repeatable_notification(p.author_id, f":marseyitsover: @{v.username} (a site admin) has unmarked {p.textlink} as an effortpost. {coins} coins have been deducted from you. :!marseyitsover:")

	return {"message": "Post has been unmarked as an effortpost!"}

@app.get("/versions/<link>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def VIEW_VERSIONs(v, link):
	try:
		if "p_" in link: obj = get_post(int(link.split("p_")[1]), v=v)
		elif "c_" in link: obj = get_comment(int(link.split("c_")[1]), v=v)
		else: stop(400)
	except: stop(400)

	if v.id != obj.author_id and v.admin_level < PERMS['VIEW_VERSIONS']:
		stop(403, "You can't view other people's edits!")

	return render_template("versions.html", v=v, obj=obj)

@app.get("/@<username>/chats")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['VIEW_CHAT_LIST'])
def user_chats(v, username):
	u = get_user(username, v=v)

	chats1 = g.db.query(ChatMessage, Chat).join(Chat).distinct(Chat.id).filter(
			ChatMessage.user_id == u.id,
		).order_by(Chat.id, ChatMessage.created_utc.desc()).all()
	chats1_ids = {x[1].id for x in chats1}
	chats2 = g.db.query(ChatMembership, Chat).join(Chat).filter(
			ChatMembership.user_id == u.id,
			ChatMembership.chat_id.notin_(chats1_ids),
		).all()

	chats = chats1 + chats2
	chats = sorted(chats, key=lambda x:x[0].created_utc, reverse=True)

	total = len(chats)

	return render_template("userpage/chats.html", v=v, u=u, chats=chats, total=total)

@app.post('/admin/remove_note/post/<int:nid>')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("100/minute;300/hour;2000/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("100/minute;300/hour;2000/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['NOTES_REMOVE'])
def remove_note_post(v, nid):
	note = g.db.get(PostNote, nid)

	if note:
		for vote in note.votes:
			g.db.delete(vote)
		g.db.delete(note)

		ma = ModAction(
			kind="remove_note",
			user_id=v.id,
			target_post_id=note.parent_id,
		)
		g.db.add(ma)

	return {"message": "Note removed successfully!"}

@app.post('/admin/remove_note/comment/<int:nid>')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("100/minute;300/hour;2000/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("100/minute;300/hour;2000/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['NOTES_REMOVE'])
def remove_note_comment(v, nid):
	note = g.db.get(CommentNote, nid)

	if note:
		for vote in note.votes:
			g.db.delete(vote)
		g.db.delete(note)

		ma = ModAction(
			kind="remove_note",
			user_id=v.id,
			target_comment_id=note.parent_id,
		)
		g.db.add(ma)

	return {"message": "Note removed successfully!"}