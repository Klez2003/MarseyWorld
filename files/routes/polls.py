from files.classes import *
from files.helpers.config.const import *
from files.helpers.get import *
from files.routes.wrappers import *
from files.__main__ import app


@app.post("/vote/post/option/<int:option_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def vote_option(option_id, v):
	try:
		option_id = int(option_id)
	except:
		stop(404)
	option = g.db.get(PostOption, option_id)
	if not option: stop(404)
	hole = option.parent.hole

	if hole in {'furry','vampire','racist','femboy','edgy'} and not v.house.lower().startswith(hole):
		stop(403, f"You need to be a member of House {hole.capitalize()} to vote on polls in /h/{hole}")

	if option.exclusive == 2:
		if option.parent.total_bet_voted(v):
			stop(403, "You can't participate in a closed bet!")
		if not v.charge_account('coins/marseybux', POLL_BET_COINS, f"Cost of bet on {option.parent.textlink}"):
			stop(400, f"You don't have {POLL_BET_COINS} coins or marseybux!")
		g.db.add(v)

	if option.exclusive:
		vote = g.db.query(PostOptionVote).join(PostOption).filter(
			PostOptionVote.user_id==v.id,
			PostOptionVote.post_id==option.parent_id,
			PostOption.exclusive==option.exclusive).all()
		if vote:
			if option.exclusive == 2: stop(400, "You already voted on this bet!")
			for x in vote:
				g.db.delete(x)

	g.db.flush()
	existing = g.db.query(PostOptionVote).filter_by(option_id=option_id, user_id=v.id).one_or_none()
	if not existing:
		vote = PostOptionVote(
			option_id=option_id,
			user_id=v.id,
			post_id=option.parent_id,
		)
		g.db.add(vote)
	elif existing and not option.exclusive:
		g.db.delete(existing)

	return {"message": "Bet successful!"}

@app.post("/vote/comment/option/<int:option_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def vote_option_comment(option_id, v):
	try:
		option_id = int(option_id)
	except:
		stop(404)
	option = g.db.get(CommentOption, option_id)
	if not option: stop(404)

	if option.parent.parent_post:
		hole = option.parent.post.hole
	else:
		hole = None

	if hole in {'furry','vampire','racist','femboy','edgy'} and not v.house.lower().startswith(hole):
		stop(403, f"You need to be a member of House {hole.capitalize()} to vote on polls in /h/{hole}")

	if option.exclusive == 2:
		if option.parent.total_bet_voted(v):
			stop(403, "You can't participate in a closed bet!")
		if not v.charge_account('coins/marseybux', POLL_BET_COINS, f"Cost of bet on {option.parent.textlink}"):
			stop(400, f"You don't have {POLL_BET_COINS} coins or marseybux!")
		g.db.add(v)

	if option.exclusive:
		vote = g.db.query(CommentOptionVote).join(CommentOption).filter(
			CommentOptionVote.user_id==v.id,
			CommentOptionVote.comment_id==option.parent_id,
			CommentOption.exclusive==option.exclusive).all()
		if vote:
			if option.exclusive == 2: stop(400, "You already voted on this bet!")
			for x in vote:
				g.db.delete(x)

	g.db.flush()
	existing = g.db.query(CommentOptionVote).filter_by(option_id=option_id, user_id=v.id).one_or_none()
	if not existing:
		vote = CommentOptionVote(
			option_id=option_id,
			user_id=v.id,
			comment_id=option.parent_id,
		)
		g.db.add(vote)
	elif existing:
		g.db.delete(existing)

	return {"message": "Bet successful!"}


@app.get("/votes/post/option/<int:option_id>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def option_votes(option_id, v):
	try:
		option_id = int(option_id)
	except:
		stop(404)
	option = g.db.get(PostOption, option_id)
	if not option: stop(404)

	if option.parent.ghost and v.admin_level < PERMS['SEE_GHOST_VOTES']:
		stop(403)

	ups = g.db.query(PostOptionVote).filter_by(option_id=option_id).order_by(PostOptionVote.created_utc).all()

	user_ids = [x[0] for x in g.db.query(PostOptionVote.user_id).filter_by(option_id=option_id)]
	total_ts = g.db.query(func.sum(User.truescore)).filter(User.id.in_(user_ids)).scalar()
	total_ts = format(total_ts, ",") if total_ts else '0'

	if v.admin_level >= PERMS['VIEW_PATRONS']:
		patrons = [x[0] for x in g.db.query(User.patron).filter(User.id.in_(user_ids - [AEVANN_ID, CARP_ID, JOAN_ID]), User.patron > 1)]
		total_patrons = len(patrons)
		total_money = 0
		for tier in patrons:
			total_money += TIER_TO_MONEY[tier]
	else:
		total_patrons = None
		total_money = 0

	return render_template("poll_votes.html",
						v=v,
						option=option,
						ups=ups,
						total_ts=total_ts,
						total_patrons=total_patrons,
						total_money=total_money,
						)


@app.get("/votes/comment/option/<int:option_id>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def option_votes_comment(option_id, v):
	try:
		option_id = int(option_id)
	except:
		stop(404)
	option = g.db.get(CommentOption, option_id)

	if not option: stop(404)

	if option.parent.ghost and v.admin_level < PERMS['SEE_GHOST_VOTES']:
		stop(403)

	ups = g.db.query(CommentOptionVote).filter_by(option_id=option_id).order_by(CommentOptionVote.created_utc).all()

	user_ids = [x[0] for x in g.db.query(CommentOptionVote.user_id).filter_by(option_id=option_id)]
	total_ts = g.db.query(func.sum(User.truescore)).filter(User.id.in_(user_ids)).scalar()
	total_ts = format(total_ts, ",") if total_ts else '0'

	if v.admin_level >= PERMS['VIEW_PATRONS']:
		patrons = [x[0] for x in g.db.query(User.patron).filter(User.id.in_(user_ids - [AEVANN_ID, CARP_ID, JOAN_ID]), User.patron > 1)]
		total_patrons = len(patrons)
		total_money = 0
		for tier in patrons:
			total_money += TIER_TO_MONEY[tier]
	else:
		total_patrons = None
		total_money = 0

	return render_template("poll_votes.html",
						v=v,
						option=option,
						ups=ups,
						total_ts=total_ts,
						total_patrons=total_patrons,
						total_money=total_money,
						)
