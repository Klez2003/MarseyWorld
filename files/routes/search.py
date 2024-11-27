import re
import time
from calendar import timegm

from sqlalchemy.orm import load_only
from sqlalchemy import select

from files.helpers.regex import *
from files.helpers.sorting_and_time import *
from files.helpers.get import *
from files.routes.wrappers import *
from files.__main__ import app

valid_params = [
	'author',
	'domain',
	'site',
	'nsfw',
	'post',
	'before',
	'after',
	'title_only',
	'sentto',
	'hole',
	'subreddit',
	'flair',
	'effortpost',
]

def searchparse(text):
	text = text.lower()

	criteria = {x[0]:x[2] for x in query_regex.findall(text)}
	for x in criteria:
		if x in valid_params:
			text = text.replace(f"{x}:{criteria[x]}", "")

	text = text.strip()
	if text:
		criteria['full_text'] = text
		criteria['q'] = []
		for m in search_token_regex.finditer(text):
			token = m[1] if m[1] else m[2]
			if not token: token = ''
			token = escape_for_search(token)
			criteria['q'].append(token)

	return criteria

@app.get("/search/posts")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def searchposts(v):
	query = request.values.get("q", '').strip()

	author = request.values.get('author')
	if author:
		return redirect(f"/search/posts?q=author:{author} {query}")

	criteria = searchparse(query)

	if 'post' in criteria:
		return redirect(request.full_path.replace('/search/posts', '/search/comments'))

	page = get_page()

	sort = request.values.get("sort", "new").lower()
	t = request.values.get('t', 'all').lower()


	posts = g.db.query(Post).options(load_only(Post.id)) \
				.join(Post.author) \
				.filter(Post.author_id.notin_(v.userblocks))

	if v.admin_level < PERMS['POST_COMMENT_MODERATION']:
		posts = posts.filter(
			Post.deleted_utc == 0,
			Post.is_banned == False,
			Post.draft == False)

	if 'author' in criteria:
		author = get_user(criteria['author'], v=v)
		if author.id != v.id:
			posts = posts.filter(Post.ghost == False)
		if not author.is_visible_to(v, 0, "posts"):
			if v.client:
				stop(403, f"@{author.username}'s post history is private; You can't use the 'author' syntax on them")
			return render_template("search.html",
								v=v,
								query=query,
								total=0,
								page=page,
								listing=[],
								sort=sort,
								t=t,
								domain=None,
								domain_obj=None,
								error=f"@{author.username}'s post history is private; You can't use the 'author' syntax on them."
								), 403
		posts = posts.filter(Post.author_id == author.id)

	if 'q' in criteria:
		text = criteria['full_text']

		words = [Post.title_ts.bool_op("@@")(func.websearch_to_tsquery("simple", text))]
		if 'title_only' not in criteria:
			words.append(Post.body_ts.bool_op("@@")(func.websearch_to_tsquery("simple", text)))
			for x in criteria['q']:
				for param in (Post.url, Post.embed):
					if x.startswith('"') and x.endswith('"'):
						words.append(param.regexp_match(f'[[:<:]]{x[1:-1]}[[:>:]]'))
					else:
						words.append(param.ilike(f'%{x}%'))

		posts = posts.filter(or_(*words))

	if 'nsfw' in criteria:
		nsfw = criteria['nsfw'].lower().strip() == 'true'
		posts = posts.filter(Post.nsfw == nsfw)

	if 'effortpost' in criteria:
		effortpost = criteria['effortpost'].lower().strip() == 'true'
		posts = posts.filter(Post.effortpost == effortpost, Post.draft == False)

	if 'domain' in criteria or 'site' in criteria:
		if 'domain' in criteria:
			domain = criteria['domain']
		else:
			domain = criteria['site']

		domain = escape_for_search(domain)

		posts = posts.filter(
			or_(
				Post.url.ilike("https://"+domain+'/%'),
				Post.url.ilike("https://"+domain),
				Post.url.ilike("https://www."+domain+'/%'),
				Post.url.ilike("https://www."+domain),
				Post.url.ilike("https://old." + domain + '/%'),
				Post.url.ilike("https://old." + domain)
				)
			)

	if 'subreddit' in criteria:
		subreddit = criteria['subreddit']

		if not subreddit_name_regex.fullmatch(subreddit):
			stop(400, "Invalid subreddit name.")

		posts = posts.filter(Post.url.ilike(f"https://old.reddit.com/r/{subreddit}/%"))

	if 'flair' in criteria:
		flair = criteria['flair']
		if flair.startswith('"') and flair.endswith('"'):
			flair = flair[1:-1]
		posts = posts.filter(Post.flair.ilike(f'%{flair}%'))

	if 'hole' in criteria:
		posts = posts.filter(Post.hole == criteria['hole'])

	if 'after' in criteria:
		after = criteria['after']
		try: after = int(after)
		except:
			try: after = timegm(time.strptime(after, "%Y-%m-%d"))
			except: stop(400)
		posts = posts.filter(Post.created_utc > after)

	if 'before' in criteria:
		before = criteria['before']
		try: before = int(before)
		except:
			try: before = timegm(time.strptime(before, "%Y-%m-%d"))
			except: stop(400)
		posts = posts.filter(Post.created_utc < before)

	posts = apply_time_filter(t, posts, Post)

	if v.admin_level < PERMS['USER_SHADOWBAN']:
		posts = posts.join(Post.author).filter(or_(User.id == v.id, User.shadowbanned == None))

	total = posts.count()

	posts = sort_objects(sort, posts, Post)

	posts = posts.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()

	ids = [x.id for x in posts]

	posts = get_posts(ids, v=v)

	if v.client: return {"total":total, "data":[x.json for x in posts]}

	return render_template("search.html",
							v=v,
							query=query,
							page=page,
							listing=posts,
							sort=sort,
							t=t,
							total=total
						)

@app.get("/search/comments")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def searchcomments(v):
	query = request.values.get("q", '').strip()

	author = request.values.get('author')
	if author:
		return redirect(f"/search/comments?q=author:{author} {query}")

	page = get_page()

	sort = request.values.get("sort", "new").lower()
	t = request.values.get('t', 'all').lower()

	criteria = searchparse(query)

	comments = g.db.query(Comment).options(load_only(Comment.id)).outerjoin(Comment.post) \
		.filter(
			or_(Comment.parent_post != None, Comment.wall_user_id != None),
			Comment.author_id.notin_(v.userblocks),
		)


	if 'post' in criteria:
		try: post = int(criteria['post'])
		except: stop(404)
		comments = comments.filter(Comment.parent_post == post)


	if 'author' in criteria:
		author = get_user(criteria['author'], v=v)
		if author.id != v.id:
			comments = comments.filter(Comment.ghost == False)
		if not author.is_visible_to(v, 0, "comments"):
			if v.client:
				stop(403, f"@{author.username}'s comment history is private; You can't use the 'author' syntax on them")

			return render_template("search_comments.html", v=v, query=query, total=0, page=page, comments=[], sort=sort, t=t, error=f"@{author.username}'s comment history is private; You can't use the 'author' syntax on them!"), 403

		else: comments = comments.filter(Comment.author_id == author.id)
	else:
		comments = comments.filter(Comment.author_id != SNAPPY_ID)

	if 'q' in criteria:
		text = criteria['full_text']
		comments = comments.filter(
			Comment.body_ts.bool_op("@@")(
				func.websearch_to_tsquery("simple", text)
			)
		)

	if 'nsfw' in criteria:
		nsfw = criteria['nsfw'].lower().strip() == 'true'
		comments = comments.filter(Comment.nsfw == nsfw)

	if 'hole' in criteria:
		comments = comments.filter(Post.hole == criteria['hole'])

	comments = apply_time_filter(t, comments, Comment)

	if v.admin_level < PERMS['POST_COMMENT_MODERATION']:
		comments = comments.filter(
			Comment.is_banned==False,
			or_(
				Post.draft == False,
				Comment.wall_user_id != None
			)
		)


	if 'after' in criteria:
		after = criteria['after']
		try: after = int(after)
		except:
			try: after = timegm(time.strptime(after, "%Y-%m-%d"))
			except: stop(400)
		comments = comments.filter(Comment.created_utc > after)

	if 'before' in criteria:
		before = criteria['before']
		try: before = int(before)
		except:
			try: before = timegm(time.strptime(before, "%Y-%m-%d"))
			except: stop(400)
		comments = comments.filter(Comment.created_utc < before)

	if v.admin_level < PERMS['USER_SHADOWBAN']:
		comments = comments.join(Comment.author).filter(or_(User.id == v.id, User.shadowbanned == None))

	total = comments.count()

	comments = sort_objects(sort, comments, Comment)

	comments = comments.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()

	ids = [x.id for x in comments]

	comments = get_comments(ids, v=v)

	if v.client: return {"total":total, "data":[x.json for x in comments]}
	return render_template("search_comments.html", v=v, query=query, page=page, comments=comments, sort=sort, t=t, total=total, standalone=True)


@app.get("/search/messages")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def searchmessages(v):
	query = request.values.get("q", '').strip()

	page = get_page()

	sort = request.values.get("sort", "new").lower()
	t = request.values.get('t', 'all').lower()

	criteria = searchparse(query)

	dm_conditions = [Comment.author_id == v.id, Comment.sentto == v.id]
	if v.admin_level >= PERMS['VIEW_MODMAIL']:
		dm_conditions.append(Comment.sentto == MODMAIL_ID),

	comments = g.db.query(Comment).options(load_only(Comment.id)) \
		.filter(
			Comment.sentto != None,
			Comment.parent_post == None,
			or_(*dm_conditions),
		)

	if 'author' in criteria:
		comments = comments.filter(Comment.ghost == False)
		author = get_user(criteria['author'], v=v)
		comments = comments.filter(Comment.author_id == author.id)

	if 'q' in criteria:
		text = criteria['full_text']
		comments = comments.filter(
			Comment.body_ts.bool_op("@@")(
				func.websearch_to_tsquery("simple", text)
			)
		)

	comments = apply_time_filter(t, comments, Comment)

	if 'after' in criteria:
		after = criteria['after']
		try: after = int(after)
		except:
			try: after = timegm(time.strptime(after, "%Y-%m-%d"))
			except: stop(400)
		comments = comments.filter(Comment.created_utc > after)

	if 'before' in criteria:
		before = criteria['before']
		try: before = int(before)
		except:
			try: before = timegm(time.strptime(before, "%Y-%m-%d"))
			except: stop(400)
		comments = comments.filter(Comment.created_utc < before)

	if 'sentto' in criteria:
		sentto = criteria['sentto']
		sentto = get_user(sentto, graceful=True)

		if not sentto:
			stop(400, "The `sentto` field must contain an existing user's username!")

		comments = comments.filter(Comment.sentto == sentto.id)

	if v.admin_level < PERMS['USER_SHADOWBAN']:
		comments = comments.join(Comment.author).filter(or_(User.id == v.id, User.shadowbanned == None))

	total = comments.count()

	comments = sort_objects(sort, comments, Comment)

	comments = comments.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()

	for x in comments: x.unread = True

	comments = dict.fromkeys([x.top_comment for x in comments])

	if v.client: return {"total":total, "data":[x.json for x in comments]}
	return render_template("search_comments.html", v=v, query=query, page=page, comments=comments, sort=sort, t=t, total=total, standalone=True, render_replies=True)

@app.get("/search/users")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def searchusers(v):
	query = request.values.get("q", '').strip()

	page = get_page()

	users = g.db.query(User)

	criteria = searchparse(query)

	if 'after' in criteria:
		after = criteria['after']
		try: after = int(after)
		except:
			try: after = timegm(time.strptime(after, "%Y-%m-%d"))
			except: stop(400)
		users = users.filter(User.created_utc > after)

	if 'before' in criteria:
		before = criteria['before']
		try: before = int(before)
		except:
			try: before = timegm(time.strptime(before, "%Y-%m-%d"))
			except: stop(400)
		users = users.filter(User.created_utc < before)

	if 'q' in criteria:
		term = criteria['q'][0]
		term = sanitize_username(term)

		or_criteria = [
			User.username.ilike(f'%{term}%'),
			User.original_username.ilike(f'%{term}%'),
			User.extra_username.ilike(f'%{term}%'),
			User.prelock_username.ilike(f'%{term}%'),
		]
		if v.admin_level >= PERMS['VIEW_EMAILS']:
			or_criteria.append(User.email.ilike(f'%{term}%'))

		users = users.filter(or_(*or_criteria)).order_by(User.username.ilike(term).desc(), User.stored_subscriber_count.desc())

	total = users.count()

	users = users.offset(PAGE_SIZE * (page-1)).limit(PAGE_SIZE).all()

	if v.client: return {"data": [x.json for x in users]}
	return render_template("search_users.html", v=v, query=query, page=page, users=users, total=total)
