import os
from shutil import copyfile

from sqlalchemy import func
from sqlalchemy.sql.expression import nullslast
from files.helpers.media import *

import files.helpers.stats as statshelper
from files.classes.award import AWARDS
from files.classes.badges import Badge, BadgeDef
from files.classes.mod_logs import ModAction
from files.classes.userblock import UserBlock
from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.config.modaction_types import *
from files.routes.wrappers import *
from files.__main__ import app, cache, limiter


@app.get("/r/drama/comments/<int:id>/<title>")
@app.get("/r/Drama/comments/<int:id>/<title>")
@limiter.limit(DEFAULT_RATELIMIT)
def rdrama(id, title):
	id = ''.join(f'{x}/' for x in id)
	return redirect(f'/archives/drama/comments/{id}{title}.html')

@app.get("/r/<subreddit>")
@limiter.limit(DEFAULT_RATELIMIT)
@auth_desired
def subreddit(subreddit, v):
	reddit = v.reddit if v else "old.reddit.com"
	return redirect(f'https://{reddit}/r/{subreddit}')

@app.get("/reddit/<subreddit>/comments/<path:path>")
@app.get("/r/<subreddit>/comments/<path:path>")
@limiter.limit(DEFAULT_RATELIMIT)
@auth_desired
def reddit_post(subreddit, v, path):
	post_id = path.rsplit("/", 1)[0].replace('/', '')
	reddit = v.reddit if v else "old.reddit.com"
	return redirect(f'https://{reddit}/{post_id}')


@app.get("/marseys")
@app.get("/marseys/all")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def marseys(v:User):
	if SITE_NAME != 'rDrama' or not FEATURES['MARSEYS']:
		abort(404)

	marseys = g.db.query(Emoji, User).join(User, Emoji.author_id == User.id).filter(Emoji.kind == "Marsey", Emoji.submitter_id==None)

	next_exists = marseys.count()

	sort = request.values.get("sort")
	if sort == "author":
		marseys = marseys.order_by(User.username, Emoji.count.desc())
	elif sort == "name":
		marseys = marseys.order_by(Emoji.name, Emoji.count.desc())
	elif sort == "added_on":
		marseys = marseys.order_by(nullslast(Emoji.created_utc.desc()), Emoji.count.desc())
	else: # implied sort == "usage"
		marseys = marseys.order_by(Emoji.count.desc(), User.username)

	try: page = max(int(request.values.get("page", 1)), 1)
	except: page = 1

	if request.path != "/marseys/all":
		marseys = marseys.offset(PAGE_SIZE*(page-1)).limit(PAGE_SIZE)

	marseys = marseys.all()

	original = os.listdir("/asset_submissions/emojis/original")
	for marsey, user in marseys:
		for x in IMAGE_FORMATS:
			if f'{marsey.name}.{x}' in original:
				marsey.og = f'{marsey.name}.{x}'
				break

	return render_template("marseys.html", v=v, marseys=marseys, page=page, next_exists=next_exists, sort=sort)


@cache.cached(key_prefix="emojis")
def get_emojis():
	emojis = []
	for emoji, author in g.db.query(Emoji, User).join(User, Emoji.author_id == User.id).filter(Emoji.submitter_id == None).order_by(Emoji.count.desc()):
		emoji.author = author.username if FEATURES['ASSET_SUBMISSIONS'] else None
		emojis.append(emoji.json())
	return emojis

@app.get("/emojis")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def emoji_list(v):
	return get_emojis()



@app.get('/sidebar')
@limiter.limit(DEFAULT_RATELIMIT)
@auth_desired
def sidebar(v:Optional[User]):
	return render_template('sidebar.html', v=v)


@app.get("/stats")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def participation_stats(v:User):
	stats = cache.get('stats') or {}
	if v.client: return stats
	return render_template("stats.html", v=v, title="Content Statistics", data=stats)

@app.get("/chart")
@limiter.limit(DEFAULT_RATELIMIT)
def chart():
	return redirect('/weekly_chart')

@app.get("/weekly_chart")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def weekly_chart(v:User):
	return send_file(statshelper.chart_path(kind="weekly", site=SITE))

@app.get("/daily_chart")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def daily_chart(v:User):
	return send_file(statshelper.chart_path(kind="daily", site=SITE))

@app.get("/admin/patrons")
@app.get("/admin/paypigs")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['VIEW_PATRONS'])
def patrons(v):
	users = g.db.query(User).filter(User.patron > 0).order_by(User.patron.desc(), User.truescore.desc()).all()

	return render_template("admin/patrons.html", v=v, users=users, benefactor_def=AWARDS['benefactor'])

@app.get("/admins")
@app.get("/badmins")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def admins(v:User):
	admins = g.db.query(User).filter(User.admin_level >= PERMS['ADMIN_MOP_VISIBLE']).order_by(User.admin_level.desc(), User.truescore.desc()).all()
	return render_template("admins.html", v=v, admins=admins)

@app.get("/log")
@app.get("/modlog")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def log(v:User):

	try: page = max(int(request.values.get("page", 1)), 1)
	except: page = 1

	admin = request.values.get("admin")
	if admin: admin_id = get_id(admin)
	else: admin_id = 0

	kind = request.values.get("kind")

	if v.admin_level >= PERMS['USER_SHADOWBAN']:
		if v.admin_level >= PERMS['PROGSTACK']:
			types = MODACTION_TYPES
		else:
			types = MODACTION_TYPES__FILTERED
	else: types = MODACTION_TYPES_FILTERED

	if kind and kind not in types:
		kind = None
		actions = []
		next_exists = 0
	else:
		actions = g.db.query(ModAction)
		if v.admin_level < PERMS['USER_SHADOWBAN']:
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
		next_exists = actions.count()
		actions = actions.order_by(ModAction.id.desc()).offset(PAGE_SIZE*(page-1)).limit(PAGE_SIZE).all()

	admins = [x[0] for x in g.db.query(User.username).filter(User.admin_level >= PERMS['ADMIN_MOP_VISIBLE']).order_by(User.username).all()]

	return render_template("log.html", v=v, admins=admins, types=types, admin=admin, type=kind, actions=actions, next_exists=next_exists, page=page, single_user_url='admin')

@app.get("/log/<int:id>")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def log_item(id, v):
	try: id = int(id)
	except: abort(404)

	action=g.db.get(ModAction, id)

	if not action: abort(404)

	if action.kind in MODACTION_PRIVILEGED_TYPES and v.admin_level < PERMS['USER_SHADOWBAN']:
		abort(404)

	admins = [x[0] for x in g.db.query(User.username).filter(User.admin_level >= PERMS['ADMIN_MOP_VISIBLE']).all()]

	if v.admin_level >= PERMS['USER_SHADOWBAN']:
		if v.admin_level >= PERMS['PROGSTACK']:
			types = MODACTION_TYPES
		else:
			types = MODACTION_TYPES__FILTERED
	else: types = MODACTION_TYPES_FILTERED

	return render_template("log.html", v=v, actions=[action], next_exists=1, page=1, action=action, admins=admins, types=types, single_user_url='admin')

@app.get("/directory")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def static_megathread_index(v:User):
	if SITE_NAME != 'rDrama':
		abort(404)

	emojis_hash = cache.get('emojis_hash') or ''
	emojis_count = cache.get('emojis_count') or ''
	emojis_size = cache.get('emojis_size') or ''

	return render_template("megathread_index.html", v=v, emojis_hash=emojis_hash, emojis_count=emojis_count, emojis_size=emojis_size)

@app.get("/api")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def api(v):
	return render_template("api.html", v=v)

@app.get("/contact")
@app.get("/contactus")
@app.get("/contact_us")
@app.get("/press")
@app.get("/media")
@app.get("/admin/chat")
@limiter.limit(DEFAULT_RATELIMIT)
@auth_desired
def contact(v:Optional[User]):
	return render_template("contact.html", v=v, msg=get_msg())

@app.post("/contact")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("1/minute;10/day")
@limiter.limit("1/minute;10/day", key_func=get_ID)
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
						parent_submission=None,
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

	admin_ids = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS['NOTIFICATIONS_MODMAIL']).all()]

	for admin_id in admin_ids:
		notif = Notification(comment_id=new_comment.id, user_id=admin_id)
		g.db.add(notif)

	push_notif(admin_ids, f'New modmail from @{new_comment.author_name}', new_comment.body, f'{SITE_FULL}/notifications/modmail')

	return redirect("/contact?msg=Your message has been sent to the admins!")

@app.get('/archives')
@limiter.limit(DEFAULT_RATELIMIT)
def archivesindex():
	return redirect("/archives/index.html")

no = (21,22,23,24,25,26,27)

@cache.memoize(timeout=3600)
def badge_list(site):
	badges = g.db.query(BadgeDef).filter(BadgeDef.id.notin_(no)).order_by(BadgeDef.id).all()
	counts_raw = g.db.query(Badge.badge_id, func.count()).group_by(Badge.badge_id).all()
	users = g.db.query(User).count()

	counts = {}
	for c in counts_raw:
		counts[c[0]] = (c[1], float(c[1]) * 100 / max(users, 1))

	return badges, counts

@app.get("/badges")
@feature_required('BADGES')
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def badges(v:User):
	badges, counts = badge_list(SITE)
	return render_template("badges.html", v=v, badges=badges, counts=counts)

@app.get("/blocks")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['USER_BLOCKS_VISIBLE'])
def blocks(v):
	blocks=g.db.query(UserBlock).all()
	users = []
	targets = []
	for x in blocks:
		acc_user = get_account(x.user_id)
		acc_tgt = get_account(x.target_id)
		if acc_user.shadowbanned or acc_tgt.shadowbanned: continue
		users.append(acc_user)
		targets.append(acc_tgt)

	return render_template("blocks.html", v=v, users=users, targets=targets)

@app.get("/formatting")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def formatting(v:User):
	return render_template("formatting.html", v=v)

@app.get("/app")
@limiter.limit(DEFAULT_RATELIMIT)
@auth_desired
def mobile_app(v:Optional[User]):
	return render_template("app.html", v=v)

@app.post("/dismiss_mobile_tip")
@limiter.limit('1/second', scope=rpath)
@limiter.limit(DEFAULT_RATELIMIT)
def dismiss_mobile_tip():
	session["tooltip_last_dismissed"] = int(time.time())
	return "", 204

@app.get("/transfers/<int:id>")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def transfers_id(id, v):

	try: id = int(id)
	except: abort(404)

	transfer = g.db.get(Comment, id)

	if not transfer: abort(404)

	return render_template("transfers.html", v=v, page=1, comments=[transfer], standalone=True, next_exists=1)

@app.get("/transfers")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def transfers(v:User):

	comments = g.db.query(Comment).filter(Comment.author_id == AUTOJANNY_ID, Comment.parent_submission == None, Comment.body_html.like("%</a> has transferred %"))

	try: page = max(int(request.values.get("page", 1)), 1)
	except: page = 1

	next_exists = comments.count()
	comments = comments.order_by(Comment.id.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()

	if v.client:
		return {"data": [x.json(g.db) for x in comments]}
	else:
		return render_template("transfers.html", v=v, page=page, comments=comments, standalone=True, next_exists=next_exists)


@app.get('/donate')
@limiter.limit(DEFAULT_RATELIMIT)
@is_not_permabanned
def donate(v):
	if v.shadowbanned or v.agendaposter == 1: abort(404)
	return render_template(f'donate.html', v=v)
