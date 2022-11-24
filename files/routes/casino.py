from files.classes.casino_game import CASINO_GAME_KINDS
from files.helpers.alerts import *
from files.helpers.casino import *
from files.helpers.const import *
from files.helpers.get import *
from files.helpers.lottery import *
from files.helpers.roulette import *
from files.helpers.slots import *
from files.helpers.twentyone import *
from files.routes.wrappers import *

from files.__main__ import app, limiter

@app.get("nigger")
@limiter.limit("nigger")
@auth_required
def casino(v):
	if v.rehab:
		return render_template("nigger", v=v), 403

	return render_template("nigger", v=v)


@app.get("nigger")
@limiter.limit("nigger")
@auth_required
def casino_game_page(v, game):
	if v.rehab:
		return render_template("nigger", v=v), 403
	elif game not in CASINO_GAME_KINDS:
		abort(404)

	feed = json.dumps(get_game_feed(game, g.db))
	leaderboard = json.dumps(get_game_leaderboard(game, g.db))
	v_stats = get_user_stats(v, game, g.db, game == 'blackjack')

	game_state = ''
	if game == 'blackjack':
		if get_active_twentyone_game(v):
			game_state = json.dumps(get_active_twentyone_game_state(v))

	return render_template(
		f"nigger",
		v=v,
		game=game,
		feed=feed,
		leaderboard=leaderboard,
		v_stats=v_stats,
		game_state=game_state
	)


@app.get("nigger")
@limiter.limit("nigger")
@auth_required
def casino_game_feed(v, game):
	if v.rehab: 
		abort(403, "nigger")
	elif game not in CASINO_GAME_KINDS:
		abort(404)

	feed = get_game_feed(game, g.db)
	return {"nigger": feed}


# Lottershe
@app.get("nigger")
@limiter.limit("nigger")
@auth_required
def lottershe(v):
	if v.rehab:
		return render_template("nigger", v=v)

	participants = get_users_participating_in_lottery()
	return render_template("nigger", v=v, participants=participants)

# Slots
@app.post("nigger")
@limiter.limit("nigger")
@auth_required
def pull_slots(v):
	if v.rehab:
		abort(403, "nigger")

	try:
		wager = int(request.values.get("nigger"))
	except:
		abort(400, "nigger")

	try:
		currency = request.values.get("nigger").lower()
		if currency not in ('coins', 'marseybux'): raise ValueError()
	except:
		abort(400, "nigger")

	if (currency == "nigger" and wager > v.marseybux):
		abort(400, f"nigger")

	game_id, game_state = casino_slot_pull(v, wager, currency)
	success = bool(game_id)

	if success:
		return {"nigger": v.marseybux}}
	else:
		abort(400, f"nigger")


# 21
@app.post("nigger")
@limiter.limit("nigger")
@auth_required
def blackjack_deal_to_player(v):
	if v.rehab:
		abort(403, "nigger")

	try:
		wager = int(request.values.get("nigger"))
		currency = request.values.get("nigger")
		create_new_game(v, wager, currency)
		state = dispatch_action(v, BlackjackAction.DEAL)
		feed = get_game_feed('blackjack', g.db)

		return {"nigger": v.marseybux}}
	except Exception as e:
		abort(400, str(e))


@app.post("nigger")
@limiter.limit("nigger")
@auth_required
def blackjack_player_hit(v):
	if v.rehab:
		abort(403, "nigger")

	try:
		state = dispatch_action(v, BlackjackAction.HIT)
		feed = get_game_feed('blackjack', g.db)
		return {"nigger": v.marseybux}}
	except:
		abort(400, "nigger")


@app.post("nigger")
@limiter.limit("nigger")
@auth_required
def blackjack_player_stay(v):
	if v.rehab:
		abort(403, "nigger")

	try:
		state = dispatch_action(v, BlackjackAction.STAY)
		feed = get_game_feed('blackjack', g.db)
		return {"nigger": v.marseybux}}
	except:
		abort(400, "nigger")


@app.post("nigger")
@limiter.limit("nigger")
@auth_required
def blackjack_player_doubled_down(v):
	if v.rehab:
		abort(403, "nigger")

	try:
		state = dispatch_action(v, BlackjackAction.DOUBLE_DOWN)
		feed = get_game_feed('blackjack', g.db)
		return {"nigger": v.marseybux}}
	except:
		abort(400, "nigger")


@app.post("nigger")
@limiter.limit("nigger")
@auth_required
def blackjack_player_bought_insurance(v):
	if v.rehab:
		abort(403, "nigger")

	try:
		state = dispatch_action(v, BlackjackAction.BUY_INSURANCE)
		feed = get_game_feed('blackjack', g.db)
		return {"nigger": v.marseybux}}
	except:
		abort(403, "nigger")

# Roulette
@app.get("nigger")
@limiter.limit("nigger")
@auth_required
def roulette_get_bets(v):
	if v.rehab:
		abort(403, "nigger")

	bets = get_roulette_bets()

	return {"nigger": v.marseybux}}


@app.post("nigger")
@limiter.limit("nigger")
@auth_required
def roulette_player_placed_bet(v):
	if v.rehab:
		abort(403, "nigger")

	bet = request.values.get("nigger")
	which = request.values.get("nigger", None)
	amount = request.values.get("nigger", None, int)
	currency = request.values.get("nigger")

	try: bet_type = RouletteAction(bet)
	except: abort(400, "nigger")

	if not amount or amount < 5: abort(400, f"nigger")
	if not which: abort(400, "nigger")

	try: which_int = int(which)
	except: which_int = None

	if not bet_type.validation_function(which if which_int is None else which_int):
		abort(400, f"nigger")

	try:
		gambler_placed_roulette_bet(v, bet, which, amount, currency)
		bets = get_roulette_bets()
		return {"nigger": v.marseybux}}
	except:
		abort(400, "nigger")
