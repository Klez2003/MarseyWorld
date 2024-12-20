from files.classes.casino_game import CASINO_GAME_KINDS
from files.helpers.alerts import *
from files.helpers.casino import *
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.lottery import *
from files.helpers.roulette import *
from files.helpers.slots import *
from files.helpers.twentyone import *
from files.routes.wrappers import *

from files.__main__ import app, limiter

@app.get("/casino")
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def casino(v):
	if v.rehab:
		return render_template("casino/rehab.html", v=v), 403

	return render_template("casino.html", v=v)


@app.get("/casino/<game>")
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def casino_game_page(v, game):
	if v.rehab:
		return render_template("casino/rehab.html", v=v), 403
	elif game not in CASINO_GAME_KINDS:
		stop(404)

	feed = json.dumps(get_game_feed(game))
	leaderboard = json.dumps(get_game_leaderboard(game))
	v_stats = get_user_stats(v, game, game == 'blackjack')

	game_state = ''
	if game == 'blackjack':
		if get_active_twentyone_game(v):
			game_state = json.dumps(get_active_twentyone_game_state(v))

	return render_template(
		f"casino/{game}_screen.html",
		v=v,
		game=game,
		feed=feed,
		leaderboard=leaderboard,
		v_stats=v_stats,
		game_state=game_state
	)


@app.get("/casino/<game>/feed")
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def casino_game_feed(v, game):
	if v.rehab:
		stop(403, "You are under Rehab award effect!")
	elif game not in CASINO_GAME_KINDS:
		stop(404)

	feed = get_game_feed(game)
	return {"feed": feed}


# Lottershe
@app.get("/lottershe")
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def lottershe(v):
	if v.rehab:
		return render_template("casino/rehab.html", v=v)

	participants = get_users_participating_in_lottery()
	return render_template("lottery.html", v=v, participants=participants)

# Slots
@app.post("/casino/slots")
@limiter.limit('1/second', scope=rpath) #Needed to fix race condition
@limiter.limit('1/second', scope=rpath, key_func=get_ID) #Needed to fix race condition
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def pull_slots(v):
	if v.rehab:
		stop(403, "You are under Rehab award effect!")

	try:
		wager = int(request.values.get("wager"))
	except:
		stop(400, "Invalid wager!")

	try:
		currency = request.values.get("currency", "").lower()
		if currency not in {'coins', 'marseybux'}: raise ValueError()
	except:
		stop(400, "Invalid currency (expected 'coins' or 'marseybux').")

	if (currency == "coins" and wager > v.coins) or (currency == "marseybux" and wager > v.marseybux):
		stop(400, f"You don't have enough {currency} to make that bet!")

	game_id, game_state = casino_slot_pull(v, wager, currency)
	success = bool(game_id)

	if success:
		return {"game_state": game_state, "gambler": {"coins": v.coins, "marseybux": v.marseybux}}
	else:
		stop(400, f"Wager must be 5 {currency} or more")


# 21
@app.post("/casino/twentyone/deal")
@limiter.limit('1/second', scope=rpath) #Needed to fix race condition
@limiter.limit('1/second', scope=rpath, key_func=get_ID) #Needed to fix race condition
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def blackjack_deal_to_player(v):
	if v.rehab:
		stop(403, "You are under Rehab award effect!")

	try:
		wager = int(request.values.get("wager"))
		currency = request.values.get("currency")
		create_new_game(v, wager, currency)
		state = dispatch_action(v, BlackjackAction.DEAL)
		feed = get_game_feed('blackjack')

		return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "marseybux": v.marseybux}}
	except Exception as e:
		stop(400, str(e))


@app.post("/casino/twentyone/hit")
@limiter.limit('1/second', scope=rpath) #Needed to fix race condition
@limiter.limit('1/second', scope=rpath, key_func=get_ID) #Needed to fix race condition
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def blackjack_player_hit(v):
	if v.rehab:
		stop(403, "You are under Rehab award effect!")

	try:
		hand = request.args.get('hand')
		state = dispatch_action(v, BlackjackAction.HIT, True if hand == 'split' else False)
		feed = get_game_feed('blackjack')
		return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "marseybux": v.marseybux}}
	except:
		stop(400, "Unable to hit!")


@app.post("/casino/twentyone/stay")
@limiter.limit('1/second', scope=rpath) #Needed to fix race condition
@limiter.limit('1/second', scope=rpath, key_func=get_ID) #Needed to fix race condition
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def blackjack_player_stay(v):
	if v.rehab:
		stop(403, "You are under Rehab award effect!")

	try:
		hand = request.args.get('hand')
		state = dispatch_action(v, BlackjackAction.STAY, True if hand == 'split' else False)
		feed = get_game_feed('blackjack')
		return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "marseybux": v.marseybux}}
	except:
		stop(400, "Unable to stay!")


@app.post("/casino/twentyone/double_down")
@limiter.limit('1/second', scope=rpath) #Needed to fix race condition
@limiter.limit('1/second', scope=rpath, key_func=get_ID) #Needed to fix race condition
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def blackjack_player_doubled_down(v):
	if v.rehab:
		stop(403, "You are under Rehab award effect!")

	try:
		state = dispatch_action(v, BlackjackAction.DOUBLE_DOWN)
		feed = get_game_feed('blackjack')
		return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "marseybux": v.marseybux}}
	except:
		stop(400, "Unable to double down!")


@app.post("/casino/twentyone/buy_insurance")
@limiter.limit('1/second', scope=rpath) #Needed to fix race condition
@limiter.limit('1/second', scope=rpath, key_func=get_ID) #Needed to fix race condition
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def blackjack_player_bought_insurance(v):
	if v.rehab:
		stop(403, "You are under Rehab award effect!")

	try:
		state = dispatch_action(v, BlackjackAction.BUY_INSURANCE)
		feed = get_game_feed('blackjack')
		return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "marseybux": v.marseybux}}
	except:
		stop(403, "Unable to buy insurance!")

@app.post("/casino/twentyone/split")
@limiter.limit('1/second', scope=rpath) #Needed to fix race condition
@limiter.limit('1/second', scope=rpath, key_func=get_ID) #Needed to fix race condition
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def split(v):
	if v.rehab:
		stop(403, "You are under Rehab award effect!")

	try:
		state = dispatch_action(v, BlackjackAction.SPLIT)
		feed = get_game_feed('blackjack')
		return {"success": True, "state": state, "feed": feed, "gambler": {"coins": v.coins, "marseybux": v.marseybux}}
	except:
		stop(403, "Unable to split!")

# Roulette
@app.get("/casino/roulette/bets")
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def roulette_get_bets(v):
	if v.rehab:
		stop(403, "You are under Rehab award effect!")

	bets = get_roulette_bets()

	return {"success": True, "bets": bets, "gambler": {"coins": v.coins, "marseybux": v.marseybux}}


@app.post("/casino/roulette/place_bet")
@limiter.limit('1/second', scope=rpath) #Needed to fix race condition
@limiter.limit('1/second', scope=rpath, key_func=get_ID) #Needed to fix race condition
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(CASINO_CSS_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def roulette_player_placed_bet(v):
	if v.rehab:
		stop(403, "You are under Rehab award effect!")

	bet = request.values.get("bet")
	which = request.values.get("which", None)
	amount = request.values.get("wager", None, int)
	currency = request.values.get("currency")

	try: bet_type = RouletteAction(bet)
	except: stop(400, "Not a valid roulette bet type")

	if not amount or amount < 5: stop(400, f"Minimum bet is 5 {currency}.")
	if not which: stop(400, "Not a valid roulette bet")

	try: which_int = int(which)
	except: which_int = None

	if not bet_type.validation_function(which if which_int is None else which_int):
		stop(400, f"Not a valid roulette bet for bet type {bet_type.value[0]}")

	try:
		gambler_placed_roulette_bet(v, bet, which, amount, currency)
		bets = get_roulette_bets()
		return {"success": True, "bets": bets, "gambler": {"coins": v.coins, "marseybux": v.marseybux}}
	except:
		stop(400, "Unable to place a bet!")
