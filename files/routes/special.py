from flask import g, render_template
from sqlalchemy.sql import text

from files.helpers.get import get_accounts_dict
from files.helpers.config.const import *

from files.routes.wrappers import *

from files.__main__ import app, cache, limiter

_special_leaderboard_query = text("""
WITH bet_options AS (
	SELECT p.id AS parent_id, so.id AS option_id, so.exclusive, cnt.count
	FROM post_options so
	JOIN posts p ON so.parent_id = p.id
	JOIN (
		SELECT option_id, COUNT(*) FROM post_option_votes
		GROUP BY option_id
	) AS cnt ON so.id = cnt.option_id
	WHERE p.author_id = 7465 AND p.created_utc > 1688950032
		AND so.exclusive IN (2, 3)
),
post_payouts AS (
	SELECT
		sq_total.parent_id,
		sq_winners.sum AS bettors,
		floor((sq_total.sum * 200) / sq_winners.sum) AS winner_payout
	FROM (
		SELECT parent_id, SUM(count)
		FROM bet_options GROUP BY parent_id
	) AS sq_total
	JOIN (
		SELECT parent_id, SUM(count)
		FROM bet_options WHERE exclusive = 3 GROUP BY parent_id
	) AS sq_winners ON sq_total.parent_id = sq_winners.parent_id
),
bet_votes AS (
	SELECT
		opt.option_id AS option_id,
		opt.exclusive,
		sov.user_id,
		CASE
			WHEN opt.exclusive = 2 THEN -200
			WHEN opt.exclusive = 3 THEN (post_payouts.winner_payout - 200)
		END payout
	FROM post_option_votes sov
	LEFT OUTER JOIN bet_options AS opt
		ON opt.option_id = sov.option_id
	LEFT OUTER JOIN post_payouts
		ON opt.parent_id = post_payouts.parent_id
	WHERE opt.option_id IS NOT NULL
),
bettors AS (
	SELECT
		COALESCE(bet_won.user_id, bet_lost.user_id) AS user_id,
		(COALESCE(bet_won.count_won, 0)
			+ COALESCE(bet_lost.count_lost, 0)) AS bets_total,
		COALESCE(bet_won.count_won, 0) AS bets_won
	FROM (
		SELECT user_id, COUNT(*) AS count_won FROM bet_votes
		WHERE exclusive = 3 GROUP BY user_id) AS bet_won
	FULL OUTER JOIN (
		SELECT user_id, COUNT(*) AS count_lost FROM bet_votes
		WHERE exclusive = 2 GROUP BY user_id
	) AS bet_lost ON bet_won.user_id = bet_lost.user_id
)
SELECT
	bettors.user_id,
	bettors.bets_won,
	bettors.bets_total,
	bet_payout.net AS payout
FROM bettors
LEFT OUTER JOIN (
	SELECT user_id, SUM(payout) AS net FROM bet_votes GROUP BY user_id
) AS bet_payout ON bettors.user_id = bet_payout.user_id
ORDER BY payout DESC, bets_won DESC, bets_total ASC;
""")

@cache.memoize()
def _special_leaderboard_get():
	result = g.db.execute(_special_leaderboard_query).all()
	return result

@app.get('/womenworldcup2023_leaderboard')
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def get_leaderboard(v):
	if SITE_NAME != 'rDrama':
		abort(404)

	result = _special_leaderboard_get()
	if g.is_api_or_xhr: return result
	users = get_accounts_dict([r[0] for r in result], v=v, graceful=True)
	return render_template("special/worldcup22_leaderboard.html",
		v=v, result=result, users=users)
