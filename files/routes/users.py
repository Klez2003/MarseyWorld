import io
import json
import math
import time
from collections import Counter

import gevent
import qrcode
from sqlalchemy.orm import aliased, load_only
from sqlalchemy.exc import IntegrityError

from files.classes import *
from files.classes.leaderboard import Leaderboard
from files.classes.transactions import *
from files.classes.views import *
from files.helpers.actions import execute_under_siege
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.mail import *
from files.helpers.sanitize import *
from files.helpers.sorting_and_time import *
from files.helpers.useractions import badge_grant
from files.routes.routehelpers import check_for_alts, add_alt
from files.routes.wrappers import *
from files.routes.comments import _mark_comment_as_read

from files.__main__ import app, cache, limiter

def _add_profile_view(vid, uid):
	db = db_session()

	view = db.query(ViewerRelationship).options(load_only(ViewerRelationship.viewer_id)).filter_by(viewer_id=vid, user_id=uid).one_or_none()

	if view: view.last_view_utc = int(time.time())
	else: view = ViewerRelationship(viewer_id=vid, user_id=uid)
	db.add(view)

	try:
		db.commit()
	except IntegrityError as e:
		db.rollback()
		if not str(e).startswith('(psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint "'):
			print(STARS + e + STARS, flush=True)

	db.close()
	stdout.flush()

def claim_rewards_all_users():
	emails = [x[0] for x in g.db.query(Transaction.email).filter_by(claimed=None)]
	users = g.db.query(User).filter(User.email.in_(emails)).order_by(User.truescore.desc()).all()
	for user in users:
		g.db.flush()
		transactions = g.db.query(Transaction).filter_by(email=user.email, claimed=None).all()

		highest_tier = 0
		marseybux = 0

		for transaction in transactions:
			for t, money in TIER_TO_MONEY.items():
				tier = t
				if transaction.amount <= money: break

			marseybux += TIER_TO_MBUX[tier]
			if tier > highest_tier:
				highest_tier = tier
			transaction.claimed = True
			g.db.add(transaction)

		if marseybux:
			user.pay_account('marseybux', marseybux)

			send_repeatable_notification(user.id, f"You have received {marseybux} Marseybux! You can use them to buy awards or hats in the [shop](/shop/awards) or gamble them in the [casino](/casino).")
			g.db.add(user)

			user.patron_utc = int(time.time()) + 2937600

			if highest_tier > user.patron:
				user.patron = highest_tier
				badge_id = 20 + highest_tier

				badges_to_remove = g.db.query(Badge).filter(
						Badge.user_id == user.id,
						Badge.badge_id > badge_id,
						Badge.badge_id < 29,
					).all()
				for badge in badges_to_remove:
					g.db.delete(badge)

				for x in range(22, badge_id+1):
					badge_grant(badge_id=x, user=user)

			g.db.flush()
			user.lifetimedonated = g.db.query(func.sum(Transaction.amount)).filter_by(email=user.email).scalar()

			if user.lifetimedonated >= 100:
				badge_grant(badge_id=257, user=user)

			if user.lifetimedonated >= 500:
				badge_grant(badge_id=258, user=user)

			if user.lifetimedonated >= 2500:
				badge_grant(badge_id=259, user=user)

			if user.lifetimedonated >= 5000:
				badge_grant(badge_id=260, user=user)

			if user.lifetimedonated >= 10000:
				badge_grant(badge_id=261, user=user)

			print(f'@{user.username} rewards claimed successfully!', flush=True)

	for user in g.db.query(User).options(load_only(User.id)).order_by(User.lifetimedonated.desc()).limit(10):
		badge_grant(badge_id=294, user=user)

def transfer_currency(v, username, currency_name, apply_tax):
	MIN_CURRENCY_TRANSFER = 100
	TAX_PCT = 0.03
	receiver = get_user(username, v=v)
	if receiver.id == v.id: abort(400, f"You can't transfer {currency_name} to yourself!")
	amount = request.values.get("amount", "").strip()
	amount = int(amount) if amount.isdigit() else None

	if amount is None or amount <= 0: abort(400, f"Invalid number of {currency_name}")
	if amount < MIN_CURRENCY_TRANSFER: abort(400, f"You have to gift at least {MIN_CURRENCY_TRANSFER} {currency_name}")
	tax = 0
	if apply_tax and not v.patron and not receiver.patron:
		tax = math.ceil(amount*TAX_PCT)

	reason = request.values.get("reason", "").strip()
	log_message = f"@{v.username} has transferred {amount} {currency_name} to @{receiver.username}"
	notif_text = f":marseycapitalistmanlet: @{v.username} has gifted you {amount-tax} {currency_name}!"

	if reason:
		if len(reason) > TRANSFER_MESSAGE_LENGTH_LIMIT:
			abort(400, f"Reason is too long, max {TRANSFER_MESSAGE_LENGTH_LIMIT} characters")
		notif_text += f"\n\n> {reason}"
		log_message += f"\n\n> {reason}"

	if not v.charge_account(currency_name, amount)[0]:
		abort(400, f"You don't have enough {currency_name}")

	if not v.shadowbanned:
		if currency_name == 'marseybux':
			receiver.pay_account('marseybux', amount - tax)
		elif currency_name == 'coins':
			receiver.pay_account('coins', amount - tax)
		else:
			raise ValueError(f"Invalid currency '{currency_name}' got when transferring {amount} from {v.id} to {receiver.id}")
		if GIFT_NOTIF_ID: send_repeatable_notification(GIFT_NOTIF_ID, log_message)
		send_repeatable_notification(receiver.id, notif_text)
	g.db.add(v)
	return {"message": f"{amount - tax} {currency_name} have been transferred to @{receiver.username}"}

def upvoters_downvoters(v, username, username2, cls, vote_cls, vote_dir, template, standalone):
	u = get_user(username, v=v)
	if not u.is_visible_to(v): abort(403)
	id = u.id

	uid = get_user(username2, attributes=[User.id]).id

	page = get_page()

	listing = g.db.query(cls).options(load_only(cls.id)).join(vote_cls).filter(
			cls.ghost == False,
			cls.is_banned == False,
			cls.deleted_utc == 0,
			vote_cls.vote_type==vote_dir,
			cls.author_id==id,
			vote_cls.user_id==uid,
		)

	total = listing.count()

	listing = listing.order_by(cls.created_utc.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()
	listing = [x.id for x in listing]

	if cls == Post:
		listing = get_posts(listing, v=v)
	elif cls == Comment:
		listing = get_comments(listing, v=v)
	else:
		listing = []

	return render_template(template, total=total, listing=listing, page=page, v=v, standalone=standalone)

@app.get("/@<username>/upvoters/@<username2>/posts")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def upvoters_posts(v, username, username2):
	return upvoters_downvoters(v, username, username2, Post, Vote, 1, "userpage/voted_posts.html", None)


@app.get("/@<username>/upvoters/@<username2>/comments")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def upvoters_comments(v, username, username2):
	return upvoters_downvoters(v, username, username2, Comment, CommentVote, 1, "userpage/voted_comments.html", True)


@app.get("/@<username>/downvoters/@<username2>/posts")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def downvoters_posts(v, username, username2):
	return upvoters_downvoters(v, username, username2, Post, Vote, -1, "userpage/voted_posts.html", None)


@app.get("/@<username>/downvoters/@<username2>/comments")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def downvoters_comments(v, username, username2):
	return upvoters_downvoters(v, username, username2, Comment, CommentVote, -1, "userpage/voted_comments.html", True)

def upvoting_downvoting(v, username, username2, cls, vote_cls, vote_dir, template, standalone):
	u = get_user(username, v=v)
	if not u.is_visible_to(v): abort(403)
	id = u.id

	uid = get_user(username2, attributes=[User.id]).id

	page = get_page()

	listing = g.db.query(cls).options(load_only(cls.id)).join(vote_cls).filter(
			cls.ghost == False,
			cls.is_banned == False,
			cls.deleted_utc == 0,
			vote_cls.vote_type==vote_dir,
			vote_cls.user_id==id,
			cls.author_id==uid,
		)

	total = listing.count()

	listing = listing.order_by(cls.created_utc.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()
	listing = [x.id for x in listing]

	if cls == Post:
		listing = get_posts(listing, v=v)
	elif cls == Comment:
		listing = get_comments(listing, v=v)
	else:
		listing = []

	return render_template(template, total=total, listing=listing, page=page, v=v, standalone=standalone)

@app.get("/@<username>/upvoting/@<username2>/posts")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def upvoting_posts(v, username, username2):
	return upvoting_downvoting(v, username, username2, Post, Vote, 1, "userpage/voted_posts.html", None)


@app.get("/@<username>/upvoting/@<username2>/comments")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def upvoting_comments(v, username, username2):
	return upvoting_downvoting(v, username, username2, Comment, CommentVote, 1, "userpage/voted_comments.html", True)


@app.get("/@<username>/downvoting/@<username2>/posts")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def downvoting_posts(v, username, username2):
	return upvoting_downvoting(v, username, username2, Post, Vote, -1, "userpage/voted_posts.html", None)


@app.get("/@<username>/downvoting/@<username2>/comments")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def downvoting_comments(v, username, username2):
	return upvoting_downvoting(v, username, username2, Comment, CommentVote, -1, "userpage/voted_comments.html", True)

def user_voted(v, username, cls, vote_cls, template, standalone):
	u = get_user(username, v=v)
	if not u.is_visible_to(v): abort(403)

	page = get_page()

	listing = g.db.query(cls).join(vote_cls).filter(
			cls.ghost == False,
			cls.is_banned == False,
			cls.deleted_utc == 0,
			cls.author_id != u.id,
			vote_cls.user_id == u.id,
		)

	total = listing.count()

	listing = listing.order_by(vote_cls.created_utc.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()
	listing = [x.id for x in listing]

	if cls == Post:
		listing = get_posts(listing, v=v)
	elif cls == Comment:
		listing = get_comments(listing, v=v)
	else:
		listing = []

	return render_template(template, total=total, listing=listing, page=page, v=v, standalone=standalone)

@app.get("/@<username>/voted/posts")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def user_voted_posts(v, username):
	return user_voted(v, username, Post, Vote, "userpage/voted_posts.html", None)


@app.get("/@<username>/voted/comments")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def user_voted_comments(v, username):
	return user_voted(v, username, Comment, CommentVote, "userpage/voted_comments.html", True)

@app.get("/banned")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def banned(v):
	users = g.db.query(User).filter(
		User.is_banned != None,
		or_(User.unban_utc == 0, User.unban_utc > time.time()),
	).order_by(User.ban_reason)

	users = users.all()
	return render_template("banned.html", v=v, users=users)

@app.get("/grassed")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def grassed(v):
	users = g.db.query(User).filter(
		User.ban_reason.like('grass award used by @%'),
		User.unban_utc > time.time(),
	)

	users = users.all()
	return render_template("grassed.html", v=v, users=users)

@app.get("/chuds")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def chuds(v):
	users = g.db.query(User).filter(
		or_(User.chud == 1, User.chud > time.time()),
	)
	if v.admin_level >= PERMS['VIEW_LAST_ACTIVE']:
		users = users.order_by(User.truescore.desc())

	users = users.order_by(User.username).all()
	return render_template("chuds.html", v=v, users=users)

def all_upvoters_downvoters(v, username, vote_dir, is_who_simps_hates):
	if username == 'Snappy':
		abort(403, "For performance reasons, you can't see Snappy's statistics!")
	vote_str = 'votes'
	simps_haters = 'voters'
	vote_name = 'Neutral'
	if vote_dir == 1:
		vote_str = 'upvotes'
		simps_haters = 'simps for' if is_who_simps_hates else 'simps'
		vote_name = 'Up'
	elif vote_dir == -1:
		vote_str = 'downvotes'
		simps_haters = 'hates' if is_who_simps_hates else 'haters'
		vote_name = 'Down'

	id = get_user(username, v=v).id
	votes = []
	votes2 = []
	if is_who_simps_hates:
		votes = g.db.query(Post.author_id, func.count(Post.author_id)).join(Vote).filter(Post.ghost == False, Post.is_banned == False, Post.deleted_utc == 0, Vote.vote_type==vote_dir, Vote.user_id==id).group_by(Post.author_id).order_by(func.count(Post.author_id).desc()).all()
		votes2 = g.db.query(Comment.author_id, func.count(Comment.author_id)).join(CommentVote).filter(Comment.ghost == False, Comment.is_banned == False, Comment.deleted_utc == 0, CommentVote.vote_type==vote_dir, CommentVote.user_id==id).group_by(Comment.author_id).order_by(func.count(Comment.author_id).desc()).all()
	else:
		votes = g.db.query(Vote.user_id, func.count(Vote.user_id)).join(Post).filter(Post.ghost == False, Post.is_banned == False, Post.deleted_utc == 0, Vote.vote_type==vote_dir, Post.author_id==id).group_by(Vote.user_id).order_by(func.count(Vote.user_id).desc()).all()
		votes2 = g.db.query(CommentVote.user_id, func.count(CommentVote.user_id)).join(Comment).filter(Comment.ghost == False, Comment.is_banned == False, Comment.deleted_utc == 0, CommentVote.vote_type==vote_dir, Comment.author_id==id).group_by(CommentVote.user_id).order_by(func.count(CommentVote.user_id).desc()).all()
	votes = Counter(dict(votes)) + Counter(dict(votes2))
	total_items = sum(votes.values())

	users = g.db.query(User).filter(User.id.in_(votes.keys()))
	users = [(user, votes[user.id]) for user in users]
	users = sorted(users, key=lambda x: x[1], reverse=True)

	try:
		pos = [x[0].id for x in users].index(v.id)
		pos = (pos+1, users[pos][1])
	except: pos = (len(users)+1, 0)

	received_given = 'given' if is_who_simps_hates else 'received'
	if total_items == 1: vote_str = vote_str[:-1] # we want to unpluralize if only 1 vote
	total_items = f'{total_items} {vote_str} {received_given}'

	name2 = f'Who @{username} {simps_haters}' if is_who_simps_hates else f"@{username}'s {simps_haters}"

	page = get_page()

	total = len(users)

	users = users[PAGE_SIZE*(page-1):]
	users = users[:PAGE_SIZE]

	return render_template("userpage/voters.html", v=v, users=users, pos=pos, name=vote_name, name2=name2, page=page, total_items=total_items, total=total)

@app.get("/@<username>/upvoters")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def upvoters(v, username):
	return all_upvoters_downvoters(v, username, 1, False)

@app.get("/@<username>/downvoters")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def downvoters(v, username):
	return all_upvoters_downvoters(v, username, -1, False)

@app.get("/@<username>/upvoting")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def upvoting(v, username):
	return all_upvoters_downvoters(v, username, 1, True)

@app.get("/@<username>/downvoting")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def downvoting(v, username):
	return all_upvoters_downvoters(v, username, -1, True)

@app.post("/@<username>/suicide")
@feature_required('USERS_SUICIDE')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("5/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("5/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def suicide(v, username):
	user = get_user(username)
	suicide = f"Hi there,\n\nA [concerned user](/id/{v.id}) reached out to us about you.\n\nWhen you're in the middle of something painful, it may feel like you don't have a lot of options. But whatever you're going through, you deserve help and there are people who are here for you.\n\nThere are resources available in your area that are free, confidential, and available 24/7:\n\n- Call, Text, or Chat with Canada's [Crisis Services Canada](https://www.crisisservicescanada.ca/en/)\n\n- Call, Email, or Visit the UK's [Samaritans](https://www.samaritans.org/)\n\n- Text CHAT to America's [Crisis Text Line](https://www.crisistextline.org/) at 741741.\n\nIf you don't see a resource in your area above, the moderators keep a comprehensive list of resources and hotlines for people organized by location. Find Someone Now\n\nIf you think you may be depressed or struggling in another way, don't ignore it or brush it aside. Take yourself and your feelings seriously, and reach out to someone.\n\nIt may not feel like it, but you have options. There are people available to listen to you, and ways to move forward.\n\nYour fellow users care about you and there are people who want to help."
	if not v.shadowbanned:
		send_notification(user.id, suicide)
	return {"message": f"Help message sent to @{user.username}"}


@app.get("/@<username>/coins")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def get_coins(v, username):
	user = get_user(username, v=v)
	return {"coins": user.coins}

@app.post("/@<username>/transfer_coins")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@is_not_permabanned
def transfer_coins(v, username):
	return transfer_currency(v, username, 'coins', True)

@app.post("/@<username>/transfer_bux")
@feature_required('MARSEYBUX')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@is_not_permabanned
def transfer_bux(v, username):
	return transfer_currency(v, username, 'marseybux', False)

@cache.memoize()
def leaderboard_cached(v):
	users = g.db.query(User)

	coins = Leaderboard("Coins", "coins", "coins", "Coins", None, Leaderboard.get_simple_lb, User.coins, v, lambda u:u.coins, users)
	marseybux = Leaderboard("Marseybux", "marseybux", "marseybux", "Marseybux", None, Leaderboard.get_simple_lb, User.marseybux, v, lambda u:u.marseybux, users)
	subscribers = Leaderboard("Followers", "followers", "followers", "Followers", "followers", Leaderboard.get_simple_lb, User.stored_subscriber_count, v, lambda u:u.stored_subscriber_count, users)
	posts = Leaderboard("Posts", "post count", "posts", "Posts", "posts", Leaderboard.get_simple_lb, User.post_count, v, lambda u:u.post_count, users)
	comments = Leaderboard("Comments", "comment count", "comments", "Comments", "comments", Leaderboard.get_simple_lb, User.comment_count, v, lambda u:u.comment_count, users)
	received_awards = Leaderboard("Received awards", "received awards", "received-awards", "Received Awards", None, Leaderboard.get_simple_lb, User.received_award_count, v, lambda u:u.received_award_count, users)
	coins_spent = Leaderboard("Coins spent on awards", "coins spent on awards", "spent", "Coins", None, Leaderboard.get_simple_lb, User.coins_spent, v, lambda u:u.coins_spent, users)
	truescore = Leaderboard("Truescore", "truescore", "truescore", "Truescore", None, Leaderboard.get_simple_lb, User.truescore, v, lambda u:u.truescore, users)

	badges = Leaderboard("Badges", "badges", "badges", "Badges", None, Leaderboard.get_badge_emoji_lb, Badge.user_id, v, None, None)

	blocks = Leaderboard("Most blocked", "most blocked", "most-blocked", "Blocked By", "blockers", Leaderboard.get_blockers_lb, UserBlock.target_id, v, None, None)

	owned_hats = Leaderboard("Owned hats", "owned hats", "owned-hats", "Owned Hats", None, Leaderboard.get_hat_lb, User.owned_hats, v, None, None)

	leaderboards = [coins, marseybux, coins_spent, truescore, subscribers, posts, comments, received_awards, badges, blocks, owned_hats]

	if SITE == 'rdrama.net':
		leaderboards.append(Leaderboard("Designed hats", "designed hats", "designed-hats", "Designed Hats", None, Leaderboard.get_hat_lb, User.designed_hats, v, None, None))
		leaderboards.append(Leaderboard("Emojis made", "emojis made", "emojis-made", "Emojis", None, Leaderboard.get_badge_emoji_lb, Emoji.author_id, v, None, None))

	leaderboards.append(Leaderboard("Upvotes given", "upvotes given", "upvotes-given", "Upvotes Given", "upvoting", Leaderboard.get_upvotes_lb, None, v, None, None))

	leaderboards.append(Leaderboard("Downvotes received", "downvotes received", "downvotes-received", "Downvotes Received", "downvoters", Leaderboard.get_downvotes_lb, None, v, None, None))

	leaderboards.append(Leaderboard("Casino winnings (top)", "casino winnings", "casino-winnings-top", "Casino Winnings", None, Leaderboard.get_winnings_lb, CasinoGame.winnings, v, None, None))
	leaderboards.append(Leaderboard("Casino winnings (bottom)", "casino winnings", "casino-winnings-bottom", "Casino Winnings", None, Leaderboard.get_winnings_lb, CasinoGame.winnings, v, None, None, 25, False))

	return render_template("leaderboard_cached.html", v=v, leaderboards=leaderboards)

@app.get("/leaderboard")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard(v):
	return render_template("leaderboard.html", v=v, leaderboard_cached=leaderboard_cached(v))

@app.get("/@<username>/css")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
def get_css(username):
	user = get_user(username, attributes=[User.css, User.background])

	css = user.css
	bg = user.background

	if bg:
		if not css: css = ''
		css += f'''
			body {{
				background: url("{bg}") center center fixed;
			}}
		'''
		if 'anime/' not in bg and not bg.startswith('/images/'):
			css += 'body {background-size: cover}'

	if not css: abort(404)

	resp = make_response(css)
	resp.headers["Content-Type"] = "text/css"
	return resp

@app.get("/@<username>/profilecss")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
def get_profilecss(username):
	user = get_user(username, attributes=[User.profilecss, User.profile_background])

	css = user.profilecss
	bg = user.profile_background

	if bg:
		if not css: css = ''
		css += f'''
			body {{
				background: url("{bg}") center center fixed;
				background-size: auto;
			}}
		'''
	if not css: abort(404)

	resp = make_response(css)
	resp.headers["Content-Type"] = "text/css"
	return resp

@app.get("/@<username>/song")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
def usersong(username):
	user = get_user(username)
	if not user.song:
		abort(404)

	resp = make_response(redirect(f"/songs/{user.song}.mp3"))
	resp.headers["Cache-Control"] = "no-store"
	return resp


@app.post("/subscribe/<int:post_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def subscribe(v, post_id):
	existing = g.db.query(Subscription).filter_by(user_id=v.id, post_id=post_id).one_or_none()
	if not existing:
		new_sub = Subscription(user_id=v.id, post_id=post_id)
		g.db.add(new_sub)
		cache.delete_memoized(userpagelisting)
	return {"message": "Subscribed to post successfully!"}

@app.post("/unsubscribe/<int:post_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def unsubscribe(v, post_id):
	existing = g.db.query(Subscription).filter_by(user_id=v.id, post_id=post_id).one_or_none()
	if existing:
		g.db.delete(existing)
		cache.delete_memoized(userpagelisting)
	return {"message": "Unsubscribed from post successfully!"}

@app.post("/@<username>/message")
@app.post("/id/<int:id>/message")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("10/minute;20/hour;50/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("10/minute;20/hour;50/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@is_not_permabanned
def message2(v, username=None, id=None):
	if id:
		user = get_account(id, v=v, include_blocks=True)
	else:
		user = get_user(username, v=v, include_blocks=True)

	if user.id == MODMAIL_ID:
		abort(403, "Please use /contact to contact the admins")

	if hasattr(user, 'is_blocking') and user.is_blocking:
		abort(403, f"You're blocking @{user.username}")

	if v.admin_level <= PERMS['MESSAGE_BLOCKED_USERS'] and hasattr(user, 'is_blocked') and user.is_blocked:
		abort(403, f"@{user.username} is blocking you!")

	if user.has_muted(v):
			abort(403, f"@{user.username} is muting notifications from you, so messaging them is pointless!")

	body = request.values.get("message", "")
	body = body[:COMMENT_BODY_LENGTH_LIMIT].strip()

	if not g.is_tor and get_setting("dm_media"):
		body = process_files(request.files, v, body, is_dm=True, dm_user=user)
		body = body[:COMMENT_BODY_LENGTH_LIMIT].strip() #process_files potentially adds characters to the post

	if not body: abort(400, "Message is empty!")

	body_html = sanitize(body)

	existing = g.db.query(Comment.id).filter(
		Comment.author_id == v.id,
		Comment.sentto == user.id,
		Comment.body_html == body_html
	).first()

	if existing: abort(403, "Message already exists!")

	c = Comment(author_id=v.id,
						parent_post=None,
						level=1,
						sentto=user.id,
						body=body,
						body_html=body_html
						)
	g.db.add(c)
	g.db.flush()
	execute_blackjack(v, c, c.body_html, 'message')
	execute_under_siege(v, c, c.body_html, 'message')
	c.top_comment_id = c.id

	if user.id not in BOT_IDs:
		g.db.flush()
		notif = g.db.query(Notification).filter_by(comment_id=c.id, user_id=user.id).one_or_none()
		if not notif:
			notif = Notification(comment_id=c.id, user_id=user.id)
			g.db.add(notif)


	title = f'New message from @{c.author_name}'

	url = f'{SITE_FULL}/notifications/messages'

	push_notif({user.id}, title, body, url)

	return {"message": "Message sent!"}


@app.post("/reply")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("6/minute;50/hour;200/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("6/minute;50/hour;200/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def messagereply(v):
	body = request.values.get("body", "")
	body = body[:COMMENT_BODY_LENGTH_LIMIT].strip()

	id = request.values.get("parent_id")
	parent = get_comment(id, v=v)

	if parent.parent_post or parent.wall_user_id:
		abort(403, "You can only reply to messages!")

	user_id = parent.author.id

	if v.is_permabanned and parent.sentto != MODMAIL_ID:
		abort(403, "You are permabanned and may not reply to messages!")
	elif v.is_muted and parent.sentto == MODMAIL_ID:
		abort(403, "You are forbidden from replying to modmail!")

	if parent.sentto == MODMAIL_ID: user_id = None
	elif v.id == user_id: user_id = parent.sentto

	user = None

	if user_id:
		user = get_account(user_id, v=v, include_blocks=True)
		if hasattr(user, 'is_blocking') and user.is_blocking:
			abort(403, f"You're blocking @{user.username}")
		elif (v.admin_level <= PERMS['MESSAGE_BLOCKED_USERS']
				and hasattr(user, 'is_blocked') and user.is_blocked):
			abort(403, f"You're blocked by @{user.username}")

		if user.has_muted(v):
			abort(403, f"@{user.username} is muting notifications from you, so messaging them is pointless!")

	if not g.is_tor and get_setting("dm_media"):
		body = process_files(request.files, v, body, is_dm=True, dm_user=user)
		body = body[:COMMENT_BODY_LENGTH_LIMIT].strip() #process_files potentially adds characters to the post

	if not body: abort(400, "Message is empty!")

	body_html = sanitize(body)

	if len(body_html) > COMMENT_BODY_HTML_LENGTH_LIMIT:
		abort(400, "Message too long!")

	if parent.sentto == MODMAIL_ID:
		sentto = MODMAIL_ID
	else:
		sentto = user_id

	c = Comment(author_id=v.id,
							parent_post=None,
							parent_comment_id=id,
							top_comment_id=parent.top_comment_id,
							level=parent.level + 1,
							sentto=sentto,
							body=body,
							body_html=body_html,
							)
	g.db.add(c)
	g.db.flush()
	execute_blackjack(v, c, c.body_html, 'message')
	execute_under_siege(v, c, c.body_html, 'message')

	if user_id and user_id not in {v.id, MODMAIL_ID} | BOT_IDs:
		notif = g.db.query(Notification).filter_by(comment_id=c.id, user_id=user_id).one_or_none()
		if not notif:
			notif = Notification(comment_id=c.id, user_id=user_id)
			g.db.add(notif)

		title = f'New message from @{c.author_name}'

		url = f'{SITE_FULL}/notifications/messages'

		push_notif({user_id}, title, body, url)

	top_comment = c.top_comment

	if top_comment.sentto == MODMAIL_ID:
		admin_ids = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS['NOTIFICATIONS_MODMAIL'], User.id != v.id)]

		if SITE == 'watchpeopledie.tv':
			if AEVANN_ID in admin_ids:
				admin_ids.remove(AEVANN_ID)
			if 'delete' in top_comment.body.lower() and 'account' in top_comment.body.lower():
				admin_ids.remove(15447)

		if parent.author.id not in admin_ids + [v.id]:
			admin_ids.append(parent.author.id)

		#Don't delete unread notifications, so the replies don't get collapsed and they get highlighted
		ids = [top_comment.id] + [x.id for x in top_comment.replies(sort="old")]
		notifications = g.db.query(Notification).filter(Notification.read == True, Notification.comment_id.in_(ids), Notification.user_id.in_(admin_ids))
		for n in notifications:
			g.db.delete(n)

		for admin in admin_ids:
			notif = Notification(comment_id=c.id, user_id=admin)
			g.db.add(notif)

	return {"comment": render_template("comments.html", v=v, comments=[c])}

@app.get("/2faqr/<secret>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def mfa_qr(v, secret):
	x = pyotp.TOTP(secret)
	qr = qrcode.QRCode(
		error_correction=qrcode.constants.ERROR_CORRECT_L
	)
	qr.add_data(x.provisioning_uri(v.username, issuer_name=SITE))
	img = qr.make_image(fill_color="#000000", back_color="white")

	mem = io.BytesIO()

	img.save(mem, format="PNG")
	mem.seek(0, 0)

	return send_file(mem, mimetype="image/png", as_attachment=False)


@app.get("/is_available/<name>")
@limiter.limit("100/day", deduct_when=lambda response: response.status_code < 400)
def is_available(name):

	name = name.strip()

	if len(name)<3 or len(name)>25:
		return {name:False}

	name2 = name.replace('\\', '').replace('_','\_').replace('%','')

	x = g.db.query(User).filter(
		or_(
			User.username.ilike(name2),
			User.original_username.ilike(name2),
			User.prelock_username.ilike(name2),
			)
		).one_or_none()

	if x:
		return {name: False}
	else:
		return {name: True}

@app.get("/id/<int:id>")
@app.route("/id/<int:id>/<path:path>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def user_id(v, id, path=''):
	user = get_account(id)
	if path:
		return redirect(f'/@{user.username}/{path}')
	return redirect(f'/@{user.username}')

@app.get("/u/<username>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def redditor_moment_redirect(v, username):
	return redirect(f"/@{username}")

@app.get("/@<username>/blockers")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def blockers(v, username):
	u = get_user(username, v=v)

	page = get_page()

	users = g.db.query(UserBlock, User).join(UserBlock, UserBlock.target_id == u.id) \
		.filter(UserBlock.user_id == User.id)

	total = users.count()

	users = users.order_by(UserBlock.created_utc.desc()) \
		.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE ).all()

	return render_template("userpage/blockers.html", v=v, u=u, users=users, page=page, total=total)

@app.get("/@<username>/blocking")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def blocking(v, username):
	u = get_user(username, v=v)

	page = get_page()

	users = g.db.query(UserBlock, User).join(UserBlock, UserBlock.user_id == u.id) \
		.filter(UserBlock.target_id == User.id)

	total = users.count()

	users = users.order_by(UserBlock.created_utc.desc()) \
		.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE ).all()

	return render_template("userpage/blocking.html", v=v, u=u, users=users, page=page, total=total)

@app.get("/@<username>/muters")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def muters(v, username):
	u = get_user(username, v=v)

	page = get_page()

	users = g.db.query(UserMute, User).join(UserMute, UserMute.target_id == u.id) \
		.filter(UserMute.user_id == User.id)

	total = users.count()

	users = users.order_by(UserMute.created_utc.desc()) \
		.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE ).all()

	return render_template("userpage/muters.html", v=v, u=u, users=users, page=page, total=total)

@app.get("/@<username>/muting")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def muting(v, username):
	u = get_user(username, v=v)

	page = get_page()

	users = g.db.query(UserMute, User).join(UserMute, UserMute.user_id == u.id) \
		.filter(UserMute.target_id == User.id)

	total = users.count()

	users = users.order_by(UserMute.created_utc.desc()) \
		.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE ).all()

	return render_template("userpage/muting.html", v=v, u=u, users=users, page=page, total=total)

@app.get("/@<username>/followers")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def followers(v, username):
	u = get_user(username, v=v)

	page = get_page()

	users = g.db.query(Follow, User).join(Follow, Follow.target_id == u.id) \
		.filter(Follow.user_id == User.id)

	total = users.count()

	users = users.order_by(Follow.created_utc.desc()) \
		.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()

	return render_template("userpage/followers.html", v=v, u=u, users=users, page=page, total=total)

@app.get("/@<username>/following")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def following(v, username):
	u = get_user(username, v=v)

	page = get_page()

	users = g.db.query(Follow, User).join(Follow, Follow.user_id == u.id) \
		.filter(Follow.target_id == User.id)

	total = users.count()

	users = users.order_by(Follow.created_utc.desc()) \
		.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()

	return render_template("userpage/following.html", v=v, u=u, users=users, page=page, total=total)

@app.get("/@<username>/views")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def visitors(v, username):
	u = get_user(username, v=v)

	page = get_page()

	views = g.db.query(ViewerRelationship).filter_by(user_id=u.id)
	total = views.count()
	views = views.order_by(ViewerRelationship.last_view_utc.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()

	return render_template("userpage/views.html", v=v, u=u, views=views, total=total, page=page)

@cache.memoize()
def userpagelisting(user, v=None, page=1, sort="new", t="all"):
	posts = g.db.query(Post).filter_by(author_id=user.id, is_pinned=False).options(load_only(Post.id))
	if not (v and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or v.id == user.id)):
		posts = posts.filter_by(is_banned=False, private=False, ghost=False, deleted_utc=0)
	posts = apply_time_filter(t, posts, Post)
	total = posts.count()
	posts = sort_objects(sort, posts, Post)
	posts = posts.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()
	return [x.id for x in posts], total

@app.get("/@<username>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_required
def u_username_wall(v, username):
	u = get_user(username, v=v, include_blocks=True)
	if username != u.username:
		return redirect(f"/@{u.username}")

	if v and hasattr(u, 'is_blocking') and u.is_blocking:
		if g.is_api_or_xhr:
			abort(403, f"You are blocking @{u.username}.")
		return render_template("userpage/blocked.html", u=u, v=v), 403

	is_following = v and u.has_follower(v)

	if v and v.id != u.id and v.admin_level < PERMS['USER_SHADOWBAN'] and not session.get("GLOBAL"):
		gevent.spawn(_add_profile_view, v.id, u.id)

	page = get_page()

	if v:
		comments, output = get_comments_v_properties(v, None, Comment.wall_user_id == u.id)
	else:
		comments = g.db.query(Comment).filter(Comment.wall_user_id == u.id)
	comments = comments.filter(Comment.level == 1)

	if not v or (v.id != u.id and v.admin_level < PERMS['POST_COMMENT_MODERATION']):
		comments = comments.filter(
			Comment.is_banned == False,
			Comment.ghost == False,
			Comment.deleted_utc == 0
		)

	total = comments.count()
	comments = comments.order_by(Comment.created_utc.desc()) \
		.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()
	if v:
		comments = [c[0] for c in comments]

	if v and v.client:
		return {"data": [c.json for c in comments]}

	return render_template("userpage/wall.html", u=u, v=v, listing=comments, page=page, total=total, is_following=is_following, standalone=True, render_replies=True, wall=True)


@app.get("/@<username>/wall/comment/<int:cid>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_required
def u_username_wall_comment(v, username, cid):
	comment = get_comment(cid, v=v)
	if not comment.wall_user_id: abort(400)
	if not User.can_see(v, comment): abort(403)

	u = comment.wall_user

	if v and hasattr(u, 'is_blocking') and u.is_blocking:
		if g.is_api_or_xhr:
			abort(403, f"You are blocking @{u.username}.")
		return render_template("userpage/blocked.html", u=u, v=v), 403

	is_following = v and u.has_follower(v)

	if v and v.id != u.id and v.admin_level < PERMS['USER_SHADOWBAN'] and not session.get("GLOBAL"):
		gevent.spawn(_add_profile_view, v.id, u.id)

	if v and request.values.get("read"):
		gevent.spawn(_mark_comment_as_read, comment.id, v.id)

	try: context = min(int(request.values.get("context", 8)), 8)
	except: context = 8
	comment_info = comment
	c = comment
	while context and c.level > 1:
		c = c.parent_comment
		context -= 1
	top_comment = c

	if v:
		# this is required because otherwise the vote and block
		# props won't save properly unless you put them in a list
		output = get_comments_v_properties(v, None, Comment.top_comment_id == c.top_comment_id)[1]

	if v and v.client: return top_comment.json

	return render_template("userpage/wall.html", u=u, v=v, listing=[top_comment], page=1, is_following=is_following, standalone=True, render_replies=True, wall=True, comment_info=comment_info, total=1)


@app.get("/@<username>/posts")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_required
def u_username(v, username):
	u = get_user(username, v=v, include_blocks=True)
	if username != u.username:
		return redirect(SITE_FULL + request.full_path.replace(username, u.username))

	if v and hasattr(u, 'is_blocking') and u.is_blocking:
		if g.is_api_or_xhr:
			abort(403, f"You are blocking @{u.username}.")
		return render_template("userpage/blocked.html", u=u, v=v), 403

	is_following = v and u.has_follower(v)

	if not u.is_visible_to(v):
		if g.is_api_or_xhr:
			abort(403, f"@{u.username}'s userpage is private")
		return render_template("userpage/private.html", u=u, v=v, is_following=is_following), 403

	if v and v.id != u.id and v.admin_level < PERMS['USER_SHADOWBAN'] and not session.get("GLOBAL"):
		gevent.spawn(_add_profile_view, v.id, u.id)

	sort = request.values.get("sort", "new")
	t = request.values.get("t", "all")
	page = get_page()

	ids, total = userpagelisting(u, v=v, page=page, sort=sort, t=t)

	if page == 1 and sort == 'new':
		sticky = []
		sticky = g.db.query(Post).filter_by(is_pinned=True, author_id=u.id, is_banned=False).all()
		if sticky:
			for p in sticky:
				ids = [p.id] + ids

	listing = get_posts(ids, v=v)

	if u.unban_utc:
		if v and v.client:
			return {"data": [x.json for x in listing]}

		return render_template("userpage/posts.html",
												unban=u.unban_string,
												u=u,
												v=v,
												listing=listing,
												page=page,
												sort=sort,
												t=t,
												total=total,
												is_following=is_following)

	if v and v.client:
		return {"data": [x.json for x in listing]}

	return render_template("userpage/posts.html",
									u=u,
									v=v,
									listing=listing,
									page=page,
									sort=sort,
									t=t,
									total=total,
									is_following=is_following)


@app.get("/@<username>/comments")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_required
def u_username_comments(username, v):
	u = get_user(username, v=v, include_blocks=True)
	if username != u.username:
		return redirect(f"/@{u.username}/comments")

	if v and hasattr(u, 'is_blocking') and u.is_blocking:
		if g.is_api_or_xhr:
			abort(403, f"You are blocking @{u.username}.")
		return render_template("userpage/blocked.html", u=u, v=v), 403

	is_following = v and u.has_follower(v)

	if not u.is_visible_to(v):
		if g.is_api_or_xhr:
			abort(403, f"@{u.username}'s userpage is private")
		return render_template("userpage/private.html", u=u, v=v, is_following=is_following), 403

	if v and v.id != u.id and v.admin_level < PERMS['USER_SHADOWBAN'] and not session.get("GLOBAL"):
		gevent.spawn(_add_profile_view, v.id, u.id)

	page = get_page()

	sort = request.values.get("sort","new")
	t = request.values.get("t","all")

	comment_post_author = aliased(User)
	comments = g.db.query(Comment).options(load_only(Comment.id)) \
				.outerjoin(Comment.post) \
				.outerjoin(comment_post_author, Post.author) \
				.filter(
					Comment.author_id == u.id,
					or_(Comment.parent_post != None, Comment.wall_user_id != None),
				)

	if not v or (v.id != u.id and v.admin_level < PERMS['POST_COMMENT_MODERATION']):
		comments = comments.filter(
			Comment.is_banned == False,
			Comment.ghost == False,
			Comment.deleted_utc == 0
		)

	comments = apply_time_filter(t, comments, Comment)

	total = comments.count()

	comments = sort_objects(sort, comments, Comment)

	comments = comments.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()
	ids = [x.id for x in comments]

	listing = get_comments(ids, v=v)

	if v and v.client:
		return {"data": [c.json for c in listing]}

	return render_template("userpage/comments.html", u=u, v=v, listing=listing, page=page, sort=sort, t=t,total=total, is_following=is_following, standalone=True)


@app.get("/@<username>/info")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def u_username_info(username, v):

	user = get_user(username, v=v, include_blocks=True)

	if hasattr(user, 'is_blocking') and user.is_blocking:
		abort(401, f"You're blocking @{user.username}")
	elif hasattr(user, 'is_blocked') and user.is_blocked:
		abort(403, f"@{user.username} is blocking you!")

	return user.json

@app.get("/<int:id>/info")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def u_user_id_info(id, v):

	user = get_account(id, v=v, include_blocks=True)

	if hasattr(user, 'is_blocking') and user.is_blocking:
		abort(403, f"You're blocking @{user.username}")
	elif hasattr(user, 'is_blocked') and user.is_blocked:
		abort(403, f"@{user.username} is blocking you!")

	return user.json

@app.post("/follow/<username>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def follow_user(username, v):

	target = get_user(username, v=v)

	if target.id==v.id:
		abort(400, "You can't follow yourself!")

	if g.db.query(Follow).filter_by(user_id=v.id, target_id=target.id).one_or_none():
		return {"message": f"@{target.username} has been followed!"}

	new_follow = Follow(user_id=v.id, target_id=target.id)
	g.db.add(new_follow)

	target.stored_subscriber_count += 1
	g.db.add(target)

	if not v.shadowbanned:
		send_notification(target.id, f"@{v.username} has followed you!")


	return {"message": f"@{target.username} has been followed!"}

@app.post("/unfollow/<username>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def unfollow_user(username, v):

	target = get_user(username)

	follow = g.db.query(Follow).filter_by(user_id=v.id, target_id=target.id).one_or_none()

	if follow:
		g.db.delete(follow)

		target.stored_subscriber_count -= 1
		g.db.add(target)

		if not v.shadowbanned:
			send_notification(target.id, f"@{v.username} has unfollowed you!")

	else:
		abort(400, f"You're not even following @{target.username} to begin with!")


	return {"message": f"@{target.username} has been unfollowed!"}

@app.post("/remove_follow/<username>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def remove_follow(username, v):
	target = get_user(username)

	follow = g.db.query(Follow).filter_by(user_id=target.id, target_id=v.id).one_or_none()

	if not follow: return {"message": f"@{target.username} has been removed as a follower!"}

	g.db.delete(follow)

	v.stored_subscriber_count -= 1
	g.db.add(v)

	send_repeatable_notification(target.id, f"@{v.username} has removed your follow!")


	return {"message": f"@{target.username} has been removed as a follower!"}


@app.get("/pp/<int:id>")
@app.get("/uid/<int:id>/pic")
@app.get("/uid/<int:id>/pic/profile")
@limiter.exempt
def user_profile_uid(id):
	return redirect(get_profile_picture(id))

@app.get("/@<username>/pic")
@limiter.exempt
def user_profile_name(username):
	return redirect(get_profile_picture(username))


def get_saves_and_subscribes(v, template, relationship_cls, page, standalone=False):
	if relationship_cls in {SaveRelationship, Subscription}:
		query = relationship_cls.post_id
		join = relationship_cls.post
		cls = Post
	elif relationship_cls is CommentSaveRelationship:
		query = relationship_cls.comment_id
		join = relationship_cls.comment
		cls = Comment
	else:
		raise TypeError("Relationships supported is SaveRelationship, Subscription, CommentSaveRelationship")

	listing = g.db.query(query).join(join).filter(relationship_cls.user_id == v.id)

	total = listing.count()

	listing = listing.order_by(cls.created_utc.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()

	ids = [x[0] for x in listing]

	extra = None
	if v.admin_level < PERMS['POST_COMMENT_MODERATION']:
		extra = lambda q:q.filter(cls.is_banned == False, cls.deleted_utc == 0)

	if cls is Post:
		listing = get_posts(ids, v=v, extra=extra)
	elif cls is Comment:
		listing = get_comments(ids, v=v, extra=extra)
	else:
		raise TypeError("Only supports Posts and Comments. This is probably the result of a bug with *this* function")

	if v.client: return {"data": [x.json for x in listing]}
	return render_template(template, u=v, v=v, listing=listing, page=page, total=total, standalone=standalone)

@app.get("/@<username>/saved/posts")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def saved_posts(v, username):
	page = get_page()

	return get_saves_and_subscribes(v, "userpage/posts.html", SaveRelationship, page, False)

@app.get("/@<username>/saved/comments")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def saved_comments(v, username):
	page = get_page()

	return get_saves_and_subscribes(v, "userpage/comments.html", CommentSaveRelationship, page, True)

@app.get("/@<username>/subscribed/posts")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def subscribed_posts(v, username):
	page = get_page()

	return get_saves_and_subscribes(v, "userpage/posts.html", Subscription, page, False)

@app.post("/fp/<fp>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def fp(v, fp):
	if session.get("GLOBAL"):
		return '', 204

	v.fp = fp
	users = g.db.query(User).filter(User.fp == fp, User.id != v.id).all()
	if v.email and v.email_verified:
		alts = g.db.query(User).filter(User.email == v.email, User.email_verified, User.id != v.id).all()
		if alts:
			users += alts
	for u in users:
		li = [v.id, u.id]
		g.db.flush()
		existing = g.db.query(Alt).filter(Alt.user1.in_(li), Alt.user2.in_(li)).one_or_none()
		if existing: continue
		add_alt(user1=v.id, user2=u.id)

	check_for_alts(v, include_current_session=True)
	g.db.add(v)
	return '', 204

@app.post("/toggle_pins/<sub>/<sort>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
def toggle_pins(sub, sort):
	if sort == 'hot': default = True
	else: default = False

	pins = session.get(f'{sub}_{sort}', default)
	session[f'{sub}_{sort}'] = not pins

	return {"message": "Pins toggled successfully!"}


@app.get("/badge_owners/<int:bid>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def bid_list(v, bid):

	page = get_page()

	users = g.db.query(User, Badge.created_utc).join(User.badges).filter(Badge.badge_id==bid)

	total = users.count()

	users = users.order_by(Badge.created_utc.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()

	return render_template("owners.html", v=v, users=users, page=page, total=total, kind="Badge")


KOFI_TOKEN = environ.get("KOFI_TOKEN", "").strip()
if KOFI_TOKEN:
	@app.post("/kofi")
	@limiter.exempt
	def kofi():
		data = json.loads(request.values['data'])
		verification_token = data['verification_token']
		if verification_token != KOFI_TOKEN: abort(400)

		print(request.headers.get('CF-Connecting-IP'), flush=True)
		id = data['kofi_transaction_id']
		created_utc = int(time.mktime(time.strptime(data['timestamp'].split('.')[0], "%Y-%m-%dT%H:%M:%SZ")))
		type = data['type']
		amount = 0
		try:
			amount = int(float(data['amount']))
		except:
			abort(400, 'invalid amount')
		email = data['email']

		transaction = Transaction(
			id=id,
			created_utc=created_utc,
			type=type,
			amount=amount,
			email=email
		)

		g.db.add(transaction)

		claim_rewards_all_users()

		return ''

@app.post("/gumroad")
@limiter.exempt
def gumroad():
	data = request.values
	ip = request.headers.get('CF-Connecting-IP')
	if ip != '34.193.146.117':
		print(STARS, flush=True)
		print(f'/gumroad fail: {ip}')
		print(STARS, flush=True)
		abort(400)

	id = data['sale_id']

	existing = g.db.get(Transaction, id)
	if existing: return ''

	created_utc = int(time.mktime(time.strptime(data['sale_timestamp'].split('.')[0], "%Y-%m-%dT%H:%M:%SZ")))

	if data.get('recurrence'):
		type = "monthly"
	else:
		type = "one-time"

	amount = int(data['price']) / 100
	email = data['email']

	transaction = Transaction(
		id=id,
		created_utc=created_utc,
		type=type,
		amount=amount,
		email=email
	)

	g.db.add(transaction)

	claim_rewards_all_users()

	return ''




@app.post("/settings/claim_rewards")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_claim_rewards(v):
	if not (v.email and v.email_verified):
		abort(400, f"You must have a verified email to verify {patron} status and claim your rewards!")

	transactions = g.db.query(Transaction).filter_by(email=v.email, claimed=None).all()

	if not transactions:
		abort(400, f"{patron} rewards already claimed!")

	claim_rewards_all_users()

	return {"message": f"{patron} rewards claimed!"}

@app.get("/users")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def users_list(v):

	page = get_page()

	users = g.db.query(User)

	total = users.count()

	users = users.order_by(User.id.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()

	return render_template("user_cards.html",
						v=v,
						users=users,
						total=total,
						page=page,
						user_cards_title="Users Feed",
						)

@app.post("/mute_notifs/<int:uid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("20/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("20/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def mute_notifs(v, uid):
	user = get_account(uid)

	if user.id == v.id:
		abort(400, "You can't mute notifications from yourself!")
	if user.id == AUTOJANNY_ID:
		abort(403, f"You can't mute notifications from @{user.username}")
	if v.has_muted(user):
		abort(409, f"You have already muted notifications from @{user.username}")

	new_mute = UserMute(user_id=v.id, target_id=user.id)
	g.db.add(new_mute)

	send_notification(user.id, f"@{v.username} has muted notifications from you!")

	return {"message": f"You have muted notifications from @{user.username} successfully!"}


@app.post("/unmute_notifs/<int:uid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def unmute_notifs(v, uid):
	user = get_account(uid)

	x = v.has_muted(user)

	if not x:
		abort(409, "You can't unmute notifications from someone you haven't muted notifications from!")

	g.db.delete(x)

	send_notification(user.id, f"@{v.username} has unmuted notifications from you!")

	return {"message": f"You have unmuted notifications from @{user.username} successfully!"}
