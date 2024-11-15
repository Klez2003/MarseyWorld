import io
import json
import math
import time
from collections import Counter

import gevent
import qrcode
from sqlalchemy.orm import aliased, load_only
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from sqlalchemy import nullslast

from files.classes import *
from files.classes.transactions import *
from files.classes.views import *
from files.helpers.actions import execute_under_siege
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.mail import *
from files.helpers.sanitize import *
from files.helpers.sorting_and_time import *
from files.helpers.useractions import badge_grant
from files.helpers.can_see import *
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
	g.db.flush()

	emails = [x[0] for x in g.db.query(Transaction.email).filter_by(claimed=None)]
	user_ids = [x[0] for x in g.db.query(Transaction.user_id).filter_by(claimed=None)]

	users = g.db.query(User).filter(
		or_(
			User.email.in_(emails),
			User.id.in_(user_ids),
		),
	).order_by(User.truescore.desc()).all()

	for user in users:
		g.db.flush()
		transactions = g.db.query(Transaction).filter(
			or_(
				Transaction.email == user.email,
				Transaction.user_id == user.id,
			),
			Transaction.claimed == None,
		).all()

		highest_tier = 0
		marseybux = 0

		has_yearly = False

		for transaction in transactions:
			tx_amount_for_tier = transaction.amount

			if transaction.type == 'yearly':
				tx_amount_for_tier /= 10
				has_yearly = True

			for t, money in TIER_TO_MONEY.items():
				if tx_amount_for_tier < money: break
				tier = t

			marseybux += transaction.amount * TIER_TO_MUL[tier]

			if tier > highest_tier:
				highest_tier = tier
			transaction.claimed = True
			g.db.add(transaction)

		if marseybux:
			marseybux = int(marseybux)
			text = f"You have received {marseybux} Marseybux! You can use them to buy awards or hats in the [shop](/shop/awards) or gamble them in the [casino](/casino)."

			user.pay_account('marseybux', marseybux, f"{patron} reward")

			send_repeatable_notification(user.id, text)
			g.db.add(user)

			if highest_tier > user.patron or (highest_tier < user.patron and user.patron_utc - time.time() < 432000):
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

			if has_yearly:
				val = 31560000
			else:
				val = 2937600

			if user.patron_utc:
				user.patron_utc += val
			else:
				user.patron_utc = time.time() + val

			g.db.flush()
			user.lifetimedonated = g.db.query(func.sum(Transaction.amount)).filter(
				or_(
					Transaction.email == user.email,
					Transaction.user_id == user.id,
				)
			).scalar()

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


	top_10_patrons = g.db.query(User).options(load_only(User.id)).order_by(User.lifetimedonated.desc()).limit(10)

	if set(users) & set(top_10_patrons):
		for badge in g.db.query(Badge).filter(
			Badge.badge_id == 294,
			Badge.user_id.notin_({x.id for x in top_10_patrons}),
		).all():
			g.db.delete(badge)
		for user in top_10_patrons:
			badge_grant(badge_id=294, user=user, repeat_notify=False)

def transfer_currency(v, username, currency_name, apply_tax):
	MIN_CURRENCY_TRANSFER = 100
	TAX_PCT = 0.03
	receiver = get_user(username, v=v)
	if receiver.id == v.id: stop(400, f"You can't transfer {currency_name} to yourself!")
	amount = request.values.get("amount", "").strip()
	amount = int(amount) if amount.isdigit() else None

	if amount is None or amount <= 0: stop(400, f"Invalid number of {currency_name}")
	if amount < MIN_CURRENCY_TRANSFER: stop(400, f"You have to gift at least {MIN_CURRENCY_TRANSFER} {currency_name}")
	tax = 0
	if apply_tax and not v.patron and not receiver.patron:
		tax = math.ceil(amount*TAX_PCT)

	if v.shadowbanned:
		return {"message": f"{amount - tax} {currency_name} have been transferred to @{receiver.username}"}

	reason = request.values.get("reason", "").strip()
	log_message = f"@{v.username} has transferred {amount} {currency_name} to @{receiver.username}"
	notif_text = f":marseycapitalistmanlet: @{v.username} has gifted you {amount-tax} {currency_name}!"

	if reason:
		if len(reason) > TRANSFER_MESSAGE_LENGTH_LIMIT:
			stop(400, f"Reason is too long (max {TRANSFER_MESSAGE_LENGTH_LIMIT} characters)")
		notif_text += '\n\n> ' + '\n\n> '.join(reason.splitlines())
		log_message += '\n\n> ' + '\n\n> '.join(reason.splitlines())

	charge_reason = f'Gift to <a href="/id/{receiver.id}">@{username}</a>'
	if not v.charge_account(currency_name, amount, charge_reason):
		stop(400, f"You don't have enough {currency_name}")

	if currency_name in {'marseybux', 'coins'}:
		pay_reason = f'Gift from <a href="/id/{v.id}">@{v.username}</a>'
		receiver.pay_account(currency_name, amount - tax, pay_reason)
	else:
		raise ValueError(f"Invalid currency '{currency_name}' got when transferring {amount} from {v.id} to {receiver.id}")

	if CURRENCY_TRANSFER_ID:
		send_repeatable_notification(CURRENCY_TRANSFER_ID, log_message)

	send_repeatable_notification(receiver.id, notif_text)

	return {"message": f"{commas(amount - tax)} {currency_name} have been transferred to @{receiver.username}"}

def upvoters_downvoters(v, username, username2, cls, vote_cls, vote_dir, template, standalone):
	u = get_user(username, v=v)
	if not u.is_visible_to(v, 0, "posts"): stop(403)
	id = u.id

	uid = get_user(username2, attributes=[User.id]).id

	page = get_page()

	listing = g.db.query(cls).options(load_only(cls.id)).join(vote_cls).filter(
			cls.ghost == False,
			cls.is_banned == False,
			cls.deleted_utc == 0,
			vote_cls.vote_type == vote_dir,
			cls.author_id == id,
			vote_cls.user_id == uid,
		)
	
	if cls == Post:
		listing = listing.filter(cls.draft == False)

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
	kind = "posts" if cls == Post else "comments"
	if not u.is_visible_to(v, 0, kind): stop(403)
	id = u.id

	uid = get_user(username2, attributes=[User.id]).id

	page = get_page()

	listing = g.db.query(cls).options(load_only(cls.id)).join(vote_cls).filter(
			cls.ghost == False,
			cls.is_banned == False,
			cls.deleted_utc == 0,
			vote_cls.vote_type == vote_dir,
			vote_cls.user_id == id,
			cls.author_id == uid,
		)

	if cls == Post:
		listing = listing.filter(cls.draft == False)

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
	sort = request.values.get("sort")

	page = get_page()

	users = g.db.query(User).filter(
		User.is_banned != None,
		or_(User.unban_utc == None, User.unban_utc > time.time()),
	)

	total = users.count()

	if sort == "name":
		key = func.lower(User.username)
	elif sort == "truescore":
		key = User.truescore.desc()
	elif sort == "ban_reason":
		key = func.lower(User.ban_reason)
	elif sort == "banned_by":
		key = User.is_banned
	else:
		sort = "unban_utc"
		key = nullslast(User.unban_utc)

	users = users.order_by(key).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE)

	return render_template("banned.html", v=v, users=users, sort=sort, total=total, page=page)

@app.get("/grassed")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def grassed(v):
	users = g.db.query(User).filter(
		User.ban_reason.like('Grass award used by @%'),
		User.unban_utc > time.time(),
	).order_by(User.unban_utc).all()

	return render_template("grassed.html", v=v, users=users)

@app.get("/chuds")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def chuds(v):
	users = g.db.query(User).filter(
		or_(User.chud == 1, User.chud > time.time()),
	).order_by(User.truescore.desc())

	return render_template("chuds.html", v=v, users=users)

@app.get("/deletion_requests")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def deletion_requests(v):
	users = g.db.query(User, AccountDeletion).join(User.deletion).order_by(AccountDeletion.created_utc)
	return render_template("deletion_requests.html", v=v, users=users)

def all_upvoters_downvoters(v, username, vote_dir, is_who_simps_hates):
	if username == 'Snappy':
		stop(403, "For performance reasons, you can't see Snappy's statistics!")
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
		votes = g.db.query(Post.author_id, func.count(Post.author_id)).join(Vote).filter(Post.draft == False, Post.ghost == False, Post.is_banned == False, Post.deleted_utc == 0, Vote.vote_type==vote_dir, Vote.user_id==id).group_by(Post.author_id).order_by(func.count(Post.author_id).desc()).all()
		votes2 = g.db.query(Comment.author_id, func.count(Comment.author_id)).join(CommentVote).filter(Comment.ghost == False, Comment.is_banned == False, Comment.deleted_utc == 0, CommentVote.vote_type==vote_dir, CommentVote.user_id==id).group_by(Comment.author_id).order_by(func.count(Comment.author_id).desc()).all()
	else:
		votes = g.db.query(Vote.user_id, func.count(Vote.user_id)).join(Post).filter(Post.draft == False, Post.ghost == False, Post.is_banned == False, Post.deleted_utc == 0, Vote.vote_type==vote_dir, Post.author_id==id).group_by(Vote.user_id).order_by(func.count(Vote.user_id).desc()).all()
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
	total_items = f'{commas(total_items)} {vote_str} {received_given}'

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
	send_notification(user.id, GET_HELP_MESSAGE.format(vid=v.id))
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
@auth_required
def transfer_coins(v, username):
	return transfer_currency(v, username, 'coins', True)

@app.post("/@<username>/transfer_marseybux")
@feature_required('MARSEYBUX')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def transfer_marseybux(v, username):
	return transfer_currency(v, username, 'marseybux', False)

@app.get("/@<username>/css")
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
def get_css(username):
	user = get_user(username, attributes=[User.css, User.background])

	css = user.css
	bg = user.background

	if bg:
		if not css: css = ''
		css += f'body {{background: url("{bg}") center center fixed;}}'
		if 'anime/' not in bg and not bg.startswith('/images/'):
			css += 'body {background-size: cover}'

	if not css: stop(404)

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
		css += f'\n\nbody {{background: url("{bg}") center center fixed;background-size: auto;}}'
	if not css: stop(404)

	resp = make_response(css)
	resp.headers["Content-Type"] = "text/css"
	return resp

@app.post("/subscribe/<int:post_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def subscribe(v, post_id):
	p = get_post(post_id)
	if v.id == p.author_id:
		stop(403, "You can't subscribe to your own posts!")

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
@auth_required
def message(v, username=None, id=None):
	if id:
		user = get_account(id, v=v, include_blocks=True)
	else:
		user = get_user(username, v=v, include_blocks=True)

	if user.id == MODMAIL_ID:
		stop(403, "Please use /contact to contact the admins")

	if hasattr(user, 'is_blocking') and user.is_blocking:
		stop(403, f"You're blocking @{user.username}")

	if v.admin_level < PERMS['MESSAGE_BLOCKED_USERS'] and hasattr(user, 'is_blocked') and user.is_blocked:
		stop(403, f"@{user.username} is blocking you!")

	if v.admin_level < PERMS['MESSAGE_BLOCKED_USERS'] and user.has_muted(v):
		stop(403, f"@{user.username} is muting notifications from you, so messaging them is pointless!")

	body = request.values.get("message", "").strip()
	if len(body) > COMMENT_BODY_LENGTH_LIMIT:
		stop(400, f'Message is too long (max {COMMENT_BODY_LENGTH_LIMIT} characters)')

	if not g.is_tor and get_setting("dm_media"):
		body = process_files(request.files, v, body, is_dm=True, dm_user=user)
		if len(body) > COMMENT_BODY_LENGTH_LIMIT:
			stop(400, f'Message is too long (max {COMMENT_BODY_LENGTH_LIMIT} characters)')

	if not body: stop(400, "Message is empty!")

	body_html = sanitize(body)

	if len(body_html) > COMMENT_BODY_HTML_LENGTH_LIMIT:
		stop(400, "Rendered message is too long!")

	existing = g.db.query(Comment.id).filter(
		Comment.author_id == v.id,
		Comment.sentto == user.id,
		Comment.body_html == body_html
	).first()

	if existing: stop(403, "Message already exists!")

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
	execute_under_siege(v, c, 'message')
	c.top_comment_id = c.id

	if user.id not in BOT_IDs and can_see(user, v):
		g.db.flush()
		notif = g.db.query(Notification).filter_by(comment_id=c.id, user_id=user.id).one_or_none()
		if not notif:
			notif = Notification(comment_id=c.id, user_id=user.id)
			g.db.add(notif)


	title = f'New message from @{c.author_name}'

	url = f'{SITE_FULL}/notifications/messages'

	push_notif({user.id}, title, body, url)

	return {"message": "Message sent!"}


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

	if name.title() in GIRL_NAMES_TOTAL:
		return {name: False}

	if len(name) < 3 or len(name) > 25:
		return {name: False}

	existing = get_user(name, graceful=True)

	if existing:
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

@app.get("/@<username>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_required
def u_username_wall(v, username):
	u = get_user(username, v=v, include_blocks=True)
	if username != u.username:
		return redirect(f"/@{u.username}" + request.full_path.split(request.path)[1])

	if v and v.id != u.id and v.admin_level < PERMS['USER_SHADOWBAN'] and not session.get("GLOBAL"):
		gevent.spawn(_add_profile_view, v.id, u.id)

	if v and v.has_blocked(u):
		if g.is_api_or_xhr:
			stop(403, f"You are blocking @{u.username}.")
		return render_template("userpage/blocked.html", u=u, v=v), 403

	is_following = v and u.has_follower(v)

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

	if v.admin_level < PERMS['USER_SHADOWBAN']:
		comments = comments.join(Comment.author).filter(or_(User.id == v.id, User.shadowbanned == None))

	total = comments.count()

	pinned = []

	if v.admin_level >= PERMS['ADMIN_NOTES']:
		pinned += [c[0] for c in comments.filter(Comment.pinned == 'Admin Note').order_by(Comment.created_utc.desc())]
	
	pinned += [c[0] for c in comments.filter(Comment.pinned != 'Admin Note').order_by(Comment.created_utc.desc())]
	for c in pinned:
		c.admin_note = True

	comments = comments.filter(Comment.pinned == None).order_by(Comment.created_utc.desc()) .offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()
	comments = [c[0] for c in comments]
	comments = pinned + comments

	if v.client:
		return {"data": [c.json for c in comments]}

	return render_template("userpage/wall.html", u=u, v=v, listing=comments, page=page, total=total, is_following=is_following, standalone=True, render_replies=True, wall=True)


@app.get("/@<username>/wall/comment/<int:cid>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_required
def u_username_wall_comment(v, username, cid):
	comment = get_comment(cid, v=v)
	if not comment.wall_user_id: stop(400)
	if not can_see(v, comment): stop(403)

	u = comment.wall_user

	if v and v.id != u.id and v.admin_level < PERMS['USER_SHADOWBAN'] and not session.get("GLOBAL"):
		gevent.spawn(_add_profile_view, v.id, u.id)

	if v and v.has_blocked(u):
		if g.is_api_or_xhr:
			stop(403, f"You are blocking @{u.username}.")
		return render_template("userpage/blocked.html", u=u, v=v), 403

	is_following = v and u.has_follower(v)

	if v and request.values.get("read"):
		gevent.spawn(_mark_comment_as_read, comment.id, v.id)

	try: context = min(int(request.values.get("context", 8)), 8)
	except: context = 8
	focused_comment = comment
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

	return render_template("userpage/wall.html", u=u, v=v, listing=[top_comment], page=1, is_following=is_following, standalone=True, render_replies=True, wall=True, focused_comment=focused_comment, total=1)

@app.get("/@<username>/posts")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_required
def u_username(v, username):
	u = get_user(username, v=v, include_blocks=True)
	if username != u.username:
		return redirect(f"/@{u.username}/posts" + request.full_path.split(request.path)[1])

	if v and v.id != u.id and v.admin_level < PERMS['USER_SHADOWBAN'] and not session.get("GLOBAL"):
		gevent.spawn(_add_profile_view, v.id, u.id)

	if v and v.has_blocked(u):
		if g.is_api_or_xhr:
			stop(403, f"You are blocking @{u.username}.")
		return render_template("userpage/blocked.html", u=u, v=v), 403

	is_following = v and u.has_follower(v)

	page = get_page()

	if not u.is_visible_to(v, page, "posts"):
		if g.is_api_or_xhr:
			stop(403, f"@{u.username}'s post history is private")
		return render_template("userpage/private_posts.html", u=u, v=v, is_following=is_following, private=True), 403

	sort = request.values.get("sort", "new")
	t = request.values.get("t", "all")

	ids, total = userpagelisting(u, v=v, page=page, sort=sort, t=t)

	if page == 1 and sort == 'new':
		pinned = []
		pinned = g.db.query(Post).filter_by(profile_pinned=True, author_id=u.id)

		if v.id != u.id and v.admin_level < PERMS['POST_COMMENT_MODERATION']:
			pinned = pinned.filter_by(is_banned=False)

		pinned = pinned.order_by(Post.created_utc.desc()).all()

		for p in pinned:
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

@cache.memoize(timeout=86400)
def userpagelisting(u, v=None, page=1, sort="new", t="all"):
	posts = g.db.query(Post).filter_by(author_id=u.id, profile_pinned=False).options(load_only(Post.id))

	if v.id != u.id and v.admin_level < PERMS['POST_COMMENT_MODERATION']:
		posts = posts.filter_by(is_banned=False, draft=False, ghost=False)

	if v.admin_level < PERMS['POST_COMMENT_MODERATION'] and not (SITE_NAME == 'rDrama' and v.id == u.id):
		posts = posts.filter_by(deleted_utc=0)

	posts = apply_time_filter(t, posts, Post)
	total = posts.count()
	posts = sort_objects(sort, posts, Post)
	posts = posts.offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()
	return [x.id for x in posts], total

@app.get("/@<username>/comments")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_required
def u_username_comments(username, v):
	u = get_user(username, v=v, include_blocks=True)
	if username != u.username:
		return redirect(f"/@{u.username}/comments" + request.full_path.split(request.path)[1])

	if v and v.id != u.id and v.admin_level < PERMS['USER_SHADOWBAN'] and not session.get("GLOBAL"):
		gevent.spawn(_add_profile_view, v.id, u.id)

	if v and v.has_blocked(u):
		if g.is_api_or_xhr:
			stop(403, f"You are blocking @{u.username}.")
		return render_template("userpage/blocked.html", u=u, v=v), 403

	is_following = v and u.has_follower(v)

	page = get_page()

	if not u.is_visible_to(v, page, "comments"):
		if g.is_api_or_xhr:
			stop(403, f"@{u.username}'s comment history is private")
		return render_template("userpage/private_comments.html", u=u, v=v, is_following=is_following, private=True), 403

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

	if v.id != u.id and v.admin_level < PERMS['POST_COMMENT_MODERATION']:
		comments = comments.filter(
			Comment.is_banned == False,
			Comment.ghost == False,
			or_(Post.draft == False, Comment.wall_user_id != None),
		)

	if v.admin_level < PERMS['POST_COMMENT_MODERATION'] and not (SITE_NAME == 'rDrama' and v.id == u.id):
		comments = comments.filter(
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
		stop(401, f"You're blocking @{user.username}")
	elif hasattr(user, 'is_blocked') and user.is_blocked:
		stop(403, f"@{user.username} is blocking you!")

	return user.json

@app.get("/<int:id>/info")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def u_user_id_info(id, v):

	user = get_account(id, v=v, include_blocks=True)

	if hasattr(user, 'is_blocking') and user.is_blocking:
		stop(403, f"You're blocking @{user.username}")
	elif hasattr(user, 'is_blocked') and user.is_blocked:
		stop(403, f"@{user.username} is blocking you!")

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
		stop(400, "You can't follow yourself!")

	if g.db.query(Follow).filter_by(user_id=v.id, target_id=target.id).one_or_none():
		return {"message": f"@{target.username} has been followed!"}

	new_follow = Follow(user_id=v.id, target_id=target.id)
	g.db.add(new_follow)

	target.stored_subscriber_count += 1
	g.db.add(target)

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

		send_notification(target.id, f"@{v.username} has unfollowed you!")

	else:
		stop(400, f"You're not even following @{target.username} to begin with!")


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

@app.post("/toggle_pins/<hole>/<sort>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
def toggle_pins(hole, sort):
	if sort == 'hot': default = True
	else: default = False

	pins = session.get(f'{hole}_{sort}', default)
	session[f'{hole}_{sort}'] = not pins

	return {"message": "Pins toggled successfully!"}

@app.post("/toggle_category/<category>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
def toggle_category(category):
	if category not in CATEGORIES_ICONS:
		stop(400, "Invalid category!")

	session[category] = not session.get(category, True)

	return {"message": f"{category} toggled successfully!"}


@app.get("/badge_owners/<int:bid>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def bid_list(v, bid):
	if bid in PATRON_BADGES and v.admin_level < PERMS['VIEW_PATRONS']:
		stop(404)

	name = g.db.query(BadgeDef.name).filter_by(id=bid).one_or_none()

	if not name:
		stop(404, "Badge not found")
	
	name = name[0]

	href = f'{SITE_FULL_IMAGES}/i/{SITE_NAME}/badges/{bid}.webp?b=14'

	page = get_page()

	users = g.db.query(User, Badge.created_utc).join(User.badges).filter(Badge.badge_id==bid)

	total = users.count()

	users = users.order_by(Badge.created_utc.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()

	return render_template("owners.html", v=v, users=users, page=page, total=total, kind="Badge", name=name, href=href)


KOFI_TOKEN = environ.get("KOFI_TOKEN", "").strip().split(',')
if KOFI_TOKEN:
	@app.post("/kofi")
	@limiter.exempt
	def kofi():
		data = json.loads(request.values['data'])
		verification_token = data['verification_token']
		if verification_token not in KOFI_TOKEN:
			print(STARS, flush=True)
			print(f'/exempt fail: {verification_token}')
			print(STARS, flush=True)
			stop(400)

		id = data['kofi_transaction_id']
		created_utc = int(time.mktime(time.strptime(data['timestamp'].split('.')[0], "%Y-%m-%dT%H:%M:%SZ")))
		type = data['type']
		amount = 0
		try:
			amount = int(float(data['amount']))
		except:
			stop(400, 'invalid amount')
		email = data['email'].strip().lower()

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
	if ip not in {'34.193.146.117', '54.156.191.45'}:
		print(STARS, flush=True)
		print(f'/gumroad fail: {ip}')
		print(STARS, flush=True)
		stop(400)

	id = data['sale_id']

	existing = g.db.get(Transaction, id)
	if existing: return ''

	created_utc = int(time.mktime(time.strptime(data['sale_timestamp'].split('.')[0], "%Y-%m-%dT%H:%M:%SZ")))

	if data.get('recurrence'):
		type = data['recurrence']
	else:
		type = "one-time"

	amount = int(data['price']) / 100
	email = data['email'].strip().lower()

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


@app.post("/bm")
@limiter.exempt
def bm():
	data = json.loads(request.data)

	ip = request.headers.get('CF-Connecting-IP')

	if ip not in {'54.187.174.169','54.187.205.235','54.187.216.72'}:
		print(STARS, flush=True)
		print(f'/bm fail: {ip}')
		print(STARS, flush=True)
		stop(400)

	data = data['data']['object']

	if data['calculated_statement_descriptor'] != 'MARSEY':
		return ''

	id = data['id']

	existing = g.db.get(Transaction, id)
	if existing: return ''

	amount = data['amount']/100

	email = data['billing_details']['email']
	if not email: return ''
	email = email.strip().lower()

	created_utc = data['created']

	if data['description'] == 'rdrama.net (@rdrama.net) - Support':
		type = "one-time"
	else:
		type = "monthly"

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


@app.post("/av")
@limiter.exempt
def av():
	data = json.loads(request.data)

	timestamp, signature = request.headers.get('Donorbox-Signature').split(',')

	if time.time() - int(timestamp) > 30:
		print(STARS, flush=True)
		print(f'/av wrong timestamp: {timestamp}')
		print(STARS, flush=True)
		stop(400)

	string = timestamp + '.' + str(request.data.decode('utf-8'))
	correct_signature = hmac.new(key=bytes(environ.get("AV_KEY").strip(), "utf-8"),
								msg=bytes(string, "utf-8"),
								digestmod=hashlib.sha256
							).hexdigest()
	if correct_signature != signature:
		print(STARS, flush=True)
		print(f'/av wrong signature: {signature}')
		print(STARS, flush=True)
		stop(400)


	data = data[0]

	id = str(data['id'])

	existing = g.db.get(Transaction, id)
	if existing: return ''

	amount = float(data['amount'])

	email = data['donor']['email']
	if not email: return ''
	email = email.strip().lower()

	created_utc = int(time.mktime(time.strptime(data['donation_date'].split('.')[0], "%Y-%m-%dT%H:%M:%S")))

	if data['recurring']:
		type = "monthly"
	else:
		type = "one-time"

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
		stop(400, f"You must have a verified email to verify {patron} status and claim your rewards!")

	transactions = g.db.query(Transaction).filter_by(email=v.email).all()
	if not transactions:
		stop(400, f"No matching email found. Please ensure you're using the same email here that you used on {DONATE_SERVICE}.")

	transactions = g.db.query(Transaction).filter_by(email=v.email, claimed=None).all()
	if not transactions:
		stop(400, f"{patron} rewards already claimed!")

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
		stop(400, "You can't mute notifications from yourself!")
	if user.id == AUTOJANNY_ID:
		stop(403, f"You can't mute notifications from @{user.username}")
	if v.has_muted(user):
		stop(409, f"You have already muted notifications from @{user.username}")

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
		stop(409, "You can't unmute notifications from someone you haven't muted notifications from!")

	g.db.delete(x)

	send_notification(user.id, f"@{v.username} has unmuted notifications from you!")

	return {"message": f"You have unmuted notifications from @{user.username} successfully!"}

@app.get("/@<username>/song")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
def usersong(username):
	user = get_user(username)

	if not user.song:
		stop(404, f"@{user.username} hasn't set a profile anthem!")

	if len(user.song) == 11:
		return redirect(f'https://youtube.com/watch?v={user.song}')

	resp = make_response(redirect(f"/songs/{user.song}.mp3"))
	resp.headers["Cache-Control"] = "no-store"
	return resp

@app.get("/@<username>/effortposts")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def user_effortposts(v, username):
	return redirect(f'/search/posts?q=author:{username}+effortpost:true')

@app.get("/@<username>/bank_statement")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def bank_statement(v, username):
	user = get_user(username, attributes=[User.id, User.username])

	page = get_page()

	logs = g.db.query(CurrencyLog).filter_by(user_id=user.id)

	total = logs.count()

	logs = logs.order_by(CurrencyLog.created_utc.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()

	return render_template("bank_statement.html", v=v, user=user, logs=logs, page=page, total=total)
