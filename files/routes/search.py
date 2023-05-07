import re
import time
from calendar import timegm

from sqlalchemy import *
from sqlalchemy.orm import load_only

from files.helpers.regex import *
from files.helpers.sorting_and_time import *
from files.routes.wrappers import *
from files.__main__ import app

search_operator_hole = HOLE_NAME

valid_params = [
	'author',
	'domain',
	'over18',
	'post',
	'before',
	'after',
	'title',
	'sentto',
	search_operator_hole,
]

def searchparse(text):
	text = text.lower()

	criteria = {x[0]:x[1] for x in query_regex.findall(text)}
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
			# Escape SQL pattern matching special characters
			token = token.replace('\\', '').replace('_', '\_').replace('%', '\%')
			criteria['q'].append(token)

	return criteria

@app.get("/search/posts")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def searchposts(v:User):
	query = request.values.get("q", '').strip()
	if not query:
		abort(403, "Empty searches aren't allowed!")

	page = get_page()

	sort = request.values.get("sort", "new").lower()
	t = request.values.get('t', 'all').lower()

	criteria=searchparse(query)

	posts = g.db.query(Submission).options(load_only(Submission.id)) \
				.join(Submission.author) \
				.filter(Submission.author_id.notin_(v.userblocks))

	if v.admin_level < PERMS['POST_COMMENT_MODERATION']:
		posts = posts.filter(
			Submission.deleted_utc == 0,
			Submission.is_banned == False,
			Submission.private == False)

	if 'author' in criteria:
		posts = posts.filter(Submission.ghost == False)
		author = get_user(criteria['author'], v=v)
		if not author.is_visible_to(v):
			if v.client:
				abort(403, f"@{author.username}'s profile is private; You can't use the 'author' syntax on them")
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
								error=f"@{author.username}'s profile is private; You can't use the 'author' syntax on them."
								), 403
		posts = posts.filter(Submission.author_id == author.id)

	if 'q' in criteria:
		if('title' in criteria):
			words = [or_(Submission.title.ilike('%'+x+'%')) \
					for x in criteria['q']]
		else:
			words = [or_(
						Submission.title.ilike('%'+x+'%'),
						Submission.body.ilike('%'+x+'%'),
						Submission.url.ilike('%'+x+'%'),
					) for x in criteria['q']]
		posts = posts.filter(*words)

	if 'over18' in criteria: posts = posts.filter(Submission.over_18==True)

	if 'domain' in criteria:
		domain=criteria['domain']

		domain = domain.replace('\\', '').replace('_', '\_').replace('%', '').strip()

		posts=posts.filter(
			or_(
				Submission.url.ilike("https://"+domain+'/%'),
				Submission.url.ilike("https://"+domain+'/%'),
				Submission.url.ilike("https://"+domain),
				Submission.url.ilike("https://"+domain),
				Submission.url.ilike("https://www."+domain+'/%'),
				Submission.url.ilike("https://www."+domain+'/%'),
				Submission.url.ilike("https://www."+domain),
				Submission.url.ilike("https://www."+domain),
				Submission.url.ilike("https://old." + domain + '/%'),
				Submission.url.ilike("https://old." + domain + '/%'),
				Submission.url.ilike("https://old." + domain),
				Submission.url.ilike("https://old." + domain)
				)
			)

	if search_operator_hole in criteria:
		posts = posts.filter(Submission.sub == criteria[search_operator_hole])

	if 'after' in criteria:
		after = criteria['after']
		try: after = int(after)
		except:
			try: after = timegm(time.strptime(after, "%Y-%m-%d"))
			except: abort(400)
		posts = posts.filter(Submission.created_utc > after)

	if 'before' in criteria:
		before = criteria['before']
		try: before = int(before)
		except:
			try: before = timegm(time.strptime(before, "%Y-%m-%d"))
			except: abort(400)
		posts = posts.filter(Submission.created_utc < before)

	posts = apply_time_filter(t, posts, Submission)

	total = posts.count()

	posts = sort_objects(sort, posts, Submission)

	posts = posts.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()

	ids = [x.id for x in posts]

	posts = get_posts(ids, v=v, eager=True)

	if v.client: return {"total":total, "data":[x.json(g.db) for x in posts]}

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
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def searchcomments(v:User):
	query = request.values.get("q", '').strip()
	if not query:
		abort(403, "Empty searches aren't allowed!")

	page = get_page()

	sort = request.values.get("sort", "new").lower()
	t = request.values.get('t', 'all').lower()

	criteria = searchparse(query)

	comments = g.db.query(Comment).options(load_only(Comment.id)).outerjoin(Comment.post) \
		.filter(
			or_(Comment.parent_submission != None, Comment.wall_user_id != None),
			Comment.author_id.notin_(v.userblocks),
		)


	if 'post' in criteria:
		try: post = int(criteria['post'])
		except: abort(404)
		comments = comments.filter(Comment.parent_submission == post)


	if 'author' in criteria:
		comments = comments.filter(Comment.ghost == False)
		author = get_user(criteria['author'], v=v)
		if not author.is_visible_to(v):
			if v.client:
				abort(403, f"@{author.username}'s profile is private; You can't use the 'author' syntax on them")

			return render_template("search_comments.html", v=v, query=query, total=0, page=page, comments=[], sort=sort, t=t, error=f"@{author.username}'s profile is private; You can't use the 'author' syntax on them!"), 403

		else: comments = comments.filter(Comment.author_id == author.id)

	if 'q' in criteria:
		tokens = map(lambda x: re.sub(r'[\0():|&*!<>]', '', x), criteria['q'])
		tokens = filter(lambda x: len(x) > 0, tokens)
		tokens = map(lambda x: re.sub(r"'", "\\'", x), tokens)
		tokens = map(lambda x: x.strip(), tokens)
		tokens = map(lambda x: re.sub(r'\s+', ' <-> ', x), tokens)
		comments = comments.filter(Comment.body_ts.match(
			' & '.join(tokens),
			postgresql_regconfig='english'))

	if 'over18' in criteria: comments = comments.filter(Comment.over_18 == True)

	if search_operator_hole in criteria:
		comments = comments.filter(Submission.sub == criteria[search_operator_hole])

	comments = apply_time_filter(t, comments, Comment)

	if v.admin_level < PERMS['POST_COMMENT_MODERATION']:
		private = [x[0] for x in g.db.query(Submission.id).filter(Submission.private == True).all()]

		comments = comments.filter(
			Comment.is_banned==False,
			Comment.deleted_utc == 0,
			or_(
				Comment.parent_submission.notin_(private),
				Comment.wall_user_id != None
			)
		)


	if 'after' in criteria:
		after = criteria['after']
		try: after = int(after)
		except:
			try: after = timegm(time.strptime(after, "%Y-%m-%d"))
			except: abort(400)
		comments = comments.filter(Comment.created_utc > after)

	if 'before' in criteria:
		before = criteria['before']
		try: before = int(before)
		except:
			try: before = timegm(time.strptime(before, "%Y-%m-%d"))
			except: abort(400)
		comments = comments.filter(Comment.created_utc < before)

	total = comments.count()

	comments = sort_objects(sort, comments, Comment)

	comments = comments.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()

	ids = [x.id for x in comments]

	comments = get_comments(ids, v=v)

	if v.client: return {"total":total, "data":[x.json(db=g.db) for x in comments]}
	return render_template("search_comments.html", v=v, query=query, page=page, comments=comments, sort=sort, t=t, total=total, standalone=True)


@app.get("/search/messages")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def searchmessages(v:User):
	query = request.values.get("q", '').strip()
	if not query:
		abort(403, "Empty searches aren't allowed!")

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
			Comment.parent_submission == None,
			or_(*dm_conditions),
		)

	if 'author' in criteria:
		comments = comments.filter(Comment.ghost == False)
		author = get_user(criteria['author'], v=v)
		if not author.is_visible_to(v):
			if v.client:
				abort(403, f"@{author.username}'s profile is private; You can't use the 'author' syntax on them")

			return render_template("search_comments.html", v=v, query=query, total=0, page=page, comments=[], sort=sort, t=t, error=f"@{author.username}'s profile is private; You can't use the 'author' syntax on them!"), 403

		else: comments = comments.filter(Comment.author_id == author.id)

	if 'q' in criteria:
		tokens = map(lambda x: re.sub(r'[\0():|&*!<>]', '', x), criteria['q'])
		tokens = filter(lambda x: len(x) > 0, tokens)
		tokens = map(lambda x: re.sub(r"'", "\\'", x), tokens)
		tokens = map(lambda x: x.strip(), tokens)
		tokens = map(lambda x: re.sub(r'\s+', ' <-> ', x), tokens)
		comments = comments.filter(Comment.body_ts.match(
			' & '.join(tokens),
			postgresql_regconfig='english'))

	comments = apply_time_filter(t, comments, Comment)

	if 'after' in criteria:
		after = criteria['after']
		try: after = int(after)
		except:
			try: after = timegm(time.strptime(after, "%Y-%m-%d"))
			except: abort(400)
		comments = comments.filter(Comment.created_utc > after)

	if 'before' in criteria:
		before = criteria['before']
		try: before = int(before)
		except:
			try: before = timegm(time.strptime(before, "%Y-%m-%d"))
			except: abort(400)
		comments = comments.filter(Comment.created_utc < before)

	if 'sentto' in criteria:
		sentto = criteria['sentto']
		try: sentto = get_user(sentto, graceful=True)
		except:
			abort(400, "The `sentto` field must contain a user's username!")
		comments = comments.filter(Comment.sentto == sentto.id)

	total = comments.count()

	comments = sort_objects(sort, comments, Comment)

	comments = comments.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()

	for x in comments: x.unread = True

	comments = [x.top_comment for x in comments]

	if v.client: return {"total":total, "data":[x.json(db=g.db) for x in comments]}
	return render_template("search_comments.html", v=v, query=query, page=page, comments=comments, sort=sort, t=t, total=total, standalone=True, render_replies=True)

@app.get("/search/users")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def searchusers(v:User):
	query = request.values.get("q", '').strip()
	if not query:
		abort(403, "Empty searches aren't allowed!")

	page = get_page()

	users = g.db.query(User)

	criteria = searchparse(query)

	if 'after' in criteria:
		after = criteria['after']
		try: after = int(after)
		except:
			try: after = timegm(time.strptime(after, "%Y-%m-%d"))
			except: abort(400)
		users = users.filter(User.created_utc > after)

	if 'before' in criteria:
		before = criteria['before']
		try: before = int(before)
		except:
			try: before = timegm(time.strptime(before, "%Y-%m-%d"))
			except: abort(400)
		users = users.filter(User.created_utc < before)

	if 'q' in criteria:
		term = criteria['q'][0]
		term = term.lstrip('@')
		term = term.replace('\\','').replace('_','\_').replace('%','')

		users = users.filter(
			or_(
				User.username.ilike(f'%{term}%'),
				User.original_username.ilike(f'%{term}%')
			)
		).order_by(User.username.ilike(term).desc(), User.stored_subscriber_count.desc())

	total = users.count()

	users = users.offset(PAGE_SIZE * (page-1)).limit(PAGE_SIZE).all()

	if v.client: return {"data": [x.json for x in users]}
	return render_template("search_users.html", v=v, query=query, page=page, users=users, total=total)
