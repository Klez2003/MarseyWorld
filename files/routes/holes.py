from files.classes import *
from files.helpers.alerts import *
from files.helpers.get import *
from files.helpers.regex import *
from files.helpers.can_see import *
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
	hole = p.hole
	if not hole: abort(400)

	if not v.mods(hole): abort(403)

	u = p.author

	if u.mods(hole): abort(403)

	if not u.exiler_username(hole):
		exile = Exile(user_id=u.id, hole=hole, exiler_id=v.id)
		g.db.add(exile)

		send_notification(u.id, f"@{v.username} has exiled you from /h/{hole} for [{p.title}]({p.shortlink})")

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
	hole = c.post.hole
	if not hole: abort(400)

	if not v.mods(hole): abort(403)

	u = c.author

	if u.mods(hole): abort(403)

	if not u.exiler_username(hole):
		exile = Exile(user_id=u.id, hole=hole, exiler_id=v.id)
		g.db.add(exile)

		send_notification(u.id, f"@{v.username} has exiled you from /h/{hole} for [{c.permalink}]({c.shortlink})")

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

	if not v.mods(hole): abort(403)

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
def block_sub(v, hole):
	hole = get_hole(hole).name
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
def unblock_sub(v, hole):
	hole = get_hole(hole)
	if not can_see(v, hole):
		abort(403)

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
def subscribe_sub(v, hole):
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
def unsubscribe_sub(v, hole):
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
def follow_sub(v, hole):
	hole = get_hole(hole)
	if not can_see(v, hole):
		abort(403)
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
def unfollow_sub(v, hole):
	hole = get_hole(hole)
	subscription = g.db.query(HoleFollow).filter_by(user_id=v.id, hole=hole.name).one_or_none()
	if subscription:
		g.db.delete(subscription)

	return {"message": f"/h/{hole} unfollowed successfully!"}

@app.get("/h/<hole>/mods")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def mods(v, hole):
	if hole == 'test':
		return redirect('/users')

	hole = get_hole(hole)
	if not can_see(v, hole):
		abort(403)
	users = g.db.query(User, Mod).join(Mod).filter_by(hole=hole.name).order_by(Mod.created_utc).all()

	return render_template("hole/mods.html", v=v, hole=hole, users=users)


@app.get("/h/<hole>/exilees")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def hole_exilees(v, hole):
	hole = get_hole(hole)
	if not can_see(v, hole):
		abort(403)
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
		abort(403)
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
		abort(403)
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
	if SITE_NAME == 'WPD': abort(403)

	if hole == 'test':
		abort(403, "Everyone is already a mod of this hole!")

	hole = get_hole(hole).name
	if not v.mods(hole): abort(403)

	user = request.values.get('user')

	if not user: abort(400)

	user = get_user(user, v=v)

	if hole in {'furry','vampire','racist','femboy','edgy'} and not v.client and not user.house.lower().startswith(hole):
		abort(403, f"@{user.username} needs to be a member of House {hole.capitalize()} to be added as a mod there!")

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

	if not v.mods(hole): abort(403)

	uid = request.values.get('uid')

	if not uid: abort(400)

	try: uid = int(uid)
	except: abort(400)

	user = get_account(uid)

	if not user: abort(404)

	mod = g.db.query(Mod).filter_by(user_id=user.id, hole=hole).one_or_none()
	if not mod: abort(400)

	if not (v.id == user.id or v.mod_date(hole) and v.mod_date(hole) < mod.created_utc): abort(403)

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

@app.get("/create_hole")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def create_sub(v):
	if not v.can_create_hole:
		abort(403)

	return render_template("hole/create_hole.html", v=v, cost=HOLE_COST)

@app.post("/create_hole")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def create_sub2(v):
	if not v.can_create_hole:
		abort(403)

	name = request.values.get('name')
	if not name: abort(400)
	name = name.strip().lower()

	if not hole_group_name_regex.fullmatch(name):
		abort(400, "Name does not match the required format!")

	if not v.charge_account('combined', HOLE_COST)[0]:
		abort(400, "You don't have enough coins or marseybux!")

	hole = get_hole(name, graceful=True)

	if hole:
		abort(400, f"/h/{hole} already exists!")

	g.db.add(v)
	if v.shadowbanned: abort(500)

	hole = Hole(name=name)
	g.db.add(hole)
	g.db.flush() #Necessary, following statement errors out otherwise
	mod = Mod(user_id=v.id, hole=hole.name)
	g.db.add(mod)

	admins = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS['NOTIFICATIONS_HOLE_CREATION'], User.id != v.id)]
	for admin in admins:
		send_repeatable_notification(admin, f":!marseyparty: /h/{hole} has been created by @{v.username} :marseyparty:")

	return redirect(f"/h/{hole}")

@app.post("/kick/<int:pid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def kick(v, pid):
	post = get_post(pid)

	if not post.hole: abort(403)
	if not v.mods(post.hole): abort(403)

	old = post.hole
	post.hole = None
	post.hole_pinned = None

	ma = HoleAction(
		hole=old,
		kind='kick_post',
		user_id=v.id,
		target_post_id=post.id
	)
	g.db.add(ma)

	if v.id != post.author_id:
		message = f"@{v.username} (a /h/{old} mod) has moved [{post.title}]({post.shortlink}) from /h/{old} to the main feed!"
		send_repeatable_notification(post.author_id, message)

	g.db.add(post)

	cache.delete_memoized(frontlist)

	return {"message": f"Post kicked from /h/{old} successfully!"}

@app.get('/h/<hole>/settings')
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def hole_settings(v, hole):
	hole = get_hole(hole)
	if not v.mods(hole.name): abort(403)
	return render_template('hole/settings.html', v=v, sidebar=hole.sidebar, hole=hole, css=hole.css)


@app.post('/h/<hole>/sidebar')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def post_hole_sidebar(v, hole):
	hole = get_hole(hole)
	if not v.mods(hole.name): abort(403)
	if v.shadowbanned: abort(400)

	hole.sidebar = request.values.get('sidebar', '')[:10000].strip()
	sidebar_html = sanitize(hole.sidebar, blackjack=f"/h/{hole} sidebar")

	if len(sidebar_html) > 20000:
		abort(400, "Sidebar is too big! (max 20000 characters)")

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

	if not hole: abort(404)
	if not v.mods(hole.name): abort(403)
	if v.shadowbanned: abort(400)

	if len(css) > 6000:
		abort(400, "CSS is too long (max 6000 characters)")

	valid, error = validate_css(css)
	if not valid:
		abort(400, error)

	hole.css = css
	g.db.add(hole)

	ma = HoleAction(
		hole=hole.name,
		kind='edit_css',
		user_id=v.id
	)
	g.db.add(ma)

	return {"message": "CSS changed successfully!"}

@app.get("/h/<hole>/css")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
def get_hole_css(hole):
	hole = g.db.query(Hole.css).filter_by(name=hole.strip().lower()).one_or_none()
	if not hole: abort(404)
	resp = make_response(hole.css or "")
	resp.headers.add("Content-Type", "text/css")
	return resp

@app.post("/h/<hole>/settings/sidebars/")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("50/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("50/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def upload_hole_sidebar(v, hole):
	if g.is_tor: abort(403, "Image uploads are not allowed through Tor")

	hole = get_hole(hole)
	if not v.mods(hole.name): abort(403)
	if v.shadowbanned: abort(500)

	file = request.files["sidebar"]

	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	sidebarurl = process_image(name, v, resize=400)

	hole.sidebarurls.append(sidebarurl)

	g.db.add(hole)

	ma = HoleAction(
		hole=hole.name,
		kind='upload_sidebar_image',
		user_id=v.id
	)
	g.db.add(ma)

	return redirect(f'/h/{hole}/settings')

@app.post("/h/<hole>/settings/sidebars/delete/<int:index>")
@limiter.limit("1/second", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("1/second", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def delete_hole_sidebar(v, hole, index):
	hole = get_hole(hole)
	if not v.mods(hole.name): abort(403)

	if not hole.sidebarurls:
		abort(404, f"Sidebar image not found (/h/{hole.name} has no sidebar images)")
	if index < 0 or index >= len(hole.sidebarurls):
		abort(404, f'Sidebar image not found (sidebar index {index} is not between 0 and {len(hole.sidebarurls)})')
	sidebar = hole.sidebarurls[index]
	try:
		remove_media_using_link(sidebar)
	except FileNotFoundError:
		pass
	del hole.sidebarurls[index]
	g.db.add(hole)

	ma = HoleAction(
		hole=hole.name,
		kind='delete_sidebar_image',
		_note=index,
		user_id=v.id
	)
	g.db.add(ma)

	return {"message": f"Deleted sidebar {index} from /h/{hole} successfully"}

@app.post("/h/<hole>/settings/sidebars/delete_all")
@limiter.limit("1/10 second;30/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("1/10 second;30/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def delete_all_hole_sidebars(v, hole):
	hole = get_hole(hole)
	if not v.mods(hole.name): abort(403)

	for sidebar in hole.sidebarurls:
		try:
			remove_media_using_link(sidebar)
		except FileNotFoundError:
			pass
	hole.sidebarurls = []
	g.db.add(hole)

	ma = HoleAction(
		hole=hole.name,
		kind='delete_sidebar_image',
		_note='all',
		user_id=v.id
	)
	g.db.add(ma)

	return {"message": f"Deleted all sidebar images from /h/{hole} successfully"}

@app.post("/h/<hole>/settings/banners/")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("50/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("50/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def upload_hole_banner(v, hole):
	if g.is_tor: abort(403, "Image uploads are not allowed through Tor")

	hole = get_hole(hole)
	if not v.mods(hole.name): abort(403)
	if v.shadowbanned: abort(500)

	file = request.files["banner"]

	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	bannerurl = process_image(name, v, resize=1600)

	hole.bannerurls.append(bannerurl)

	g.db.add(hole)

	ma = HoleAction(
		hole=hole.name,
		kind='upload_banner',
		user_id=v.id
	)
	g.db.add(ma)

	return redirect(f'/h/{hole}/settings')

@app.post("/h/<hole>/settings/banners/delete/<int:index>")
@limiter.limit("1/second", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("1/second", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def delete_hole_banner(v, hole, index):
	hole = get_hole(hole)
	if not v.mods(hole.name): abort(403)

	if not hole.bannerurls:
		abort(404, f"Banner not found (/h/{hole.name} has no banners)")
	if index < 0 or index >= len(hole.bannerurls):
		abort(404, f'Banner not found (banner index {index} is not between 0 and {len(hole.bannerurls)})')
	banner = hole.bannerurls[index]
	try:
		remove_media_using_link(banner)
	except FileNotFoundError:
		pass
	del hole.bannerurls[index]
	g.db.add(hole)

	ma = HoleAction(
		hole=hole.name,
		kind='delete_banner',
		_note=index,
		user_id=v.id
	)
	g.db.add(ma)

	return {"message": f"Deleted banner {index} from /h/{hole} successfully"}

@app.post("/h/<hole>/settings/banners/delete_all")
@limiter.limit("1/10 second;30/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("1/10 second;30/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def delete_all_hole_banners(v, hole):
	hole = get_hole(hole)
	if not v.mods(hole.name): abort(403)

	for banner in hole.bannerurls:
		try:
			remove_media_using_link(banner)
		except FileNotFoundError:
			pass
	hole.bannerurls = []
	g.db.add(hole)

	ma = HoleAction(
		hole=hole.name,
		kind='delete_banner',
		_note='all',
		user_id=v.id
	)
	g.db.add(ma)

	return {"message": f"Deleted all banners from /h/{hole} successfully"}

@app.post("/h/<hole>/marsey_image")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("10/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("10/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def hole_marsey(v, hole):
	if g.is_tor: abort(403, "Image uploads are not allowed through TOR!")

	hole = get_hole(hole)
	if not v.mods(hole.name): abort(403)
	if v.shadowbanned: abort(500)

	file = request.files["marsey"]
	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	marseyurl = process_image(name, v, resize=200)

	if marseyurl:
		if hole.marseyurl:
			remove_media_using_link(hole.marseyurl)
		hole.marseyurl = marseyurl
		g.db.add(hole)

	ma = HoleAction(
		hole=hole.name,
		kind='change_marsey',
		user_id=v.id
	)
	g.db.add(ma)

	return redirect(f'/h/{hole}/settings')

@app.get("/flairs")
@app.get("/holes")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def subs(v):
	subs = g.db.query(Hole, func.count(Post.hole)).outerjoin(Post, Hole.name == Post.hole).group_by(Hole.name).order_by(func.count(Post.hole).desc()).all()
	total_users = g.db.query(User).count()
	return render_template('hole/holes.html', v=v, subs=subs, total_users=total_users)

@app.post("/hole_pin/<int:pid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def hole_pin(v, pid):
	p = get_post(pid)

	if not p.hole: abort(403)

	if not v.mods(p.hole): abort(403)

	num = g.db.query(Post).filter(Post.hole == p.hole, Post.hole_pinned != None).count()
	if num >= 2:
		abort(403, f"You can only pin 2 posts to /h/{p.hole}")

	p.hole_pinned = v.username
	g.db.add(p)

	if v.id != p.author_id:
		message = f"@{v.username} (a /h/{p.hole} mod) has pinned [{p.title}]({p.shortlink}) in /h/{p.hole}"
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

	if not p.hole: abort(403)

	if not v.mods(p.hole): abort(403)

	p.hole_pinned = None
	g.db.add(p)

	if v.id != p.author_id:
		message = f"@{v.username} (a /h/{p.hole} mod) has unpinned [{p.title}]({p.shortlink}) in /h/{p.hole}"
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
	if hole.name in {'braincels','smuggies','mnn','glory'} and v.admin_level < PERMS["MODS_EVERY_HOLE"]:
		abort(403)
	if not v.mods(hole.name): abort(403)

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


@app.post("/pin_comment_mod/<int:cid>")
@feature_required('PINS')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def pin_comment_mod(cid, v):

	comment = get_comment(cid, v=v)

	if not comment.stickied:
		if not (comment.post.hole and v.mods(comment.post.hole)): abort(403)

		comment.stickied = v.username + " (Mod)"

		g.db.add(comment)

		ma = HoleAction(
			hole=comment.post.hole,
			kind="pin_comment",
			user_id=v.id,
			target_comment_id=comment.id
		)
		g.db.add(ma)

		if v.id != comment.author_id:
			message = f"@{v.username} (a /h/{comment.post.hole} mod) has pinned your [comment]({comment.shortlink})"
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

	if comment.stickied:
		if not (comment.post.hole and v.mods(comment.post.hole)): abort(403)

		comment.stickied = None
		comment.stickied_utc = None
		g.db.add(comment)

		ma = HoleAction(
			hole=comment.post.hole,
			kind="unpin_comment",
			user_id=v.id,
			target_comment_id=comment.id
		)
		g.db.add(ma)

		if v.id != comment.author_id:
			message = f"@{v.username} (a /h/{comment.post.hole} mod) has unpinned your [comment]({comment.shortlink})"
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
		abort(403)
	page = get_page()

	mod = request.values.get("mod")
	if mod: mod_id = get_user(mod, attributes=[User.id]).id
	else: mod_id = 0

	kind = request.values.get("kind")

	types = HOLEACTION_TYPES

	if kind and kind not in types:
		kind = None
		actions = []
		total=0
	else:
		actions = g.db.query(HoleAction).filter_by(hole=hole.name)

		if mod_id:
			actions = actions.filter_by(user_id=mod_id)
			kinds = set(x.kind for x in actions)
			if kind: kinds.add(kind)
			types2 = {}
			for k,val in types.items():
				if k in kinds: types2[k] = val
			types = types2
		if kind: actions = actions.filter_by(kind=kind)
		total = actions.count()
		actions = actions.order_by(HoleAction.id.desc()).offset(PAGE_SIZE*(page-1)).limit(PAGE_SIZE).all()

	mods = [x[0] for x in g.db.query(Mod.user_id).filter_by(hole=hole.name)]
	mods = [x[0] for x in g.db.query(User.username).filter(User.id.in_(mods)).order_by(User.username)]

	return render_template("log.html", v=v, admins=mods, types=types, admin=mod, type=kind, actions=actions, total=total, page=page, hole=hole, single_user_url='mod')

@app.get("/h/<hole>/log/<int:id>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def hole_log_item(id, v, hole):
	hole = get_hole(hole)
	if not can_see(v, hole):
		abort(403)

	action = g.db.get(HoleAction, id)

	if not action: abort(404)

	mods = [x[0] for x in g.db.query(Mod.user_id).filter_by(hole=hole.name)]
	mods = [x[0] for x in g.db.query(User.username).filter(User.id.in_(mods)).order_by(User.username)]

	types = HOLEACTION_TYPES

	return render_template("log.html", v=v, actions=[action], total=1, page=1, action=action, admins=mods, types=types, hole=hole, single_user_url='mod')
