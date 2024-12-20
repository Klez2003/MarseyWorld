import time
from flask import g
from files.classes.casino_game import CasinoGame
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.useractions import badge_grant

def get_game_feed(game):
	games = g.db.query(CasinoGame) \
		.filter(CasinoGame.active == False, CasinoGame.kind == game) \
		.order_by(CasinoGame.created_utc.desc()).limit(30).all()

	def format_game(game):
		user = g.db.query(User).filter(User.id == game.user_id).one()
		wonlost = 'lost' if game.winnings < 0 else 'won'
		relevant_currency = "coin" if game.currency == "coins" else "marseybux"

		return {
			"user": user.username,
			"won_or_lost": wonlost,
			"amount": commas(abs(game.winnings)),
			"currency": relevant_currency
		}

	return list(map(format_game, games))

def get_user_stats(u, game, include_ties=False):
	games = g.db.query(CasinoGame.user_id, CasinoGame.winnings).filter(CasinoGame.kind == game, CasinoGame.user_id == u.id)
	wins = games.filter(CasinoGame.winnings > 0).count()
	ties = games.filter(CasinoGame.winnings == 0).count() if include_ties else 0
	losses = games.filter(CasinoGame.winnings < 0).count()
	return (wins, ties, losses)

def get_game_leaderboard(game):
	timestamp_24h_ago = time.time() - 86400
	timestamp_all_time = CASINO_RELEASE_DAY # "All Time" starts on release day

	biggest_win_all_time = g.db.query(CasinoGame.user_id, User.username, CasinoGame.currency, CasinoGame.winnings).select_from(
		CasinoGame).join(User).order_by(CasinoGame.winnings.desc()).filter(CasinoGame.user_id != CARP_ID, CasinoGame.kind == game, CasinoGame.created_utc > timestamp_all_time).limit(1).one_or_none()

	biggest_win_last_24h = g.db.query(CasinoGame.user_id, User.username, CasinoGame.currency, CasinoGame.winnings).select_from(
		CasinoGame).join(User).order_by(CasinoGame.winnings.desc()).filter(CasinoGame.user_id != CARP_ID, CasinoGame.kind == game, CasinoGame.created_utc > timestamp_24h_ago).limit(1).one_or_none()

	biggest_loss_all_time = g.db.query(CasinoGame.user_id, User.username, CasinoGame.currency, CasinoGame.winnings).select_from(
		CasinoGame).join(User).order_by(CasinoGame.winnings).filter(CasinoGame.user_id != CARP_ID, CasinoGame.kind == game, CasinoGame.created_utc > timestamp_all_time).limit(1).one_or_none()

	biggest_loss_last_24h = g.db.query(CasinoGame.user_id, User.username, CasinoGame.currency, CasinoGame.winnings).select_from(
		CasinoGame).join(User).order_by(CasinoGame.winnings).filter(CasinoGame.user_id != CARP_ID, CasinoGame.kind == game, CasinoGame.created_utc > timestamp_24h_ago).limit(1).one_or_none()

	if not biggest_win_all_time:
		biggest_win_all_time = [None, None, None, 0]

	if not biggest_win_last_24h:
		biggest_win_last_24h = [None, None, None, 0]

	if not biggest_loss_all_time:
		biggest_loss_all_time = [None, None, None, 0]

	if not biggest_loss_last_24h:
		biggest_loss_last_24h = [None, None, None, 0]


	return {
		"all_time": {
			"biggest_win": {
				"user": biggest_win_all_time[1],
				"currency": biggest_win_all_time[2],
				"amount": commas(biggest_win_all_time[3])
			},
			"biggest_loss": {
				"user": biggest_loss_all_time[1],
				"currency": biggest_loss_all_time[2],
				"amount": commas(abs(biggest_loss_all_time[3]))
			}
		},
		"last_24h": {
			"biggest_win": {
				"user": biggest_win_last_24h[1],
				"currency": biggest_win_last_24h[2],
				"amount": commas(biggest_win_last_24h[3])
			},
			"biggest_loss": {
				"user": biggest_loss_last_24h[1],
				"currency": biggest_loss_last_24h[2],
				"amount": commas(abs(biggest_loss_last_24h[3]))
			}
		}
	}


def distribute_wager_badges(user, wager, won):
	badges_earned = set()

	if won:
		if wager >= 1000:
			badges_earned.add(160)
		if wager >= 10000:
			badges_earned.add(161)
		if wager >= 100000:
			badges_earned.add(162)
	else:
		if wager >= 1000:
			badges_earned.add(157)
		if wager >= 10000:
			badges_earned.add(158)
		if wager >= 100000:
			badges_earned.add(159)

	for badge in badges_earned:
		badge_grant(user, badge)
