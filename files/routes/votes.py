from files.classes import *
from files.helpers.config.const import *
from files.helpers.config.boosted_sites import *
from files.helpers.get import *
from files.helpers.alerts import *
from files.routes.wrappers import *
from files.__main__ import app, limiter
from files.routes.routehelpers import get_alt_graph

from math import floor
from datetime import datetime

def vote_post_comment(target_id, new, v, cls, vote_cls):
	if new == "-1" and DISABLE_DOWNVOTES: abort(403)
	if new not in {"-1", "0", "1"}: abort(400)

	if request.headers.get("Authorization"):
		abort(403, "Bots aren't allowed to vote right now!")

	new = int(new)
	target = None
	if cls == Post:
		target = get_post(target_id)
	elif cls == Comment:
		target = get_comment(target_id)
		if not target.parent_post and not target.wall_user_id: abort(404)
	else:
		abort(404)

	if not User.can_see(v, target): abort(403)

	coin_delta = 1
	if v.id == target.author.id:
		coin_delta = 0

	alt = False
	if target.author.id in [x.id for x in get_alt_graph(v.id)]:
		coin_delta = -1
		alt = True

	coin_mult = 1

	existing = g.db.query(vote_cls).filter_by(user_id=v.id)
	if vote_cls == Vote:
		existing = existing.filter_by(post_id=target.id)
	elif vote_cls == CommentVote:
		existing = existing.filter_by(comment_id=target.id)
	else:
		abort(400)
	existing = existing.one_or_none()

	if SITE_NAME == 'WPD':
		coin_mult *= 4

	if IS_EVENT():
		coin_mult *= 2

	coin_value = coin_delta * coin_mult

	imlazy = 0

	if existing and existing.vote_type == new: return "", 204
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

		real = new == -1 or (not alt and v.is_votes_real)
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

		try: return votes.count()
		except: abort(500)

	target.upvotes = get_vote_count(1, False)
	target.downvotes = get_vote_count(-1, False)

	if SITE_NAME == 'rDrama':
		target.realupvotes = get_vote_count(0, True) # first arg is ignored here
	else:
		target.realupvotes = target.upvotes - target.downvotes

	mul = 1
	if target.is_approved == PROGSTACK_ID:
		mul = PROGSTACK_MUL
	elif cls == Post and (any(i in target.title.lower() for i in ENCOURAGED) or any(i in str(target.url).lower() for i in ENCOURAGED2)):
		mul = PROGSTACK_MUL
		send_notification(AEVANN_ID, target.permalink)
	elif target.author.progressivestack or (target.author.admin_level and target.author.id != SCHIZO_ID):
		mul = 2
	elif SITE == 'rdrama.net' and cls == Post:
		if (target.domain.endswith('.win')
		or 'forum' in target.domain or 'chan' in target.domain or 'lemmy' in target.domain
		or (target.domain in BOOSTED_SITES and not target.url.startswith('/'))):
			mul = 2
		elif target.sub in STEALTH_HOLES or target.sub in {'countryclub', 'highrollerclub'}:
			mul = 2
		elif 6 <= datetime.fromtimestamp(target.created_utc).hour <= 10:
			mul = 2
		elif target.sub in BOOSTED_HOLES:
			mul = 1.25

		if target.body_html and target.author.id != LNTERNETCUSTODIAN_ID:
			x = target.body_html.count('" target="_blank" rel="nofollow noopener">')
			x += target.body_html.count('" rel="nofollow noopener" target="_blank">')
			target.realupvotes += min(x*2, 20)
			mul += min(x/10, 1)
	elif SITE == 'rdrama.net' and cls == Comment and 6 <= datetime.fromtimestamp(target.created_utc).hour <= 10:
		mul = 2

	target.realupvotes = floor(target.realupvotes * mul)

	g.db.add(target)

	if imlazy == 1:
		target.author.pay_account('coins', coin_value)
		target.author.truescore += coin_delta
	elif imlazy == 2:
		target.author.charge_account('coins', existing.coins, should_check_balance=False)
		target.author.truescore -= coin_delta
	elif imlazy == 3:
		target.author.pay_account('coins', coin_value)
		target.author.truescore += coin_delta

	return "", 204

@app.get("/votes/<link>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def vote_info_get(v, link):
	try:
		if "p_" in link: thing = get_post(int(link.split("p_")[1]), v=v)
		elif "c_" in link: thing = get_comment(int(link.split("c_")[1]), v=v)
		else: abort(400)
	except: abort(400)

	if thing.ghost and v.admin_level < PERMS['SEE_GHOST_VOTES']:
		abort(403)

	if thing.author.shadowbanned and not (v and v.admin_level >= PERMS['USER_SHADOWBAN']):
		abort(500)

	if isinstance(thing, Post):
		query = g.db.query(Vote).join(Vote.user).filter(
			Vote.post_id == thing.id,
		).order_by(Vote.created_utc)

		ups = query.filter(Vote.vote_type == 1).all()
		downs = query.filter(Vote.vote_type == -1).all()

	elif isinstance(thing, Comment):
		query = g.db.query(CommentVote).join(CommentVote.user).filter(
			CommentVote.comment_id == thing.id,
		).order_by(CommentVote.created_utc)

		ups = query.filter(CommentVote.vote_type == 1).all()
		downs = query.filter(CommentVote.vote_type == -1).all()

	else: abort(400)

	return render_template("votes.html",
						v=v,
						thing=thing,
						ups=ups,
						downs=downs)

@app.post("/vote/post/<int:post_id>/<new>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("60/minute;1000/hour;2000/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("60/minute;1000/hour;2000/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@is_not_permabanned
def vote_post(post_id, new, v):
	return vote_post_comment(post_id, new, v, Post, Vote)

@app.post("/vote/comment/<int:comment_id>/<new>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("60/minute;1000/hour;2000/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("60/minute;1000/hour;2000/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@is_not_permabanned
def vote_comment(comment_id, new, v):
	return vote_post_comment(comment_id, new, v, Comment, CommentVote)
