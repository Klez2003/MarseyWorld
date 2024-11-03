from files.classes import *
from files.helpers.alerts import *
from files.helpers.get import *
from files.helpers.regex import *
from files.helpers.can_see import *
from files.helpers.useractions import badge_grant
from files.routes.wrappers import *

from .front import frontlist
from files.__main__ import app, cache, limiter

@app.post("/exile/post/<int:pid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def exile_post(v, pid):
	p = get_post(pid)
	hole = p.hole_obj
	if not hole: stop(400)

	if hole.public_use:
		stop(403, "You can't exile users while Public Use mode is enabled!")

	hole = hole.name

	if not v.mods_hole(hole): stop(403)

	u = p.author

	if u.mods_hole(hole): stop(403)

	if not u.exiler_username(hole):
		exile = Exile(user_id=u.id, hole=hole, exiler_id=v.id)
		g.db.add(exile)

		send_notification(u.id, f"@{v.username} has exiled you from /h/{hole} for {p.textlink}")

		ma = HoleAction(
			hole=hole,
			kind='exile_user',
			user_id=v.id,
			target_user_id=u.id,
			_note=f'for <a href="{p.permalink}">{p.title_html}</a>'
		)
		g.db.add(ma)

	return {"message": f"@{u.username} has been exiled from /h/{hole} successfully!"}

@app.post("/exile/comment/<int:cid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def exile_comment(v, cid):
	c = get_comment(cid)
	hole = c.post.hole_obj
	if not hole: stop(400)

	if hole.public_use:
		stop(403, "You can't exile users while Public Use mode is enabled!")

	hole = hole.name

	if not v.mods_hole(hole): stop(403)

	u = c.author

	if u.mods_hole(hole): stop(403)

	if not u.exiler_username(hole):
		exile = Exile(user_id=u.id, hole=hole, exiler_id=v.id)
		g.db.add(exile)

		send_notification(u.id, f"@{v.username} has exiled you from /h/{hole} for {c.textlink}")

		ma = HoleAction(
			hole=hole,
			kind='exile_user',
			user_id=v.id,
			target_user_id=u.id,
			_note=f'for <a href="/comment/{c.id}#context">comment</a>'
		)
		g.db.add(ma)

	return {"message": f"@{u.username} has been exiled from /h/{hole} successfully!"}

@app.post("/h/<hole>/unexile/<int:uid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def unexile(v, hole, uid):
	u = get_account(uid)

	if not v.mods_hole(hole): stop(403)

	if u.exiler_username(hole):
		exile = g.db.query(Exile).filter_by(user_id=u.id, hole=hole).one_or_none()
		g.db.delete(exile)

		send_notification(u.id, f"@{v.username} has revoked your exile from /h/{hole}")

		ma = HoleAction(
			hole=hole,
			kind='unexile_user',
			user_id=v.id,
			target_user_id=u.id
		)
		g.db.add(ma)

	return {"message": f"@{u.username} has been unexiled from /h/{hole} successfully!"}

@app.post("/h/<hole>/block")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def block_hole(v, hole):
	hole = get_hole(hole)

	if hole.public_use:
		stop(403, f"/h/{hole} has Public Use mode enabled and is unblockable!")

	hole = hole.name

	existing = g.db.query(HoleBlock).filter_by(user_id=v.id, hole=hole).one_or_none()
	if not existing:
		block = HoleBlock(user_id=v.id, hole=hole)
		g.db.add(block)
		cache.delete_memoized(frontlist)
	return {"message": f"/h/{hole} blocked successfully!"}

@app.post("/h/<hole>/unblock")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def unblock_hole(v, hole):
	hole = get_hole(hole)
	if not can_see(v, hole):
		stop(403)

	block = g.db.query(HoleBlock).filter_by(user_id=v.id, hole=hole.name).one_or_none()

	if block:
		g.db.delete(block)
		cache.delete_memoized(frontlist)

	return {"message": f"/h/{hole.name} unblocked successfully!"}

@app.post("/h/<hole>/subscribe")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def subscribe_hole(v, hole):
	hole = get_hole(hole).name
	existing = g.db.query(StealthHoleUnblock).filter_by(user_id=v.id, hole=hole).one_or_none()
	if not existing:
		subscribe = StealthHoleUnblock(user_id=v.id, hole=hole)
		g.db.add(subscribe)
		cache.delete_memoized(frontlist)
	return {"message": f"/h/{hole} unblocked successfully!"}

@app.post("/h/<hole>/unsubscribe")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def unsubscribe_hole(v, hole):
	hole = get_hole(hole).name
	subscribe = g.db.query(StealthHoleUnblock).filter_by(user_id=v.id, hole=hole).one_or_none()
	if subscribe:
		g.db.delete(subscribe)
		cache.delete_memoized(frontlist)
	return {"message": f"/h/{hole} blocked successfully!"}

@app.post("/h/<hole>/follow")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def follow_hole(v, hole):
	hole = get_hole(hole)
	if not can_see(v, hole):
		stop(403)
	existing = g.db.query(HoleFollow).filter_by(user_id=v.id, hole=hole.name).one_or_none()
	if not existing:
		subscription = HoleFollow(user_id=v.id, hole=hole.name)
		g.db.add(subscription)

	return {"message": f"/h/{hole} followed successfully!"}

@app.post("/h/<hole>/unfollow")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def unfollow_hole(v, hole):
	hole = get_hole(hole)
	subscription = g.db.query(HoleFollow).filter_by(user_id=v.id, hole=hole.name).one_or_none()
	if subscription:
		g.db.delete(subscription)

	return {"message": f"/h/{hole} unfollowed successfully!"}

@app.get("/h/<hole>/mods")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def mods_hole(v, hole):
	if hole == 'test':
		return redirect('/users')

	hole = get_hole(hole)
	if not can_see(v, hole):
		stop(403)
	users = g.db.query(User, Mod).join(Mod).filter_by(hole=hole.name).order_by(Mod.created_utc).all()

	return render_template("hole/mods.html", v=v, hole=hole, users=users)


@app.get("/h/<hole>/exilees")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def hole_exilees(v, hole):
	hole = get_hole(hole)
	if not can_see(v, hole):
		stop(403)
	users = g.db.query(User, Exile).join(Exile, Exile.user_id==User.id) \
				.filter_by(hole=hole.name) \
				.order_by(Exile.created_utc.desc(), User.username).all()

	return render_template("hole/exilees.html", v=v, hole=hole, users=users)


@app.get("/h/<hole>/blockers")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def hole_blockers(v, hole):
	hole = get_hole(hole)

	if not can_see(v, hole):
		stop(403)

	if hole.public_use:
		users = []
	else:
		users = g.db.query(User, HoleBlock).join(HoleBlock) \
					.filter_by(hole=hole.name) \
					.order_by(HoleBlock.created_utc.desc(), User.username).all()

	return render_template("hole/blockers.html",
		v=v, hole=hole, users=users, verb="blocking")


@app.get("/h/<hole>/followers")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def hole_followers(v, hole):
	hole = get_hole(hole)
	if not can_see(v, hole):
		stop(403)
	users = g.db.query(User, HoleFollow).join(HoleFollow) \
			.filter_by(hole=hole.name) \
			.order_by(HoleFollow.created_utc.desc(), User.username).all()

	return render_template("hole/blockers.html",
		v=v, hole=hole, users=users, verb="following")


@app.post("/h/<hole>/add_mod")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("30/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("30/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def add_mod(v, hole):
	if SITE_NAME == 'WPD': stop(403)

	if hole == 'test':
		stop(403, "Everyone is already a mod of this hole!")

	hole = get_hole(hole).name
	if not v.mods_hole(hole): stop(403)

	user = request.values.get('user')

	if not user: stop(400)

	user = get_user(user, v=v)

	if hole in {'furry','vampire','racist','femboy','edgy'} and not v.client and not user.house.lower().startswith(hole):
		stop(403, f"@{user.username} needs to be a member of House {hole.capitalize()} to be added as a mod there!")

	existing = g.db.query(Mod).filter_by(user_id=user.id, hole=hole).one_or_none()

	if not existing:
		mod = Mod(user_id=user.id, hole=hole)
		g.db.add(mod)

		if v.id != user.id:
			send_repeatable_notification(user.id, f"@{v.username} has added you as a mod to /h/{hole}")

		ma = HoleAction(
			hole=hole,
			kind='make_mod',
			user_id=v.id,
			target_user_id=user.id
		)
		g.db.add(ma)

	return {"message": "Mod added successfully!"}

@app.post("/h/<hole>/remove_mod")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def remove_mod(v, hole):
	hole = get_hole(hole).name

	if not v.mods_hole(hole): stop(403)

	uid = request.values.get('uid')

	if not uid: stop(400)

	try: uid = int(uid)
	except: stop(400)

	user = get_account(uid)

	if not user: stop(404)

	mod = g.db.query(Mod).filter_by(user_id=user.id, hole=hole).one_or_none()
	if not mod: stop(400)

	if not (v.id == user.id or v.mod_date(hole) and v.mod_date(hole) < mod.created_utc): stop(403)

	g.db.delete(mod)

	if v.id != user.id:
		send_repeatable_notification(user.id, f"@{v.username} has removed you as a mod from /h/{hole}")

	ma = HoleAction(
		hole=hole,
		kind='remove_mod',
		user_id=v.id,
		target_user_id=user.id
	)
	g.db.add(ma)

	return {"message": f"@{user.username} has been removed as a mod!"}

@app.post("/create_hole")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def create_hole(v):
	if not v.can_create_hole:
		stop(403)

	name = request.values.get('name')
	if not name: stop(400)
	name = name.strip().lower()

	if not hole_group_name_regex.fullmatch(name):
		stop(400, "Name does not match the required format!")

	charge_reason = f'Cost of creating <a href="/h/{name}">/h/{name}</a>'
	if not v.charge_account('coins/marseybux', HOLE_COST, charge_reason):
		stop(400, "You don't have enough coins or marseybux!")

	hole = get_hole(name, graceful=True)

	if hole:
		stop(400, f"/h/{hole} already exists!")

	g.db.add(v)
	if v.shadowbanned: stop(500)

	hole = Hole(name=name)
	g.db.add(hole)
	g.db.flush() #Necessary, following statement errors out otherwise
	mod = Mod(user_id=v.id, hole=hole.name)
	g.db.add(mod)

	text = f":!marseyparty: /h/{hole} has been created by @{v.username} :marseyparty:"
	alert_active_users(text, v.id, User.hole_creation_notifs == True)

	return redirect(f"/h/{hole}")

@app.get('/h/<hole>/settings')
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def hole_settings(v, hole):
	hole = get_hole(hole)
	return render_template('hole/settings.html', v=v, sidebar=hole.sidebar, hole=hole, css=hole.css, snappy_quotes=hole.snappy_quotes)


@app.post('/h/<hole>/sidebar')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def post_hole_sidebar(v, hole):
	hole = get_hole(hole)
	if not v.mods_hole(hole.name): stop(403)
	if v.shadowbanned: stop(400)

	sidebar = request.values.get('sidebar', '').strip()

	if len(sidebar) > 10000:
		stop(400, "New sidebar is too long (max 10000 characters)")

	sidebar_html = sanitize(sidebar, blackjack=f"/h/{hole} sidebar")

	if len(sidebar_html) > 20000:
		stop(400, "New rendered sidebar is too long!")

	hole.sidebar = sidebar
	hole.sidebar_html = sidebar_html
	g.db.add(hole)

	ma = HoleAction(
		hole=hole.name,
		kind='edit_sidebar',
		user_id=v.id
	)
	g.db.add(ma)

	return {"message": "Sidebar changed successfully!"}


@app.post('/h/<hole>/css')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def post_hole_css(v, hole):
	hole = get_hole(hole)
	css = request.values.get('css', '').strip()

	if not hole: stop(404)
	if not v.mods_hole(hole.name): stop(403)
	if v.shadowbanned: stop(400)

	if len(css) > CSS_LENGTH_LIMIT:
		stop(400, f"Hole CSS is too long (max {CSS_LENGTH_LIMIT} characters)")

	valid, error = validate_css(css)
	if not valid:
		stop(400, error)

	hole.css = css
	g.db.add(hole)

	ma = HoleAction(
		hole=hole.name,
		kind='edit_css',
		user_id=v.id
	)
	g.db.add(ma)

	return {"message": "CSS edited successfully!"}

@app.get("/h/<hole>/css")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
def get_hole_css(hole):
	hole = g.db.query(Hole.css).filter_by(name=hole.strip().lower()).one_or_none()
	if not hole: stop(404)
	resp = make_response(hole.css or "")
	resp.headers.add("Content-Type", "text/css")
	return resp

@app.post("/h/<hole>/settings/sidebars")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("50/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("50/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def upload_hole_sidebar(v, hole):
	if g.is_tor: stop(403, "File uploads are not allowed through TOR")

	hole = get_hole(hole)
	if not v.mods_hole(hole.name): stop(403)
	if v.shadowbanned: stop(500)

	file = request.files["image"]

	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	sidebarurl = process_image(name, v, resize=600)

	hole.sidebarurls.append(sidebarurl)

	g.db.add(hole)

	ma = HoleAction(
		hole=hole.name,
		kind='upload_sidebar_image',
		_note=f'<a href="{sidebarurl}">{sidebarurl}</a>',
		user_id=v.id
	)
	g.db.add(ma)

	return {"message": "Sidebar image uploaded successfully!", "url": sidebarurl}

@app.post("/h/<hole>/settings/sidebars/delete")
@limiter.limit("1/second", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("1/second", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def delete_hole_sidebar(v, hole):
	hole = get_hole(hole)
	if not v.mods_hole(hole.name): stop(403)

	if not hole.sidebarurls:
		stop(404, f"Sidebar image not found (/h/{hole.name} has no sidebar images)")

	sidebar = request.values["url"]
	
	if sidebar not in hole.sidebarurls:
		stop(404, "Sidebar image not found!")

	remove_image_using_link(sidebar)

	hole.sidebarurls.remove(sidebar)
	g.db.add(hole)

	ma = HoleAction(
		hole=hole.name,
		kind='delete_sidebar_image',
		_note=f'<a href="{sidebar}">{sidebar}</a>',
		user_id=v.id
	)
	g.db.add(ma)

	return {"message": "Sidebar image deleted successfully!"}

@app.post("/h/<hole>/settings/banners")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("50/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("50/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def upload_hole_banner(v, hole):
	if g.is_tor: stop(403, "File uploads are not allowed through TOR")

	hole = get_hole(hole)
	if not v.mods_hole(hole.name): stop(403)
	if v.shadowbanned: stop(500)

	file = request.files["image"]

	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	bannerurl = process_image(name, v, resize=2000)

	hole.bannerurls.append(bannerurl)

	g.db.add(hole)

	ma = HoleAction(
		hole=hole.name,
		kind='upload_banner',
		_note=f'<a href="{bannerurl}">{bannerurl}</a>',
		user_id=v.id
	)
	g.db.add(ma)

	return {"message": "Banner uploaded successfully!", "url": bannerurl}

@app.post("/h/<hole>/settings/banners/delete")
@limiter.limit("1/second", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("1/second", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def delete_hole_banner(v, hole):
	hole = get_hole(hole)
	if not v.mods_hole(hole.name): stop(403)

	if not hole.bannerurls:
		stop(404, f"Banner not found (/h/{hole.name} has no banner images)")

	banner = request.values["url"]
	
	if banner not in hole.bannerurls:
		stop(404, "Banner not found!")

	remove_image_using_link(banner)

	hole.bannerurls.remove(banner)
	g.db.add(hole)

	ma = HoleAction(
		hole=hole.name,
		kind='delete_banner',
		_note=f'<a href="{banner}">{banner}</a>',
		user_id=v.id
	)
	g.db.add(ma)

	return {"message": "Banner deleted successfully!"}

@app.post("/h/<hole>/marsey_image")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("5/minute;50/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("5/minute;50/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def hole_marsey(v, hole):
	if g.is_tor: stop(403, "File uploads are not allowed through TOR!")

	hole = get_hole(hole)
	if not v.mods_hole(hole.name): stop(403)
	if v.shadowbanned: stop(500)

	file = request.files["marsey"]
	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	marseyurl = process_image(name, v, resize=200)

	if marseyurl:
		remove_image_using_link(hole.marseyurl)
		hole.marseyurl = marseyurl
		g.db.add(hole)

	ma = HoleAction(
		hole=hole.name,
		kind='change_marsey',
		_note=f'<a href="{hole.marseyurl}">{hole.marseyurl}</a>',
		user_id=v.id
	)
	g.db.add(ma)

	return redirect(f'/h/{hole}/settings')

@app.get("/holes")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def holes(v):
	holes = g.db.query(Hole, func.count(Post.hole)).outerjoin(Post, Hole.name == Post.hole).group_by(Hole.name)
	alive = holes.filter(Hole.dead_utc == None).order_by(Hole.created_utc).all()
	dead = holes.filter(Hole.dead_utc != None).order_by(Hole.dead_utc).all()
	total_users = g.db.query(User).count()
	return render_template('hole/holes.html', v=v, alive=alive, dead=dead, total_users=total_users)

@app.post("/hole_pin/<int:pid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def hole_pin(v, pid):
	p = get_post(pid)

	if not p.hole: stop(403)

	if not v.mods_hole(p.hole): stop(403)

	num = g.db.query(Post).filter(Post.hole == p.hole, Post.hole_pinned != None).count()
	if num >= 2:
		stop(403, f"You can only pin 2 posts to /h/{p.hole}")

	p.hole_pinned = v.username
	g.db.add(p)

	if v.id != p.author_id:
		message = f"@{v.username} (a /h/{p.hole} mod) has pinned {p.textlink} in /h/{p.hole}"
		send_repeatable_notification(p.author_id, message)

	ma = HoleAction(
		hole=p.hole,
		kind='pin_post',
		user_id=v.id,
		target_post_id=p.id
	)
	g.db.add(ma)

	cache.delete_memoized(frontlist)

	return {"message": f"Post pinned to /h/{p.hole} successfully!"}

@app.post("/hole_unpin/<int:pid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def hole_unpin(v, pid):
	p = get_post(pid)

	if not p.hole: stop(403)

	if not v.mods_hole(p.hole): stop(403)

	p.hole_pinned = None
	g.db.add(p)

	if v.id != p.author_id:
		message = f"@{v.username} (a /h/{p.hole} mod) has unpinned {p.textlink} in /h/{p.hole}"
		send_repeatable_notification(p.author_id, message)

	ma = HoleAction(
		hole=p.hole,
		kind='unpin_post',
		user_id=v.id,
		target_post_id=p.id
	)
	g.db.add(ma)

	cache.delete_memoized(frontlist)

	return {"message": f"Post unpinned from /h/{p.hole} successfully!"}


@app.post('/h/<hole>/stealth')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def hole_stealth(v, hole):
	hole = get_hole(hole)
	if hole.name in {'mnn','glory','racist'} and v.admin_level < PERMS["MODS_EVERY_HOLE"]:
		stop(403)
	if not v.mods_hole(hole.name): stop(403)

	hole.stealth = not hole.stealth
	g.db.add(hole)

	cache.delete_memoized(frontlist)

	if hole.stealth:
		ma = HoleAction(
			hole=hole.name,
			kind='enable_stealth',
			user_id=v.id
		)
		g.db.add(ma)
		return {"message": f"Stealth mode has been enabled for /h/{hole} successfully!"}
	else:
		ma = HoleAction(
			hole=hole.name,
			kind='disable_stealth',
			user_id=v.id
		)
		g.db.add(ma)
		return {"message": f"Stealth mode has been disabled for /h/{hole} successfully!"}

@app.post('/h/<hole>/public_use')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def hole_public_use(v, hole):
	hole = get_hole(hole)

	if not v.mods_hole(hole.name): stop(403)

	if hole in {'furry','vampire','racist','femboy','edgy'}:
		stop(400, "House holes can't have Public Use mode enabled.")

	hole.public_use = not hole.public_use
	g.db.add(hole)

	exiles = g.db.query(Exile).filter_by(hole=hole.name)
	for exile in exiles:
		send_repeatable_notification(exile.user_id, f"Your exile from /h/{exile.hole} has been revoked due to its jannies enabling Public Use mode!")
		g.db.delete(exile)

	if hole.public_use:
		ma = HoleAction(
			hole=hole.name,
			kind='enable_public_use',
			user_id=v.id
		)
		g.db.add(ma)
		return {"message": f"Public Use mode has been enabled for /h/{hole} successfully!"}
	else:
		ma = HoleAction(
			hole=hole.name,
			kind='disable_public_use',
			user_id=v.id
		)
		g.db.add(ma)
		return {"message": f"Public Use mode has been disabled for /h/{hole} successfully!"}

@app.post("/pin_comment_mod/<int:cid>")
@feature_required('PINS')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def pin_comment_mod(cid, v):

	comment = get_comment(cid, v=v)

	if not comment.pinned:
		if not v.mods_hole(comment.post.hole): stop(403)

		comment.pinned = v.username + " (Mod)"

		g.db.add(comment)

		comment.pin_parents()

		ma = HoleAction(
			hole=comment.post.hole,
			kind="pin_comment",
			user_id=v.id,
			target_comment_id=comment.id
		)
		g.db.add(ma)

		if v.id != comment.author_id:
			message = f"@{v.username} (a /h/{comment.post.hole} mod) has pinned {comment.textlink}"
			send_repeatable_notification(comment.author_id, message)

	return {"message": "Comment pinned!"}

@app.post("/unpin_comment_mod/<int:cid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def unpin_comment_mod(cid, v):

	comment = get_comment(cid, v=v)

	if comment.pinned:
		if not v.mods_hole(comment.post.hole): stop(403)

		comment.pinned = None
		comment.pinned_utc = None
		g.db.add(comment)

		comment.unpin_parents()

		ma = HoleAction(
			hole=comment.post.hole,
			kind="unpin_comment",
			user_id=v.id,
			target_comment_id=comment.id
		)
		g.db.add(ma)

		if v.id != comment.author_id:
			message = f"@{v.username} (a /h/{comment.post.hole} mod) has unpinned {comment.textlink}"
			send_repeatable_notification(comment.author_id, message)
	return {"message": "Comment unpinned!"}


@app.get("/h/<hole>/log")
@app.get("/h/<hole>/modlog")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def hole_log(v, hole):
	hole = get_hole(hole)
	if not can_see(v, hole):
		stop(403)
	page = get_page()

	mod = request.values.get("mod")
	if mod: mod_id = get_user(mod, attributes=[User.id]).id
	else: mod_id = 0

	kind = request.values.get("kind")

	kinds = HOLEACTION_KINDS

	if kind and kind not in kinds:
		kind = None
		actions = []
		total=0
	else:
		actions = g.db.query(HoleAction).filter_by(hole=hole.name)

		if mod_id:
			actions = actions.filter_by(user_id=mod_id)
			new_kinds = {x.kind for x in actions}
			if kind: new_kinds.add(kind)
			kinds2 = {}
			for k,val in kinds.items():
				if k in new_kinds: kinds2[k] = val
			kinds = kinds2
		if kind: actions = actions.filter_by(kind=kind)
		total = actions.count()
		actions = actions.order_by(HoleAction.id.desc()).offset(PAGE_SIZE*(page-1)).limit(PAGE_SIZE).all()

	mods = [x[0] for x in g.db.query(Mod.user_id).filter_by(hole=hole.name)]
	mods = [x[0] for x in g.db.query(User.username).filter(User.id.in_(mods)).order_by(User.username)]

	return render_template("log.html", v=v, admins=mods, kinds=kinds, admin=mod, kind=kind, actions=actions, total=total, page=page, hole=hole, single_user_url='mod')

@app.get("/h/<hole>/log/<int:id>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def hole_log_item(id, v, hole):
	hole = get_hole(hole)
	if not can_see(v, hole):
		stop(403)

	action = g.db.get(HoleAction, id)

	if not action: stop(404)

	mods = [x[0] for x in g.db.query(Mod.user_id).filter_by(hole=hole.name)]
	mods = [x[0] for x in g.db.query(User.username).filter(User.id.in_(mods)).order_by(User.username)]

	kinds = HOLEACTION_KINDS

	return render_template("log.html", v=v, actions=[action], total=1, page=1, action=action, admins=mods, kinds=kinds, hole=hole, single_user_url='mod')

@app.post('/h/<hole>/snappy_quotes')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def post_hole_snappy_quotes(v, hole):
	hole = get_hole(hole)
	snappy_quotes = request.values.get('snappy_quotes', '').strip()

	if not hole: stop(404)
	if not v.mods_hole(hole.name): stop(403)
	if v.shadowbanned: stop(400)

	if snappy_quotes.endswith('[para]'):
		snappy_quotes = snappy_quotes[:-6].strip()

	if len(snappy_quotes) > HOLE_SNAPPY_QUOTES_LENGTH:
		stop(400, f"Quotes are too long (max {HOLE_SNAPPY_QUOTES_LENGTH} characters)")

	hole.snappy_quotes = snappy_quotes
	g.db.add(hole)

	ma = HoleAction(
		hole=hole.name,
		kind='edit_snappy_quotes',
		user_id=v.id
	)
	g.db.add(ma)

	return {"message": "Snappy quotes edited successfully!"}


@app.post("/change_hole/<int:pid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def change_hole(pid, v):
	post = get_post(pid)

	if post.ghost:
		stop(403, "You can't move ghost posts into holes!")

	hole_from = post.hole

	hole_to = request.values.get("hole_to", "").strip()
	if hole_to:
		hole_to = get_hole(hole_to)

		if hole_to.dead_utc:
			stop(400, f'/h/{hole_to} is dead. You can resurrect it at a cost if you wish.')
		
		hole_to = hole_to.name
	else:
		hole_to = None

	if not post.hole_changable(v):
		stop(403, "You can't change the hole of this post!")

	if hole_to == None:
		if HOLE_REQUIRED:
			stop(403, "All posts are required to be in holes!")
		hole_to_in_notif = 'the main feed'
	else:
		hole_to_in_notif = f'/h/{hole_to}'

	if hole_from == hole_to:
		stop(409, f"Post is already in {hole_to_in_notif}")

	if post.author.exiler_username(hole_to):
		stop(403, f"User is exiled from this hole!")

	if hole_to == 'changelog':
		stop(403, "/h/changelog is archived!")

	if hole_to in {'furry','vampire','racist','femboy','edgy'} and not v.client and not post.author.house.lower().startswith(hole_to):
		if v.id == post.author_id:
			stop(403, f"You need to be a member of House {hole_to.capitalize()} to post in /h/{hole_to}")
		else:
			stop(403, f"@{post.author_name} needs to be a member of House {hole_to.capitalize()} for their post to be moved to /h/{hole_to}")

	post.hole = hole_to
	post.hole_pinned = None

	if hole_to == 'chudrama':
		post.bannedfor = None
		post.chuddedfor = None
		for c in post.comments:
			c.bannedfor = None
			c.chuddedfor = None
			g.db.add(c)

	g.db.add(post)

	if v.id != post.author_id:
		hole_from_str = 'main feed' if hole_from is None else \
			f'<a href="/h/{hole_from}">/h/{hole_from}</a>'
		hole_to_str = 'main feed' if hole_to is None else \
			f'<a href="/h/{hole_to}">/h/{hole_to}</a>'

		if v.admin_level >= PERMS['POST_COMMENT_MODERATION']:
			ma = ModAction(
				kind='change_hole',
				user_id=v.id,
				target_post_id=post.id,
				_note=f'{hole_from_str} → {hole_to_str}',
			)
			g.db.add(ma)
			position = 'a site admin'
		else:
			ma = HoleAction(
				hole=hole_from,
				kind='change_hole',
				user_id=v.id,
				target_post_id=post.id,
				_note=f'{hole_from_str} → {hole_to_str}',
			)
			g.db.add(ma)
			position = f'a /h/{hole_from} mod'

		if hole_from == None:
			hole_from_in_notif = 'the main feed'
		else:
			hole_from_in_notif = f'/h/{hole_from}'

		message = f"@{v.username} ({position}) has moved {post.textlink} from {hole_from_in_notif} to {hole_to_in_notif}"
		send_repeatable_notification(post.author_id, message)

	cache.delete_memoized(frontlist)

	return {"message": f"Post moved to {hole_to_in_notif} successfully!"}

@app.post('/h/<hole>/resurrect')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def resurrect_hole(v, hole):
	hole = get_hole(hole)

	if not hole: stop(404)
	if not hole.dead_utc: stop(400, "This hole is not dead!")
	if v.shadowbanned: stop(400)

	charge_reason = f'Cost of resurrecting <a href="/h/{hole}">/h/{hole}</a>'
	if not v.charge_account('coins/marseybux', HOLE_COST, charge_reason):
		stop(400, "You don't have enough coins or marseybux!")

	hole.dead_utc = None
	g.db.add(hole)

	ma = HoleAction(
		hole=hole.name,
		kind='resurrect_hole',
		user_id=v.id
	)
	g.db.add(ma)

	mod = Mod(user_id=v.id, hole=hole.name)
	g.db.add(mod)

	badge_grant(badge_id=351, user=v, description=f'Resurrected a hole (/h/{hole})')

	text = f':marseyrises: /h/{hole} has been resurrected by @{v.username}'
	alert_active_users(text, v.id, User.hole_creation_notifs == True)

	return {"message": f"/h/{hole} resurrected successfully!"}
