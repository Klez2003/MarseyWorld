
from sqlalchemy import or_, not_
from sqlalchemy.orm import load_only

from files.classes.post import Post
from files.classes.votes import Vote
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.sorting_and_time import *
from files.helpers.useractions import *
from files.routes.wrappers import *
from files.__main__ import app, cache, limiter

@app.get("/")
@app.get("/h/<sub>")
@limiter.limit("30/minute;5000/hour;10000/day")
@auth_desired_with_logingate
def front_all(v, sub=None, subdomain=None):
	if sub:
		sub = get_sub_by_name(sub, graceful=True)
		if sub and not User.can_see(v, sub):
			abort(403)

	if (request.path.startswith('/h/') or request.path.startswith('/s/')) and not sub: abort(404)

	page = get_page()

	if v:
		defaultsorting = v.defaultsorting
		if sub or SITE_NAME != 'rDrama': defaulttime = 'all'
		else: defaulttime = v.defaulttime
	else:
		defaultsorting = "hot"
		if sub or SITE_NAME != 'rDrama': defaulttime = 'all'
		else: defaulttime = DEFAULT_TIME_FILTER

	sort=request.values.get("sort", defaultsorting)
	t=request.values.get('t', defaulttime)

	try: gt=int(request.values.get("after", 0))
	except: gt=0

	try: lt=int(request.values.get("before", 0))
	except: lt=0

	if sort == 'hot': default = True
	else: default = False

	pins = session.get(sort, default)

	ids, total, size = frontlist(sort=sort,
					page=page,
					t=t,
					v=v,
					filter_words=v.filter_words if v else [],
					gt=gt,
					lt=lt,
					sub=sub,
					pins=pins,
					)

	posts = get_posts(ids, v=v, eager=True)

	if v and v.hidevotedon:
		posts = [x for x in posts if not hasattr(x, 'voted') or not x.voted]

	if v and v.client: return {"data": [x.json(g.db) for x in posts], "total": total}
	return render_template("home.html", v=v, listing=posts, total=total, sort=sort, t=t, page=page, sub=sub, home=True, pins=pins, size=size)


LIMITED_WPD_HOLES = ('gore', 'aftermath', 'selfharm', 'meta', 'discussion', 'social', 'music', 'request')

@cache.memoize()
def frontlist(v=None, sort="hot", page=1, t="all", ids_only=True, filter_words='', gt=0, lt=0, sub=None, pins=True):
	posts = g.db.query(Post)

	if v and v.hidevotedon:
		posts = posts.outerjoin(Vote,
					and_(Vote.post_id == Post.id, Vote.user_id == v.id)
				).filter(Vote.post_id == None)

	if sub: posts = posts.filter(Post.sub == sub.name)
	elif v: posts = posts.filter(or_(Post.sub == None, Post.sub.notin_(v.all_blocks)))

	if gt: posts = posts.filter(Post.created_utc > gt)
	if lt: posts = posts.filter(Post.created_utc < lt)

	if not gt and not lt:
		posts = apply_time_filter(t, posts, Post)

	posts = posts.filter(
		Post.is_banned == False,
		Post.private == False,
		Post.deleted_utc == 0,
	)

	if pins and not gt and not lt:
		if sub: posts = posts.filter(Post.hole_pinned == None)
		else: posts = posts.filter(Post.stickied == None)

	if v:
		posts = posts.filter(Post.author_id.notin_(v.userblocks))

	if v and filter_words:
		for word in filter_words:
			word = word.replace('\\', '').replace('_', '\_').replace('%', '\%').strip()
			posts=posts.filter(not_(Post.title.ilike(f'%{word}%')))

	total = posts.count()

	posts = sort_objects(sort, posts, Post)

	if v: size = v.frontsize or 0
	else: size = PAGE_SIZE

	posts = posts.options(load_only(Post.id)).offset(size * (page - 1))

	if SITE_NAME == 'WPD' and sort == "hot" and sub == None:
		posts = posts.limit(200).all()

		to_remove = []
		for h in LIMITED_WPD_HOLES:
			to_remove += [x.id for x in posts if x.sub == h][1:]

		posts = [x for x in posts if x.id not in to_remove][:size]
	else:
		posts = posts.limit(size).all()

	if pins and page == 1 and not gt and not lt:
		if sub:
			pins = g.db.query(Post).options(load_only(Post.id)).filter(Post.sub == sub.name, Post.hole_pinned != None)
		else:
			pins = g.db.query(Post).options(load_only(Post.id)).filter(Post.stickied != None, Post.is_banned == False)

			if v:
				pins = pins.filter(or_(Post.sub == None, Post.sub.notin_(v.all_blocks)))
				for pin in pins:
					if pin.stickied_utc and int(time.time()) > pin.stickied_utc:
						pin.stickied = None
						pin.stickied_utc = None
						g.db.add(pin)


		if v: pins = pins.filter(Post.author_id.notin_(v.userblocks))
		if SITE_NAME == 'rDrama':
			pins = pins.order_by(Post.author_id != LAWLZ_ID)
		pins = pins.order_by(Post.created_utc.desc()).all()
		posts = pins + posts

	if v and (time.time() - v.created_utc) > (365 * 86400 - 1):
		badge_grant(user=v, badge_id=134)

	if v and (time.time() - v.created_utc) > (365 * 86400 * 2 - 1):
		badge_grant(user=v, badge_id=237)

	if ids_only: posts = [x.id for x in posts]
	return posts, total, size


@app.get("/random_post")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def random_post(v:User):

	p = g.db.query(Post.id).filter(Post.deleted_utc == 0, Post.is_banned == False, Post.private == False).order_by(func.random()).first()

	if p: p = p[0]
	else: abort(404)

	return redirect(f"/post/{p}")


@app.get("/random_user")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def random_user(v:User):
	u = g.db.query(User.username).filter(User.song != None).order_by(func.random()).first()

	if u: u = u[0]
	else: abort(404, "No users have set a profile anthem so far!")

	return redirect(f"/@{u}")

@cache.memoize()
def comment_idlist(v=None, page=1, sort="new", t="day", gt=0, lt=0):
	comments = g.db.query(Comment) \
		.outerjoin(Comment.post) \
		.options(load_only(Comment.id)) \
		.filter(
			or_(Comment.parent_submission != None, Comment.wall_user_id != None),
		)

	if v.admin_level < PERMS['POST_COMMENT_MODERATION']:
		comments = comments.filter(
			Comment.is_banned == False,
			Comment.deleted_utc == 0,
			Comment.author_id.notin_(v.userblocks),
			or_(Comment.parent_submission == None, Post.private == False),
		)

	if gt: comments = comments.filter(Comment.created_utc > gt)
	if lt: comments = comments.filter(Comment.created_utc < lt)

	if not gt and not lt:
		comments = apply_time_filter(t, comments, Comment)

	total = comments.count()
	comments = sort_objects(sort, comments, Comment)

	comments = comments.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()
	return [x.id for x in comments], total

@app.get("/comments")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def all_comments(v:User):
	page = get_page()

	sort=request.values.get("sort", "new")
	t=request.values.get("t", "hour")

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

	if v.client: return {"data": [x.json(g.db) for x in comments]}
	return render_template("home_comments.html", v=v, sort=sort, t=t, page=page, comments=comments, standalone=True, total=total, size = PAGE_SIZE)
