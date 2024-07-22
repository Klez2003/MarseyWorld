
from sqlalchemy import or_, not_
from sqlalchemy.orm import load_only

from files.classes.post import Post
from files.classes.votes import Vote
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.sorting_and_time import *
from files.helpers.useractions import *
from files.helpers.can_see import *
from files.routes.wrappers import *
from files.__main__ import app, cache, limiter

@app.get("/")
@app.get("/community")
@app.get("/h/<hole>")
@limiter.limit("30/minute;5000/hour;10000/day", deduct_when=lambda response: response.status_code < 400)
@auth_desired_with_logingate
def front_all(v, hole=None):
	if hole:
		hole = get_hole(hole, graceful=True)
		if hole and not can_see(v, hole):
			abort(403)

	if request.path.startswith('/h/') and not hole:
		abort(404)

	page = get_page()

	effortposts_only = request.values.get('effortposts_only', False)

	if effortposts_only:
		defaultsorting = 'new'
		defaulttime = 'all'
	elif v:
		defaultsorting = v.defaultsorting
		if hole: defaulttime = 'all'
		else: defaulttime = v.defaulttime
	else:
		defaultsorting = "hot"
		if hole: defaulttime = 'all'
		else: defaulttime = DEFAULT_TIME_FILTER

	if hole:
		defaultsorting = "new"

	sort = request.values.get("sort", defaultsorting)
	t = request.values.get('t', defaulttime)

	if SITE == 'rdrama.net' and t == 'all' and sort == 'hot' and page > 1000:
		sort = 'top'

	try: gt = int(request.values.get("after", 0))
	except: gt = 0

	try: lt = int(request.values.get("before", 0))
	except: lt = 0

	if effortposts_only:
		pins = False
	else:
		if sort == 'hot' or (hole and sort == 'new'):
			default = True
		else:
			default = False
		pins = session.get(f'{hole}_{sort}', default)

	if not v:
		result = cache.get(f'frontpage_{sort}_{t}_{page}_{hole}_{pins}_{effortposts_only}')
		if result:
			calc_users()
			return result

	hide_cw = (SITE_NAME == 'WPD' and v and v.hide_cw)

	is_community = (request.path == '/community')

	ids, total, size = frontlist(sort=sort,
					page=page,
					t=t,
					v=v,
					filter_words=v.filter_words if v else [],
					gt=gt,
					lt=lt,
					hole=hole,
					pins=pins,
					effortposts_only=effortposts_only,
					hide_cw=hide_cw,
					is_community=is_community,
					)

	posts = get_posts(ids, v=v)

	if v and v.hidevotedon:
		posts = [x for x in posts if not hasattr(x, 'voted') or not x.voted]

	if v and v.client: return {"data": [x.json for x in posts], "total": total}

	result = render_template("home.html", v=v, listing=posts, total=total, sort=sort, t=t, page=page, hole=hole, home=True, pins=pins, size=size)

	if not v:
		cache.set(f'frontpage_{sort}_{t}_{page}_{hole}_{pins}_{effortposts_only}', result, timeout=900)

	return result


COMMUNITY_WPD_HOLES = {'art', 'discussion', 'meta', 'music', 'pets', 'social'}

LIMITED_WPD_HOLES = COMMUNITY_WPD_HOLES | \
					 {'aftermath', 'fights', 'gore', 'medical', 'request', 'selfharm',
					 'countryclub', 'highrollerclub',
					 'slavshit', 'sandshit'}

@cache.memoize(timeout=86400)
def frontlist(v=None, sort="hot", page=1, t="all", ids_only=True, filter_words='', gt=0, lt=0, hole=None, pins=True, effortposts_only=False, hide_cw=False, is_community=False):
	posts = g.db.query(Post).options(load_only(Post.id))

	if v and v.hidevotedon:
		posts = posts.outerjoin(Vote,
					and_(Vote.post_id == Post.id, Vote.user_id == v.id)
				).filter(Vote.post_id == None)

	if hole:
		posts = posts.filter(Post.hole == hole.name)
	elif v:
		posts = posts.filter(or_(Post.hole == None, Post.hole.notin_(v.hole_blocks)))
	else:
		stealth = [x[0] for x in g.db.query(Hole.name).filter_by(stealth=True)]
		posts = posts.filter(or_(Post.hole == None, Post.hole.notin_(stealth)))

	if gt: posts = posts.filter(Post.created_utc > gt)
	if lt: posts = posts.filter(Post.created_utc < lt)

	if effortposts_only:
		posts = posts.filter(Post.effortpost == True)

	if not gt and not lt:
		posts = apply_time_filter(t, posts, Post)

	posts = posts.filter(
		Post.is_banned == False,
		Post.draft == False,
		Post.deleted_utc == 0,
	)

	if hide_cw:
		posts = posts.filter(
			or_(
				Post.cw == False,
				Post.author_id == v.id,
			)
		)

	if pins and not gt and not lt:
		if hole: posts = posts.filter(Post.hole_pinned == None)
		else: posts = posts.filter(Post.pinned == None)

	if v:
		posts = posts.filter(Post.author_id.notin_(v.userblocks))

	if v and filter_words:
		for word in filter_words:
			word = escape_for_search(word)
			posts = posts.filter(not_(Post.title.ilike(f'%{word}%')))

	if v and v.admin_level < PERMS['USER_SHADOWBAN']:
		posts = posts.join(Post.author).filter(or_(User.id == v.id, User.shadowbanned == None))

	total = posts.count()

	posts = sort_objects(sort, posts, Post)

	if v: size = v.frontsize or 0
	else: size = PAGE_SIZE

	if SITE_NAME == 'WPD':
		if is_community:
			posts = posts.filter(Post.hole.in_(COMMUNITY_WPD_HOLES))
		elif not v and hole == None and sort != "hot":
			posts = posts.filter(Post.hole.notin_({'pets','selfharm'}))

	if SITE_NAME == 'WPD' and sort == "hot" and hole == None and not is_community:
		size -= 3
		posts1 = posts.filter(Post.hole.notin_(LIMITED_WPD_HOLES)).offset((size) * (page - 1)).limit(size).all()
		if posts1:
			posts2 = posts.filter(Post.hole.in_(LIMITED_WPD_HOLES)).offset(3 * (page - 1)).limit(3).all()
			posts = posts1 + posts2
		else:
			elapsed_pages = posts.filter(Post.hole.notin_(LIMITED_WPD_HOLES)).count() / size
			size += 3
			posts = posts.filter(Post.hole.in_(LIMITED_WPD_HOLES)).offset(3 * elapsed_pages + size * (page - 1 - elapsed_pages)).limit(size).all()
	else:
		posts = posts.offset(size * (page - 1)).limit(size).all()

	if pins and page == 1 and not gt and not lt:
		if hole:
			pins = g.db.query(Post).options(load_only(Post.id)).filter(Post.hole == hole.name, Post.hole_pinned != None)
		else:
			pins = g.db.query(Post).options(load_only(Post.id)).filter(Post.pinned != None, Post.is_banned == False)

			if v:
				pins = pins.filter(or_(Post.hole == None, Post.hole.notin_(v.hole_blocks)))


		if v: pins = pins.filter(Post.author_id.notin_(v.userblocks))
		pins = pins.order_by(Post.created_utc.desc()).all()
		posts = pins + posts

	if ids_only: posts = [x.id for x in posts]
	return posts, total, size


@app.get("/random_post")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def random_post(v):

	p = g.db.query(Post.id).filter(
			Post.deleted_utc == 0,
			Post.is_banned == False,
			Post.draft == False,
			or_(Post.hole == None, Post.hole.notin_(v.hole_blocks)),
		).order_by(func.random()).first()

	if p: p = p[0]
	else: abort(404)

	return redirect(f"/post/{p}")


@app.get("/random_user")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def random_user(v):
	u = g.db.query(User.username).filter(
		User.song != None,
		User.shadowbanned == None,
	).order_by(func.random()).first()

	if u: u = u[0]
	else: abort(404, "No users have set a profile anthem so far!")

	return redirect(f"/@{u}")

@cache.memoize(timeout=86400)
def comment_idlist(v=None, page=1, sort="new", t="day", gt=0, lt=0):
	comments = g.db.query(Comment) \
		.outerjoin(Comment.post) \
		.options(load_only(Comment.id)) \
		.filter(
			or_(Comment.parent_post != None, Comment.wall_user_id != None),
		)

	if v.admin_level < PERMS['POST_COMMENT_MODERATION']:
		comments = comments.filter(
			Comment.is_banned == False,
			Comment.deleted_utc == 0,
			Comment.author_id.notin_(v.userblocks),
			or_(Comment.parent_post == None, Post.draft == False),
		)

	if gt: comments = comments.filter(Comment.created_utc > gt)
	if lt: comments = comments.filter(Comment.created_utc < lt)

	if not gt and not lt:
		comments = apply_time_filter(t, comments, Comment)

	if v.admin_level < PERMS['USER_SHADOWBAN']:
		comments = comments.join(Comment.author).filter(or_(User.id == v.id, User.shadowbanned == None))

	total = comments.count()
	comments = sort_objects(sort, comments, Comment)

	comments = comments.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()
	return [x.id for x in comments], total

@app.get("/comments")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def all_comments(v):
	page = get_page()

	sort = request.values.get("sort", "new")
	t = request.values.get("t", "hour")

	try: gt=int(request.values.get("after", 0))
	except: gt=0

	try: lt=int(request.values.get("before", 0))
	except: lt=0
	idlist, total = comment_idlist(v=v,
							page=page,
							sort=sort,
							t=t,
							gt=gt,
							lt=lt,
							)

	comments = get_comments(idlist, v=v)

	if v.client: return {"data": [x.json for x in comments]}
	return render_template("home_comments.html", v=v, sort=sort, t=t, page=page, comments=comments, standalone=True, total=total, size = PAGE_SIZE)
