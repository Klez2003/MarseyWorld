from files.classes import *
from files.helpers.config.const import *
from files.helpers.config.boosted_sites import *
from files.helpers.get import *
from files.helpers.alerts import *
from files.helpers.can_see import *
from files.routes.wrappers import *
from files.__main__ import app, limiter
from files.routes.routehelpers import get_alt_graph
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy.orm.exc import StaleDataError

from math import floor
from datetime import datetime

def get_coin_mul(cls, target):
	if cls == Post and target.effortpost:
		coin_mul = 16
	else:
		coin_mul = 1

		if SITE_NAME == 'WPD' or cls == Post:
			coin_mul *= 4

		if IS_EVENT():
			coin_mul *= 2

		if IS_HOMOWEEN() and target.author.zombie > 0:
			coin_mul += 1
	
	return coin_mul


def vote_post_comment(target_id, new, v, cls, vote_cls):
	if new == "-1" and DISABLE_DOWNVOTES: stop(403)
	if new not in {"-1", "0", "1"}: stop(400)

	if request.headers.get("Authorization"):
		stop(403, "Bots aren't allowed to vote right now!")

	new = int(new)
	target = None
	if cls == Post:
		target = get_post(target_id)
	elif cls == Comment:
		target = get_comment(target_id)
		if not target.parent_post and not target.wall_user_id: stop(404)
	else:
		stop(404)

	if not can_see(v, target): stop(403)

	coin_delta = 1
	if v.id == target.author.id:
		coin_delta = 0

	if v.truescore < 10:
		coin_delta = 0

	alt = False
	if target.author.id in [x.id for x in get_alt_graph(v.id)]:
		coin_delta = -1
		alt = True

	g.db.flush()
	existing = g.db.query(vote_cls).filter_by(user_id=v.id)
	if vote_cls == Vote:
		existing = existing.filter_by(post_id=target.id)
	elif vote_cls == CommentVote:
		existing = existing.filter_by(comment_id=target.id)
	else:
		stop(400)
	existing = existing.one_or_none()

	coin_mul = get_coin_mul(cls, target)

	coin_value = coin_delta * coin_mul

	imlazy = 0

	if existing and existing.vote_type == new: return ""
	if existing:
		if existing.vote_type == 0 and new != 0:
			imlazy = 1
			existing.vote_type = new
			existing.coins = coin_value
			g.db.add(existing)
		elif existing.vote_type != 0 and new == 0:
			imlazy = 2
			existing_coins = existing.coins
			g.db.delete(existing)
		else:
			existing.vote_type = new
			g.db.add(existing)
	elif new != 0:
		imlazy = 3

		real = not alt and (new == -1 or v.has_real_votes)
		vote = None
		if vote_cls == Vote:
			vote = Vote(user_id=v.id,
						vote_type=new,
						post_id=target_id,
						real=real,
						coins=coin_value
			)
		elif vote_cls == CommentVote:
			vote = CommentVote(user_id=v.id,
						vote_type=new,
						comment_id=target_id,
						real=real,
						coins=coin_value
			)
		g.db.add(vote)

	# this is hacky but it works, we should probably do better later
	def get_vote_count(dir, real_instead_of_dir):
		try: g.db.flush()
		except StaleDataError:
			stop(500, "You already cancelled your vote on this!")
		except IntegrityError as e:
			if str(e).startswith('(psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint "'):
				stop(400, "You already voted on this!")
			raise
		except OperationalError as e:
			if str(e).startswith('(psycopg2.errors.QueryCanceled) canceling statement due to statement timeout'):
				stop(409, f"Statement timeout while trying to register your vote!")
			raise

		votes = g.db.query(vote_cls)
		if real_instead_of_dir:
			votes = votes.filter(vote_cls.real == True)
		else:
			votes = votes.filter(vote_cls.vote_type == dir)

		if vote_cls == Vote:
			votes = votes.filter(vote_cls.post_id == target.id)
		elif vote_cls == CommentVote:
			votes = votes.filter(vote_cls.comment_id == target.id)
		else:
			return 0

		return votes.count()

	target.upvotes = get_vote_count(1, False)
	target.downvotes = get_vote_count(-1, False)

	if SITE_NAME == 'rDrama':
		target.realupvotes = get_vote_count(0, True) # first arg is ignored here
	elif cls == Post and target.hole in {'sandshit', 'slavshit'}:
		target.realupvotes = target.upvotes
	else:
		target.realupvotes = target.upvotes - target.downvotes

	mul = 1
	if target.is_approved == PROGSTACK_ID:
		mul = PROGSTACK_MUL
	elif cls == Post and (any(i in target.title.lower() for i in ENCOURAGED) or any(i in str(target.url).lower() for i in ENCOURAGED2)):
		mul = PROGSTACK_MUL
	elif cls == Post and target.hole == 'highrollerclub':
		mul = 8
	elif cls == Post and (target.effortpost or target.hole in STEALTH_HOLES):
		mul = 5
	elif SITE == 'rdrama.net' and target.author_id == 29:
		mul = 4
	elif target.author.progressivestack or (IS_HOMOWEEN() and target.author.zombie < 0) or target.author.admin_level >= PERMS['IS_PERMA_PROGSTACKED']:
		mul = 2
	elif SITE == 'rdrama.net' and 6 <= datetime.fromtimestamp(target.created_utc).hour <= 10:
		mul = 2
	elif SITE == 'rdrama.net' and cls == Post:
		if target.hole == 'chudrama':
			mul = 3
		elif target.hole in BOOSTED_HOLES \
		or (target.domain in BOOSTED_SITES and not target.url.startswith('/')) \
		or any(i in target.domain for i in ('forum','community','board','chan','lemmy','mastodon','stackoverflow.com','stackexchange.com')):
			mul = 2
	elif target.author.new_user:
		mul = 1.25

	if target.body_html and target.author.id != SNAPPY_ID and not (cls == Post and target.hole == 'mnn'):
		x = target.body_html.count('" target="_blank" rel="nofollow noopener">')
		x += target.body_html.count('" rel="nofollow noopener" target="_blank">')
		target.realupvotes += min(x*2, 20)
		mul += min(x/10, 1)

	target.realupvotes = floor(target.realupvotes * mul)

	g.db.add(target)

	if imlazy == 1:
		target.author.pay_account('coins', coin_value)
		target.author.truescore += coin_delta
		target.coins += coin_value
	elif imlazy == 2:
		target.author.charge_account('coins', existing.coins, should_check_balance=False)
		target.author.truescore -= coin_delta
		target.coins -= coin_value
	elif imlazy == 3:
		target.author.pay_account('coins', coin_value)
		target.author.truescore += coin_delta
		target.coins += coin_value

	return ""

@app.get("/votes/<link>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def vote_info_get(v, link):
	try:
		if "p_" in link: obj = get_post(int(link.split("p_")[1]), v=v)
		elif "c_" in link: obj = get_comment(int(link.split("c_")[1]), v=v)
		else: stop(400)
	except: stop(400)

	if obj.ghost and v.admin_level < PERMS['SEE_GHOST_VOTES']:
		stop(403)

	if v.shadowbanned:
		stop(451)

	if isinstance(obj, Post):
		query = g.db.query(Vote).join(Vote.user).filter(
			Vote.post_id == obj.id,
		).order_by(Vote.created_utc)

		ups = query.filter(Vote.vote_type == 1).all()
		downs = query.filter(Vote.vote_type == -1).all()

	elif isinstance(obj, Comment):
		query = g.db.query(CommentVote).join(CommentVote.user).filter(
			CommentVote.comment_id == obj.id,
		).order_by(CommentVote.created_utc)

		ups = query.filter(CommentVote.vote_type == 1).all()
		downs = query.filter(CommentVote.vote_type == -1).all()

	else: stop(400)

	return render_template("votes.html",
						v=v,
						obj=obj,
						ups=ups,
						downs=downs)

@app.post("/vote/post/<int:post_id>/<new>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("60/minute;1000/hour;3000/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("60/minute;1000/hour;3000/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def vote_post(post_id, new, v):
	return vote_post_comment(post_id, new, v, Post, Vote)

@app.post("/vote/comment/<int:comment_id>/<new>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("60/minute;1000/hour;3000/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("60/minute;1000/hour;3000/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def vote_comment(comment_id, new, v):
	return vote_post_comment(comment_id, new, v, Comment, CommentVote)
