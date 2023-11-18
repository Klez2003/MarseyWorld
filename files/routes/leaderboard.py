from files.classes import *
from files.classes.leaderboard import Leaderboard
from files.helpers.config.const import *
from files.routes.wrappers import *

from files.__main__ import app, limiter

@app.get("/leaderboard")
@app.get("/leaderboard/coins")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard_coins(v):
	leaderboard = Leaderboard("Coins", "coins", "coins", "Coins", None, Leaderboard.get_simple_lb, User.coins, v, lambda u:u.coins, g.db.query(User))
	return render_template("leaderboard.html", v=v, leaderboard=leaderboard)

@app.get("/leaderboard/marseybux")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard_marseybux(v):
	leaderboard = Leaderboard("Marseybux", "marseybux", "marseybux", "Marseybux", None, Leaderboard.get_simple_lb, User.marseybux, v, lambda u:u.marseybux, g.db.query(User))
	return render_template("leaderboard.html", v=v, leaderboard=leaderboard)

@app.get("/leaderboard/spent")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard_spent(v):
	leaderboard = Leaderboard("Coins spent on awards", "coins spent on awards", "spent", "Coins", None, Leaderboard.get_simple_lb, User.coins_spent, v, lambda u:u.coins_spent, g.db.query(User))
	return render_template("leaderboard.html", v=v, leaderboard=leaderboard)

@app.get("/leaderboard/truescore")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard_truescore(v):
	leaderboard = Leaderboard("Truescore", "truescore", "truescore", "Truescore", None, Leaderboard.get_simple_lb, User.truescore, v, lambda u:u.truescore, g.db.query(User))
	return render_template("leaderboard.html", v=v, leaderboard=leaderboard)

@app.get("/leaderboard/followers")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard_followers(v):
	leaderboard = Leaderboard("Followers", "followers", "followers", "Followers", "followers", Leaderboard.get_simple_lb, User.stored_subscriber_count, v, lambda u:u.stored_subscriber_count, g.db.query(User))
	return render_template("leaderboard.html", v=v, leaderboard=leaderboard)

@app.get("/leaderboard/posts")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard_posts(v):
	leaderboard = Leaderboard("Posts", "post count", "posts", "Posts", "posts", Leaderboard.get_simple_lb, User.post_count, v, lambda u:u.post_count, g.db.query(User))
	return render_template("leaderboard.html", v=v, leaderboard=leaderboard)

@app.get("/leaderboard/comments")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard_comments(v):
	leaderboard = Leaderboard("Comments", "comment count", "comments", "Comments", "comments", Leaderboard.get_simple_lb, User.comment_count, v, lambda u:u.comment_count, g.db.query(User))
	return render_template("leaderboard.html", v=v, leaderboard=leaderboard)

@app.get("/leaderboard/received_awards")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard_received_awards(v):
	leaderboard = Leaderboard("Received awards", "received awards", "received-awards", "Received Awards", None, Leaderboard.get_simple_lb, User.received_award_count, v, lambda u:u.received_award_count, g.db.query(User))
	return render_template("leaderboard.html", v=v, leaderboard=leaderboard)

@app.get("/leaderboard/badges")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard_badges(v):
	leaderboard = Leaderboard("Badges", "badges", "badges", "Badges", None, Leaderboard.get_badge_emoji_lb, Badge.user_id, v, None, None)
	return render_template("leaderboard.html", v=v, leaderboard=leaderboard)

@app.get("/leaderboard/most_blocked")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard_most_blocked(v):
	leaderboard = Leaderboard("Most blocked", "most blocked", "most-blocked", "Blocked By", "blockers", Leaderboard.get_blockers_lb, UserBlock.target_id, v, None, None)
	return render_template("leaderboard.html", v=v, leaderboard=leaderboard)

@app.get("/leaderboard/owned_hats")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard_owned_hats(v):
	leaderboard = Leaderboard("Owned hats", "owned hats", "owned-hats", "Owned Hats", None, Leaderboard.get_hat_lb, User.owned_hats, v, None, None)
	return render_template("leaderboard.html", v=v, leaderboard=leaderboard)

@app.get("/leaderboard/designed_hats")
@feature_required('HAT_SUBMISSIONS')
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard_designed_hats(v):
	leaderboard = Leaderboard("Designed hats", "designed hats", "designed-hats", "Designed Hats", None, Leaderboard.get_hat_lb, User.designed_hats, v, None, None)
	return render_template("leaderboard.html", v=v, leaderboard=leaderboard)

@app.get("/leaderboard/emojis_made")
@feature_required('EMOJI_SUBMISSIONS')
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard_emojis_made(v):
	leaderboard = Leaderboard("Emojis made", "emojis made", "emojis-made", "Emojis Made", None, Leaderboard.get_badge_emoji_lb, Emoji.author_id, v, None, None)
	return render_template("leaderboard.html", v=v, leaderboard=leaderboard)

@app.get("/leaderboard/upvotes_given")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard_upvotes_given(v):
	leaderboard = Leaderboard("Upvotes given", "upvotes given", "upvotes-given", "Upvotes Given", "upvoting", Leaderboard.get_upvotes_lb, None, v, None, None)
	return render_template("leaderboard.html", v=v, leaderboard=leaderboard)

@app.get("/leaderboard/downvotes_received")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard_downvotes_received(v):
	leaderboard = Leaderboard("Downvotes received", "downvotes received", "downvotes-received", "Downvotes Received", "downvoters", Leaderboard.get_downvotes_lb, None, v, None, None)
	return render_template("leaderboard.html", v=v, leaderboard=leaderboard)

@app.get("/leaderboard/casino_winnings_top")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard_casino_winnings_top(v):
	leaderboard = Leaderboard("Casino winnings (top)", "casino winnings", "casino-winnings-top", "Casino Winnings", None, Leaderboard.get_winnings_lb, CasinoGame.winnings, v, None, None)
	return render_template("leaderboard.html", v=v, leaderboard=leaderboard)

@app.get("/leaderboard/casino_winnings_bottom")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard_casino_winnings_bottom(v):
	leaderboard = Leaderboard("Casino winnings (bottom)", "casino winnings", "casino-winnings-bottom", "Casino Winnings", None, Leaderboard.get_winnings_lb, CasinoGame.winnings, v, None, None, 25, False)
	return render_template("leaderboard.html", v=v, leaderboard=leaderboard)

@app.get("/leaderboard/average_upvotes_per_post")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard_average_upvotes_per_post(v):
	leaderboard = Leaderboard("Average upvotes per post", "average upvotes per post", "average-upvotes-per-post", "Average Upvotes per Post", "posts", Leaderboard.get_avg_upvotes_lb, Post, v, None, None)
	return render_template("leaderboard.html", v=v, leaderboard=leaderboard)

@app.get("/leaderboard/average_upvotes_per_comment")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leaderboard_average_upvotes_per_comment(v):
	leaderboard = Leaderboard("Average upvotes per comment", "average upvotes per comment", "average-upvotes-per-comment", "Average Upvotes per Comment", "comments", Leaderboard.get_avg_upvotes_lb, Comment, v, None, None)
	return render_template("leaderboard.html", v=v, leaderboard=leaderboard)
