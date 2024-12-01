import os
from shutil import copyfile
import user_agents

from sqlalchemy import func, text, or_
from files.helpers.media import *

import files.helpers.stats as statshelper
from files.classes.award import AWARDS
from files.classes.badges import Badge, BadgeDef
from files.classes.mod_logs import ModAction
from files.classes.userblock import UserBlock
from files.classes.usermute import UserMute
from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.config.modaction_kinds import *
from files.routes.wrappers import *
from files.routes.notifications import modmail_listing
from files.__main__ import app, cache, limiter


@app.get("/r/drama/comments/<id>/<path:path>")
@app.get("/r/Drama/comments/<id>/<path:path>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
def rdrama(id, path):
	id = ''.join(f'{x}/' for x in id)
	title = path.split("/")[0]
	return redirect(f'/archives/drama/comments/{id}{title}.html')

@app.get("/r/<subreddit>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_desired
def subreddit(subreddit, v):
	reddit = v.reddit if v else "old.reddit.com"
	return redirect(f'https://{reddit}/r/{subreddit}')

@app.get("/reddit/<subreddit>/comments/<path:path>")
@app.get("/r/<subreddit>/comments/<path:path>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_desired
def reddit_post(subreddit, v, path):
	reddit = v.reddit if v else "old.reddit.com"
	id = path.split("/")[0]
	return redirect(f'https://{reddit}/{id}')


@app.get("/marseys")
@app.get("/emojis")
def marseys_redirect():
	return redirect("/emojis/marsey")

@cache.cached(make_cache_key=lambda kind, nsfw:f"emoji_list_{kind}_{nsfw}", timeout=86400)
def get_emoji_list(kind, nsfw):
	emojis = g.db.query(Emoji).filter(Emoji.submitter_id == None, Emoji.kind == kind)

	if not nsfw:
		emojis = emojis.filter(Emoji.nsfw == False)

	emojis = emojis.order_by(Emoji.count.desc()).all()

	return emojis

@app.get("/emojis/<kind>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def emoji_list(v, kind):
	kind = kind.title()
	emojis = get_emoji_list(kind, g.show_nsfw)
	authors = get_accounts_dict([e.author_id for e in emojis], v=v, graceful=True)

	if FEATURES['EMOJI_SUBMISSIONS']:
		original = os.listdir("/asset_submissions/emojis/original")
		for emoji in emojis:
			emoji.user = authors.get(emoji.author_id)
			for x in IMAGE_FORMATS:
				if f'{emoji.name}.{x}' in original:
					emoji.og = f'{emoji.name}.{x}'
					break
	else:
		for emoji in emojis:
			emoji.user = authors.get(emoji.author_id)

	emojis_hash = cache.get('emojis_hash') or ''

	return render_template("emojis.html", v=v, emojis=emojis, kind=kind, emojis_hash=emojis_hash)



@cache.cached(make_cache_key=lambda nsfw:f"emojis_{nsfw}", timeout=86400)
def get_emojis(nsfw):
	emojis = g.db.query(Emoji, User).join(User, Emoji.author_id == User.id).options(load_only(
		User.id,
		User.username,
		User.original_username,
		User.extra_username,
		User.prelock_username,
	)).filter(Emoji.submitter_id == None)

	if not nsfw:
		emojis = emojis.filter(Emoji.nsfw == False)

	emojis1 = emojis.filter(Emoji.kind != 'Marsey Alphabet').order_by(Emoji.count.desc()).all()
	emojis2 = emojis.filter(Emoji.kind == 'Marsey Alphabet').order_by(func.length(Emoji.name), Emoji.name).all()
	emojis = emojis1 + emojis2

	collected = []
	for emoji, author in emojis:
		if author.id == 2:
			if SITE == 'rdrama.net':
				emoji.author_username = 'a WPD user'
			else:
				emoji.author_username = 'an rDrama user'
		else:
			emoji.author_username = author.username
			emoji.author_original_username = author.original_username
			emoji.author_extra_username = author.extra_username
			emoji.author_prelock_username = author.prelock_username
		collected.append(emoji.json())
	return collected

@app.get("/emojis.csv")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def emojis_csv(v):
	show_nsfw = request.values.get('show_nsfw') == 'True'
	return get_emojis(show_nsfw)


@cache.cached(make_cache_key=lambda :"flag_emojis", timeout=86400)
def get_flag_emojis():
	emojis = g.db.query(Emoji, User).join(User, Emoji.author_id == User.id).options(load_only(
		User.id,
		User.username,
		User.original_username,
		User.extra_username,
		User.prelock_username,
	)).filter(Emoji.submitter_id == None, Emoji.kind == 'Marsey Flags').order_by(Emoji.count.desc())

	collected = []
	for emoji, author in emojis:
		if author.id == 2:
			if SITE == 'rdrama.net':
				emoji.author_username = 'a WPD user'
			else:
				emoji.author_username = 'an rDrama user'
		else:
			emoji.author_username = author.username
			emoji.author_original_username = author.original_username
			emoji.author_extra_username = author.extra_username
			emoji.author_prelock_username = author.prelock_username
		collected.append(emoji.json())
	return collected

@app.get("/flag_emojis.csv")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def flag_emojis_csv(v):
	return get_flag_emojis()

@app.get("/groups.csv")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def groups_csv(v):
	groups = [x[0] for x in g.db.query(Group.name).order_by(Group.name).all()]
	groups += ['everyone', 'jannies', 'followers', 'commenters']
	if SITE_NAME != 'WPD':
		groups.append('holejannies')
	return groups

@app.get("/users.csv")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def users_csv(v):
	users = g.db.query(User.username, User.original_username, User.extra_username)

	if SITE == 'watchpeopledie.tv':
		users = users.filter(User.truescore > 100)

	if SITE == 'rdrama.net':
		t = time.time() - 604800
		users = users.filter(or_(User.truescore > 10, User.last_active > t))

	return [f'{x[0]},{x[1]},{x[2]}' for x in users.order_by(User.truescore.desc()).all()]

@app.get('/sidebar')
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_desired
def sidebar(v):
	return render_template('sidebar.html', v=v)

@app.get('/rules')
@app.get('/h/<hole>/rules')
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_desired
def rules(v, hole=None):
	hole_sidebar = None
	if hole:
		hole_sidebar = g.db.query(Hole.sidebar_html).filter_by(name=hole.lower()).one_or_none()
	return render_template('rules.html', v=v, hole_sidebar=hole_sidebar)

@app.get("/stats")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def participation_stats(v):
	stats = cache.get('stats')
	if not stats:
		stats = statshelper.stats()
		cache.set('stats', stats, timeout=172800)
	if v.client: return stats
	return render_template("stats.html", v=v, title="Statistics", stats=stats)

@app.get("/admin/patrons")
@app.get("/admin/paypigs")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['VIEW_PATRONS'])
def patrons(v):
	ids = [x[0] for x in g.db.query(User.id).filter(User.lifetimedonated > 0).order_by(User.email, User.truescore.desc()).distinct(User.email)]
	users = g.db.query(User).filter(User.id.in_(ids)).order_by(User.patron.desc(), User.truescore.desc()).all()

	return render_template("admin/patrons.html", v=v, users=users, benefactor_def=AWARDS['benefactor'])

@app.get("/admins")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def admins(v):
	admins = g.db.query(User).filter(User.admin_level >= PERMS['ADMIN_MOP_VISIBLE']).order_by(User.admin_level.desc(), User.truescore.desc()).all()
	return render_template("admins.html", v=v, admins=admins)

@app.get("/log")
@app.get("/modlog")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def log(v):

	page = get_page()

	admin = request.values.get("admin")
	if admin: admin_id = get_user(admin, attributes=[User.id]).id
	else: admin_id = 0

	target_id = int(request.values.get("target_id", 0))

	kind = request.values.get("kind")

	if v.admin_level >= PERMS['USER_SHADOWBAN']:
		if v.admin_level >= PERMS['PROGSTACK']:
			kinds = MODACTION_KINDS
		else:
			kinds = MODACTION_KINDS__FILTERED
	else: kinds = MODACTION_KINDS_FILTERED

	if kind and kind not in kinds:
		kind = None
		actions = []
		total = 0
	else:
		actions = g.db.query(ModAction)
		if v.admin_level < PERMS['USER_SHADOWBAN']:
			actions = actions.filter(ModAction.kind.notin_(MODACTION_PRIVILEGED_KINDS))
		if v.admin_level < PERMS['PROGSTACK']:
			actions = actions.filter(ModAction.kind.notin_(MODACTION_PRIVILEGED__KINDS))
		if admin_id:
			actions = actions.filter_by(user_id=admin_id)
			new_kinds = {x.kind for x in actions}
			new_kinds.add(kind)
			kinds2 = {}
			for k,val in kinds.items():
				if k in new_kinds: kinds2[k] = val
			kinds = kinds2
		if target_id:
			target_post_ids = [x[0] for x in g.db.query(Post.id).filter_by(author_id=target_id)]
			target_comment_ids = [x[0] for x in g.db.query(Comment.id).filter_by(author_id=target_id)]
			actions = actions.filter(or_(
				ModAction.target_user_id == target_id,
				ModAction.target_post_id.in_(target_post_ids),
				ModAction.target_comment_id.in_(target_comment_ids),
			))
			new_kinds = {x.kind for x in actions}
			new_kinds.add(kind)
			kinds2 = {}
			for k,val in kinds.items():
				if k in new_kinds: kinds2[k] = val
			kinds = kinds2
		if kind: actions = actions.filter_by(kind=kind)
		total = actions.count()
		actions = actions.order_by(ModAction.id.desc()).offset(PAGE_SIZE*(page-1)).limit(PAGE_SIZE).all()

	admins = [x[0] for x in g.db.query(User.username).filter(User.admin_level >= PERMS['ADMIN_MOP_VISIBLE']).order_by(func.lower(User.username))]

	return render_template("log.html", v=v, admins=admins, kinds=kinds, admin=admin, target_id=target_id, kind=kind, actions=actions, total=total, page=page, single_user_url='admin')

@app.get("/log/<int:id>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def log_item(id, v):
	action = g.db.get(ModAction, id)

	if not action: stop(404)

	if action.kind in MODACTION_PRIVILEGED_KINDS and v.admin_level < PERMS['USER_SHADOWBAN']:
		stop(404)

	admins = [x[0] for x in g.db.query(User.username).filter(User.admin_level >= PERMS['ADMIN_MOP_VISIBLE'])]

	if v.admin_level >= PERMS['USER_SHADOWBAN']:
		if v.admin_level >= PERMS['PROGSTACK']:
			kinds = MODACTION_KINDS
		else:
			kinds = MODACTION_KINDS__FILTERED
	else: kinds = MODACTION_KINDS_FILTERED

	return render_template("log.html", v=v, actions=[action], total=1, page=1, action=action, admins=admins, kinds=kinds, single_user_url='admin')

@app.get("/directory")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def directory(v):
	return render_template("directory.html", v=v)

@app.get("/api")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def api(v):
	return render_template("api.html", v=v)

@app.get("/contact")
@app.get("/contactus")
@app.get("/contact_us")
@app.get("/press")
@app.get("/media")
@app.get("/admin/chat")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_desired
def contact(v):
	if v:
		listing, total, page = modmail_listing(v)
	else:
		listing, total, page = None, None, None
	return render_template("contact.html",
							v=v,
							listing=listing,
							total=total,
							page=page,
							standalone=True,
							render_replies=True,
						)

@app.post("/contact")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("1/minute;10/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("1/minute;10/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def submit_contact(v):
	body = request.values.get("message")
	if not body: stop(400)

	if v.is_muted:
		stop(403, "You are muted!")

	body = process_files(request.files, v, body, is_dm=True)
	body = body.strip()
	body_html = sanitize(body)

	execute_antispam_duplicate_comment_check(v, body_html)

	new_comment = Comment(author_id=v.id,
						parent_post=None,
						level=1,
						body=body,
						body_html=body_html,
						sentto=MODMAIL_ID
						)
	g.db.add(new_comment)
	g.db.flush()
	execute_blackjack(v, new_comment, new_comment.body_html, 'modmail')
	execute_under_siege(v, new_comment, 'modmail')
	new_comment.top_comment_id = new_comment.id

	return {"message": "Your message has been sent to the admins!"}

@app.get("/badges")
@feature_required('BADGES')
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def badges(v):
	badges = g.db.query(BadgeDef)

	if v.admin_level < PERMS['VIEW_PATRONS']:
		badges = badges.filter(BadgeDef.id.notin_(PATRON_BADGES))

	badges = badges.order_by(BadgeDef.id).all()

	counts_raw = g.db.query(Badge.badge_id, func.count()).group_by(Badge.badge_id).all()
	users = g.db.query(User).count()

	counts = {}
	for c in counts_raw:
		counts[c[0]] = (c[1], float(c[1]) * 100 / max(users, 1))

	return render_template("badges.html", v=v, badges=badges, counts=counts)

@app.get("/blocks")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def blocks(v):
	sort = request.values.get("sort")

	page = get_page()

	blocks = g.db.query(UserBlock).options(
			joinedload(UserBlock.user),
			joinedload(UserBlock.target),
		)

	total = blocks.count()

	if sort == "user":
		key = text('users_1_username')
	elif sort == "target":
		key = text('users_2_username')
	else:
		sort = "time"
		key = UserBlock.created_utc.desc()

	blocks = blocks.order_by(key).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE)

	return render_template("blocks.html", v=v, blocks=blocks, sort=sort, total=total, page=page)

@app.get("/notification_mutes")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def mutes(v):
	mutes = g.db.query(UserMute).options(
			joinedload(UserMute.user),
			joinedload(UserMute.target),
		).order_by(UserMute.created_utc.desc())

	return render_template("notification_mutes.html", v=v, mutes=mutes)

@app.get("/formatting")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def formatting(v):
	return render_template("formatting.html", v=v, allowed_tags=allowed_tags, allowed_css_properties=allowed_css_properties)

@app.get("/app")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_desired
def mobile_app(v):
	return render_template("app.html", v=v)

@app.post("/dismiss_mobile_tip")
@limiter.limit('1/second', scope=rpath)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
def dismiss_mobile_tip():
	session["tooltip_dismissed"] = int(time.time())
	return ""

@app.get("/transfers/<int:id>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def transfers_id(id, v):

	transfer = g.db.get(Comment, id)

	if not transfer: stop(404)

	return render_template("transfers.html", v=v, page=1, comments=[transfer], standalone=True, total=1)

@app.get("/transfers")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def transfers(v):

	comments = g.db.query(Comment).filter(
		Comment.author_id == AUTOJANNY_ID,
		Comment.parent_post == None,
		Comment.body_html.like("%</a> has transferred %"),
	)

	page = get_page()

	total = comments.count()
	comments = comments.order_by(Comment.id.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()

	if v.client:
		return {"data": [x.json for x in comments]}
	else:
		return render_template("transfers.html", v=v, page=page, comments=comments, standalone=True, total=total)


@app.get('/donate')
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_desired
def donate(v):
	return render_template(f'donate.html', v=v)

@app.get("/sidebar_images")
@app.get("/banners")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def view_art(v):
	if request.path == '/sidebar_images':
		location_kind = 'sidebar'
		title = "Sidebar Images"
	else:
		location_kind = 'banners'
		title = "Banners"

	
	urls = os.listdir(f'files/assets/images/{SITE_NAME}/{location_kind}')
	urls = sorted(urls, key=lambda x: int(x.split('.webp')[0]), reverse=True)
	urls = [f"{SITE_FULL_IMAGES}/i/{SITE_NAME}/{location_kind}/{x}" for x in urls]

	return render_template(f'view_art.html', v=v, urls=urls, title=title, kind=location_kind)
