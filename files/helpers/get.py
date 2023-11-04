
from flask import *
from sqlalchemy import and_, any_, or_
from sqlalchemy.orm import joinedload, Query, load_only

from files.classes import Comment, CommentVote, Hat, Hole, Post, User, UserBlock, Vote
from files.helpers.config.const import *
from files.__main__ import cache

# Escape SQL pattern-matching special characters
def escape_for_search(string):
	return string.replace('\\', '').replace('_', '\_').replace('%', '\%').strip()

def sanitize_username(username):
	username = username.lstrip('@').replace('(', '').replace(')', '')
	username = escape_for_search(username)
	return username

def get_user(username, v=None, graceful=False, include_blocks=False, attributes=None):
	if not username:
		if graceful: return None
		abort(400, "Empty username.")

	search_name = sanitize_username(username)
	if not search_name:
		if graceful: return None
		abort(400, "Empty username.")

	user = g.db.query(
		User
		).filter(
		or_(
			User.username.ilike(search_name),
			User.original_username.ilike(search_name),
			User.prelock_username.ilike(search_name),
			)
		)

	if attributes:
		user = user.options(load_only(*attributes))

	user = user.one_or_none()

	if not user:
		if graceful: return None
		abort(404, f"A user with the name '{username}' was not found!")

	if v and include_blocks:
		user = add_block_props(user, v)
	return user

def get_users(usernames, ids_only=False, graceful=False):
	if not usernames: return []
	usernames = [sanitize_username(n) for n in usernames]
	if not any(usernames):
		if graceful and len(usernames) == 0: return []
		abort(400, "Empty usernames.")

	if ids_only:
		users = g.db.query(User.id)
	else:
		users = g.db.query(User)

	users = users.filter(
		or_(
			User.username.ilike(any_(usernames)),
			User.original_username.ilike(any_(usernames)),
			User.prelock_username.ilike(any_(usernames)),
			)
		).all()

	if len(users) != len(usernames) and not graceful:
		abort(404, "Users not found.")

	if ids_only:
		users = [x[0] for x in users]

	return users

def get_account(id, v=None, graceful=False, include_blocks=False):
	try:
		id = int(id)
	except:
		if graceful: return None
		abort(400, "User ID needs to be an integer.")

	user = g.db.get(User, id)

	if not user:
		if not graceful: abort(404, "User not found.")
		else: return None

	if include_blocks:
		user = add_block_props(user, v)
	return user


def get_accounts_dict(ids, v=None, graceful=False):
	if not ids: return {}
	try:
		ids = set(int(id) for id in ids)
	except:
		if graceful: return None
		abort(400, "User IDs need to be an integer.")

	users = g.db.query(User).filter(User.id.in_(ids))
	users = users.all()
	if len(users) != len(ids) and not graceful:
		abort(404, "Users not found.")

	return {u.id:u for u in users}

def get_post(i, v=None, graceful=False):
	try: i = int(i)
	except:
		if graceful: return None
		else: abort(400, "Post ID needs to be an integer.")

	if not i:
		if graceful: return None
		else: abort(400, "Empty post ID.")

	if v:
		vt = g.db.query(Vote).filter_by(user_id=v.id, post_id=i).subquery()
		blocking = v.blocking.subquery()

		post = g.db.query(
			Post,
			vt.c.vote_type,
			blocking.c.target_id,
		)

		post = post.filter(Post.id == i
		).outerjoin(
			vt,
			vt.c.post_id == Post.id,
		).outerjoin(
			blocking,
			blocking.c.target_id == Post.author_id,
		)

		post = post.one_or_none()

		if not post:
			if graceful: return None
			else: abort(404, "Post not found.")

		x = post[0]
		x.voted = post[1] or 0
		x.is_blocking = post[2] or 0
	else:
		post = g.db.get(Post, i)
		if not post:
			if graceful: return None
			else: abort(404, "Post not found.")
		x=post

	return x


def get_posts(pids, v=None, extra=None):
	if not pids: return []

	if v:
		vt = g.db.query(Vote.vote_type, Vote.post_id).filter(
			Vote.post_id.in_(pids),
			Vote.user_id==v.id
			).subquery()

		blocking = v.blocking.subquery()
		blocked = v.blocked.subquery()

		query = g.db.query(
			Post,
			vt.c.vote_type,
			blocking.c.target_id,
			blocked.c.target_id,
		).filter(
			Post.id.in_(pids)
		).outerjoin(
			vt, vt.c.post_id==Post.id
		).outerjoin(
			blocking,
			blocking.c.target_id == Post.author_id,
		).outerjoin(
			blocked,
			blocked.c.user_id == Post.author_id,
		)
	else:
		query = g.db.query(Post).filter(Post.id.in_(pids))

	if extra: query = extra(query)

	results = query.all()

	if v:
		output = [p[0] for p in results]
		for i in range(len(output)):
			output[i].voted = results[i][1] or 0
			output[i].is_blocking = results[i][2] or 0
			output[i].is_blocked = results[i][3] or 0
	else:
		output = results

	return sorted(output, key=lambda x: pids.index(x.id))

def get_comment(i, v=None, graceful=False):
	try: i = int(i)
	except:
		if graceful: return None
		abort(404, "Comment ID needs to be an integer.")

	if not i:
		if graceful: return None
		else: abort(404, "Empty comment ID.")

	comment = g.db.get(Comment, i)
	if not comment:
		if graceful: return None
		else: abort(404, "Comment not found.")

	return add_vote_and_block_props(comment, v, CommentVote)

def add_block_props(target, v):
	if not v: return target
	id = None

	if any(isinstance(target, cls) for cls in {Post, Comment}):
		id = target.author_id
	elif isinstance(target, User):
		id = target.id
	else:
		raise TypeError("add_block_props only supports non-None posts, comments, and users")

	if hasattr(target, 'is_blocking') and hasattr(target, 'is_blocked'):
		return target

	if v.id == id or id == AUTOJANNY_ID: # users can't block or be blocked by themselves or AutoJanny
		target.is_blocking = False
		target.is_blocked = False
		return target

	block = g.db.query(UserBlock).filter(
		or_(
			and_(
				UserBlock.user_id == v.id,
				UserBlock.target_id == id
			),
			and_(
				UserBlock.user_id == id,
				UserBlock.target_id == v.id
			)
		)
	).first()
	target.is_blocking = block and block.user_id == v.id
	target.is_blocked = block and block.target_id == v.id
	return target

def add_vote_props(target, v, vote_cls):
	if hasattr(target, 'voted'): return target

	vt = g.db.query(vote_cls.vote_type).filter_by(user_id=v.id)
	if vote_cls == Vote:
		vt = vt.filter_by(post_id=target.id)
	elif vote_cls == CommentVote:
		vt = vt.filter_by(comment_id=target.id)
	else:
		vt = None
	if vt: vt = vt.one_or_none()
	target.voted = vt.vote_type if vt else 0
	return target

def add_vote_and_block_props(target, v, vote_cls):
	if not v: return target
	target = add_block_props(target, v)
	return add_vote_props(target, v, vote_cls)

def get_comments(cids, v=None, extra=None):
	if not cids: return []
	if v:
		output = get_comments_v_properties(v, None, Comment.id.in_(cids))[1]
	else:
		output = g.db.query(Comment).join(Comment.author)
		if extra: output = extra(output)
		output = output.filter(Comment.id.in_(cids)).all()
	return sorted(output, key=lambda x: cids.index(x.id))

def get_comments_v_properties(v, should_keep_func=None, *criterion):
	if not v:
		raise TypeError("A user is required")
	votes = g.db.query(CommentVote.vote_type, CommentVote.comment_id).filter_by(user_id=v.id).subquery()
	blocking = v.blocking.subquery()
	blocked = v.blocked.subquery()
	comments = g.db.query(
		Comment,
		votes.c.vote_type,
		blocking.c.target_id,
		blocked.c.target_id,
	)

	comments = comments.filter(*criterion)
	comments = comments.outerjoin(
		votes,
		votes.c.comment_id == Comment.id,
	).outerjoin(
		blocking,
		blocking.c.target_id == Comment.author_id,
	).outerjoin(
		blocked,
		blocked.c.user_id == Comment.author_id,
	)
	queried = comments.all()
	output = []
	dump = []
	for c in queried:
		comment = c[0]
		comment.voted = c[1] or 0
		comment.is_blocking = c[2] or 0
		comment.is_blocked = c[3] or 0
		if not should_keep_func or should_keep_func(c[0]): output.append(comment)
		else: dump.append(comment)
	return (comments, output)

def get_hole(hole, v=None, graceful=False):
	if not hole:
		if graceful: return None
		else: abort(404)
	hole = hole.replace('/h/', '').replace('h/', '').strip().lower()
	if not hole:
		if graceful: return None
		else: abort(404)
	hole = g.db.get(Hole, hole)
	if not hole:
		if graceful: return None
		else: abort(404)
	return hole

@cache.memoize(timeout=3600)
def get_profile_picture(identifier):
	if isinstance(identifier, int):
		x = get_account(identifier, graceful=True)
	else:
		x = get_user(identifier, graceful=True)

	return x.profile_url if x else 'not_found'

def get_msg():
	if request.referrer and request.referrer.split('?')[0] == request.base_url:
		return request.values.get("msg")
	else:
		return None

def get_error():
	if request.referrer and request.referrer.split('?')[0] == request.base_url:
		return request.values.get("error")
	else:
		return None

def get_page():
	try: return max(int(request.values.get("page", 1)), 1)
	except: return 1

def get_obj_hole(obj):
	if isinstance(obj, Comment):
		if obj.parent_post:
			obj.hole = g.db.query(Post.hole).filter_by(id=obj.parent_post).one()[0]
		else:
			obj.hole = None
	return obj.hole
