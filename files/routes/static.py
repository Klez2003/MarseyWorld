import os
from shutil import copyfile

from sqlalchemy import func
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
from files.helpers.config.modaction_types import *
from files.routes.wrappers import *
from files.__main__ import app, cache, limiter


@app.get("/r/drama/comments/<int:id>/<title>")
@app.get("/r/Drama/comments/<int:id>/<title>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
def rdrama(id, title):
	id = ''.join(f'{x}/' for x in id)
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
	post_id = path.rsplit("/", 1)[0].replace('/', '')
	reddit = v.reddit if v else "old.reddit.com"
	return redirect(f'https://{reddit}/{post_id}')


@cache.cached(make_cache_key=lambda kind, nsfw:f"emoji_list_{kind}_{nsfw}")
def get_emoji_list(kind, nsfw):
	li = g.db.query(Emoji, User).join(User, Emoji.author_id == User.id).filter(Emoji.submitter_id == None, Emoji.kind == kind)
	if not nsfw:
		li = li.filter(Emoji.nsfw == False)
	li = li.order_by(Emoji.count.desc())

	emojis = []
	for emoji, author in li:
		emoji.author = author.username if FEATURES['ASSET_SUBMISSIONS'] else None
		emojis.append(emoji)
	return emojis

@app.get("/marseys")
@app.get("/emojis")
def marseys_redirect():
	return redirect("/emojis/Marsey")

@app.get("/emojis/<kind>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def emoji_list(v, kind):
	emojis = get_emoji_list(kind, g.show_nsfw)
	authors = get_accounts_dict([e.author_id for e in emojis], v=v, graceful=True)

	if FEATURES['ASSET_SUBMISSIONS']:
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



@cache.cached(make_cache_key=lambda nsfw:f"emojis_{nsfw}")
def get_emojis(nsfw):
	emojis = g.db.query(Emoji, User).join(User, Emoji.author_id == User.id).filter(Emoji.submitter_id == None)

	if not nsfw:
		emojis = emojis.filter(Emoji.nsfw == False)

	emojis1 = emojis.filter(Emoji.kind != 'Marsey Alphabet').order_by(Emoji.count.desc()).all()
	emojis2 = emojis.filter(Emoji.kind == 'Marsey Alphabet').order_by(func.length(Emoji.name), Emoji.name).all()
	emojis = emojis1 + emojis2

	collected = []
	for emoji, author in emojis:
		if FEATURES['ASSET_SUBMISSIONS']:
			emoji.author_username = author.username
			emoji.author_original_username = author.original_username
			emoji.author_prelock_username = author.prelock_username
		collected.append(emoji.json())
	return collected

@app.get("/emojis_json")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def emojis(v):
	return get_emojis(g.show_nsfw)



@app.get('/sidebar')
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_desired
def sidebar(v):
	return render_template('sidebar.html', v=v)


@app.get("/stats")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def participation_stats(v):
	stats = cache.get('stats') or {}
	if v.client: return stats
	return render_template("stats.html", v=v, title="Content Statistics", data=stats)

@app.get("/chart")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
def chart():
	return redirect('/weekly_chart')

@app.get("/weekly_chart")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def weekly_chart(v):
	return send_file(statshelper.chart_path(kind="weekly", site=SITE))

@app.get("/daily_chart")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def daily_chart(v):
	return send_file(statshelper.chart_path(kind="daily", site=SITE))

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

	kind = request.values.get("kind")

	if v.can_see_shadowbanned:
		if v.admin_level >= PERMS['PROGSTACK']:
			types = MODACTION_TYPES
		else:
			types = MODACTION_TYPES__FILTERED
	else: types = MODACTION_TYPES_FILTERED

	if kind and kind not in types:
		kind = None
		actions = []
		total = 0
	else:
		actions = g.db.query(ModAction)
		if not v.can_see_shadowbanned:
			actions = actions.filter(ModAction.kind.notin_(MODACTION_PRIVILEGED_TYPES))
		if v.admin_level < PERMS['PROGSTACK']:
			actions = actions.filter(ModAction.kind.notin_(MODACTION_PRIVILEGED__TYPES))
		if admin_id:
			actions = actions.filter_by(user_id=admin_id)
			kinds = set([x.kind for x in actions])
			kinds.add(kind)
			types2 = {}
			for k,val in types.items():
				if k in kinds: types2[k] = val
			types = types2
		if kind: actions = actions.filter_by(kind=kind)
		total = actions.count()
		actions = actions.order_by(ModAction.id.desc()).offset(PAGE_SIZE*(page-1)).limit(PAGE_SIZE).all()

	admins = [x[0] for x in g.db.query(User.username).filter(User.admin_level >= PERMS['ADMIN_MOP_VISIBLE']).order_by(User.username)]

	return render_template("log.html", v=v, admins=admins, types=types, admin=admin, type=kind, actions=actions, total=total, page=page, single_user_url='admin')

@app.get("/log/<int:id>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def log_item(id, v):
	action = g.db.get(ModAction, id)

	if not action: abort(404)

	if action.kind in MODACTION_PRIVILEGED_TYPES and not v.can_see_shadowbanned:
		abort(404)

	admins = [x[0] for x in g.db.query(User.username).filter(User.admin_level >= PERMS['ADMIN_MOP_VISIBLE'])]

	if v.can_see_shadowbanned:
		if v.admin_level >= PERMS['PROGSTACK']:
			types = MODACTION_TYPES
		else:
			types = MODACTION_TYPES__FILTERED
	else: types = MODACTION_TYPES_FILTERED

	return render_template("log.html", v=v, actions=[action], total=1, page=1, action=action, admins=admins, types=types, single_user_url='admin')

@app.get("/directory")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def directory(v):
	if SITE_NAME != 'rDrama':
		abort(404)


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
	return render_template("contact.html", v=v)

@app.post("/contact")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("1/minute;10/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("1/minute;10/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def submit_contact(v):
	body = request.values.get("message")
	if not body: abort(400)

	if v.is_muted:
		abort(403)

	body = process_files(request.files, v, body)
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
	execute_under_siege(v, new_comment, new_comment.body_html, 'modmail')
	new_comment.top_comment_id = new_comment.id

	admin_ids = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS['NOTIFICATIONS_MODMAIL'])]

	if SITE == 'watchpeopledie.tv':
		if AEVANN_ID in admin_ids:
			admin_ids.remove(AEVANN_ID)
		if 'delete' in new_comment.body.lower() and 'account' in new_comment.body.lower():
			admin_ids.remove(15447)

	for admin_id in admin_ids:
		notif = Notification(comment_id=new_comment.id, user_id=admin_id)
		g.db.add(notif)

	push_notif(admin_ids, f'New modmail from @{new_comment.author_name}', new_comment.body, f'{SITE_FULL}/notifications/modmail')

	return {"message": "Your message has been sent to the admins!"}

patron_badges = (22,23,24,25,26,27,28,257,258,259,260,261)

@cache.memoize(timeout=3600)
def badge_list(site, can_view_patron_badges):

	badges = g.db.query(BadgeDef)

	if not can_view_patron_badges:
		badges = badges.filter(BadgeDef.id.notin_(patron_badges))

	badges = badges.order_by(BadgeDef.id).all()

	counts_raw = g.db.query(Badge.badge_id, func.count()).group_by(Badge.badge_id).all()
	users = g.db.query(User).count()

	counts = {}
	for c in counts_raw:
		counts[c[0]] = (c[1], float(c[1]) * 100 / max(users, 1))

	return badges, counts

@app.get("/badges")
@feature_required('BADGES')
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def badges(v):
	badges, counts = badge_list(SITE, v.admin_level >= PERMS['VIEW_PATRONS'])
	return render_template("badges.html", v=v, badges=badges, counts=counts)

@app.get("/blocks")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def blocks(v):
	blocks = g.db.query(UserBlock).options(
			joinedload(UserBlock.user),
			joinedload(UserBlock.target),
		).order_by(UserBlock.created_utc.desc())

	return render_template("blocks.html", v=v, blocks=blocks)

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
	return render_template("formatting.html", v=v, allowed_tags=allowed_tags, allowed_styles=allowed_styles)

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
	return "", 204

@app.get("/transfers/<int:id>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def transfers_id(id, v):

	transfer = g.db.get(Comment, id)

	if not transfer: abort(404)

	return render_template("transfers.html", v=v, page=1, comments=[transfer], standalone=True, total=1)

@app.get("/transfers")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def transfers(v):

	comments = g.db.query(Comment).filter(Comment.author_id == AUTOJANNY_ID, Comment.parent_post == None, Comment.body_html.like("%</a> has transferred %"))

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
	if v and (v.shadowbanned or v.chud == 1 or v.is_permabanned):
		abort(404)
	return render_template(f'donate.html', v=v)


@app.get("/orgy")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def orgy(v):
	return redirect("/chat")
