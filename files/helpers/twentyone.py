import json
import random
from enum import Enum
from math import floor

from flask import g

from files.classes.casino_game import CasinoGame
from files.classes.currency_logs import CurrencyLog
from files.helpers.casino import distribute_wager_badges

from sqlalchemy.orm.exc import MultipleResultsFound

class BlackjackStatus(str, Enum):
	PLAYING = "PLAYING"
	STAYED = "STAYED"
	PUSHED = "PUSHED"
	WON = "WON"
	LOST = "LOST"
	BLACKJACK = "BLACKJACK"


class BlackjackAction(str, Enum):
	DEAL = "DEAL"
	HIT = "HIT"
	STAY = "STAY"
	DOUBLE_DOWN = "DOUBLE_DOWN"
	BUY_INSURANCE = "BUY_INSURANCE"
	SPLIT = 'SPLIT'
	HIT_SPLIT = 'HIT_SPLIT'
	STAY_SPLIT = 'STAY_SPLIT'


ranks = ("2", "3", "4", "5", "6", "7", "8", "9", "X", "J", "Q", "K", "A")
suits = ("S", "H", "C", "D")
deck = [rank + suit for rank in ranks for suit in suits]
deck_count = 4
minimum_bet = 5


def get_initial_state():
	return {
		"player": [],
		"player_split": [],
		"player_split_value": 0,
		"player_value": 0,
		"dealer": [],
		"dealer_value": 0,
		"has_player_split": False,
		"player_bought_insurance": False,
		"player_doubled_down": False,
		"status": BlackjackStatus.PLAYING,
		"status_split": BlackjackStatus.PLAYING,
		"actions": [],
		"wager": {
			"amount": 0,
			"currency": "coins"
		},
		"payout": 0,
	}


def build_casino_game(gambler, wager, currency):
	initial_state = get_initial_state()
	initial_state['wager']['amount'] = wager
	initial_state['wager']['currency'] = currency

	casino_game = CasinoGame()
	casino_game.user_id = gambler.id
	casino_game.currency = currency
	casino_game.wager = wager
	casino_game.winnings = 0
	casino_game.kind = 'blackjack'
	casino_game.game_state = json.dumps(initial_state)
	casino_game.active = True
	g.db.add(casino_game)

	return casino_game


def get_active_twentyone_game(gambler):
	try:
		return g.db.query(CasinoGame).filter(
		CasinoGame.active == True,
		CasinoGame.kind == 'blackjack',
		CasinoGame.user_id == gambler.id).one_or_none()
	except MultipleResultsFound:
		games = g.db.query(CasinoGame).filter(
		CasinoGame.active == True,
		CasinoGame.kind == 'blackjack',
		CasinoGame.user_id == gambler.id).all()
		for game in games:
			g.db.delete(game)
		g.db.commit()
		return None

def get_active_twentyone_game_state(gambler):
	active_game = get_active_twentyone_game(gambler)
	full_state = active_game.game_state_json
	return remove_exploitable_information(full_state)


def charge_gambler(gambler, amount, currency):
	charged = gambler.charge_account(currency, amount)

	if not charged:
		raise Exception("Gambler cannot afford charge.")


def create_new_game(gambler, wager, currency):
	existing_game = get_active_twentyone_game(gambler)
	over_minimum_bet = wager >= minimum_bet

	if existing_game:
		existing_game.active = False
		g.db.add(existing_game)

	if not over_minimum_bet:
		raise Exception(f"Gambler must bet over {minimum_bet} {currency}.")

	try:
		charge_gambler(gambler, wager, currency)
		new_game = build_casino_game(gambler, wager, currency)
		g.db.add(new_game)
		g.db.flush()
	except:
		raise Exception(f"Gambler cannot afford to bet {wager} {currency}.")


def handle_blackjack_deal(state, split):
	deck = build_deck(state)
	first = deck.pop()
	second = deck.pop()
	third = deck.pop()
	fourth = deck.pop()
	state['player'] = [first, third]
	state['dealer'] = [second, fourth]

	return state


def handle_blackjack_hit(state, split = False):
	deck = build_deck(state)
	if(split and state['has_player_split'] and state['status_split'] != BlackjackStatus.LOST):
		next_card = deck.pop()
		state['player_split'].append(next_card)
	elif(state['status'] != BlackjackStatus.LOST):
		next_card = deck.pop()
		state['player'].append(next_card)

	return state


def handle_blackjack_stay(state, split = False):
	if(split and state['has_player_split'] and state['status_split'] != BlackjackStatus.LOST):
		state['status_split'] = BlackjackStatus.STAYED
	elif(state['status'] != BlackjackStatus.LOST):
		state['status'] = BlackjackStatus.STAYED

	return state


def handle_blackjack_double_down(state, split):
	state['player_doubled_down'] = True
	state = handle_blackjack_hit(state)
	state = handle_blackjack_stay(state)

	return state


def handle_blackjack_buy_insurance(state, split):
	state['player_bought_insurance'] = True

	return state

def handle_split(state, split):
	state['has_player_split'] = True
	state['player_split'] = [state['player'].pop()]

	state = handle_blackjack_hit(state)
	state = handle_blackjack_hit(state, True)

	return state


def check_for_completion(state):
	has_split = state['has_player_split']
	after_initial_deal = len(
		state['player']) == 2 and len(state['dealer']) == 2 and not has_split
	player_hand_value = get_value_of_hand(state['player'])
	player_split_hand_value = get_value_of_hand(state['player_split'])
	dealer_hand_value = get_value_of_hand(state['dealer'])

	# Both player and dealer were initially dealt 21: Push.
	if after_initial_deal and player_hand_value == 21 and dealer_hand_value == 21:
		state['status'] = BlackjackStatus.PUSHED
		return True, state

	# Player was originally dealt 21, dealer was not: Blackjack.
	if after_initial_deal and player_hand_value == 21:
		state['status'] = BlackjackStatus.BLACKJACK
		return True, state

	# Player went bust: Lost.
	if player_hand_value == -1 and state['status'] != BlackjackStatus.LOST:
		state['status'] = BlackjackStatus.LOST
		if(not has_split or state['status_split'] == BlackjackStatus.LOST):
			return True, state

	# Player went bust: Lost.
	if player_split_hand_value == -1 and state['status_split'] != BlackjackStatus.LOST:
		state['status_split'] = BlackjackStatus.LOST
		if state['status'] == BlackjackStatus.LOST:
			return True, state

	hand_terminal_status = state['status'] in [BlackjackStatus.LOST, BlackjackStatus.STAYED]
	hand_split_terminal_status = not has_split or state['status_split'] in [BlackjackStatus.LOST, BlackjackStatus.STAYED]

	# Player chose to stay: Deal rest for dealer then determine winner.
	if hand_split_terminal_status and hand_terminal_status:
		deck = build_deck(state)

		while dealer_hand_value < 17 and dealer_hand_value != -1:
			next_card = deck.pop()
			state['dealer'].append(next_card)
			dealer_hand_value = get_value_of_hand(state['dealer'])

		if((not has_split) or state['status'] != BlackjackStatus.LOST):
			if player_hand_value > dealer_hand_value or dealer_hand_value == -1:
				state['status'] = BlackjackStatus.WON
			elif dealer_hand_value > player_hand_value:
				state['status'] = BlackjackStatus.LOST
			else:
				state['status'] = BlackjackStatus.PUSHED

		state['player_value'] = get_value_of_hand(state['player'])
		state['dealer_value'] = get_value_of_hand(state['dealer'])

		if has_split and state['status_split'] != BlackjackStatus.LOST:
			if player_split_hand_value > dealer_hand_value or dealer_hand_value == -1:
				state['status_split'] = BlackjackStatus.WON
			elif dealer_hand_value > player_split_hand_value:
				state['status_split'] = BlackjackStatus.LOST
			else:
				state['status_split'] = BlackjackStatus.PUSHED

		state['player_split_value'] = get_value_of_hand(state['player_split'])

		return True, state

	return False, state


def does_insurance_apply(state):
	dealer = state['dealer']
	dealer_hand_value = get_value_of_hand(dealer)
	dealer_first_card_ace = dealer[0][0] == 'A'
	dealer_never_hit = len(dealer) == 2
	return not state['has_player_split'] and dealer_hand_value == 21 and dealer_first_card_ace and dealer_never_hit


def can_purchase_insurance(state):
	dealer = state['dealer']
	dealer_first_card_ace = dealer[0][0] == 'A'
	dealer_never_hit = len(dealer) == 2
	return not state['has_player_split'] and dealer_first_card_ace and dealer_never_hit and not state['player_bought_insurance']


def can_double_down(state):
	player = state['player']
	player_hand_value = get_value_of_hand(player)
	player_never_hit = len(player) == 2
	return not state['has_player_split'] and player_hand_value in (9, 10, 11) and player_never_hit

def can_split(state):
	player = state['player']
	player_never_hit = len(player) == 2
	hand_can_split = get_value_of_card(player[0]) == get_value_of_card(player[1])
	player_has_split = state['has_player_split']
	return hand_can_split and player_never_hit and not player_has_split


def handle_payout(gambler, state, game):
	status = state['status']
	split_status = state['status_split']
	payout = 0

	if status == BlackjackStatus.BLACKJACK:
		game.winnings = floor(game.wager * 3/2)
		payout = game.wager + game.winnings
	elif status == BlackjackStatus.WON:
		game.winnings = game.wager
		payout = game.wager * 2
	elif status == BlackjackStatus.LOST:
		dealer = state['dealer']
		dealer_first_card_ace = dealer[0][0] == 'A'
		dealer_never_hit = len(dealer) == 2
		dealer_hand_value = get_value_of_hand(dealer) == 21
		insurance_applies = dealer_hand_value == 21 and dealer_first_card_ace and dealer_never_hit

		if insurance_applies and state['player_bought_insurance']:
			game.winnings = 0
			payout = game.wager
		else:
			game.winnings = -game.wager
			payout = 0
	elif status == BlackjackStatus.PUSHED:
		game.winnings = 0
		payout = game.wager
	else:
		raise Exception("Attempted to payout a game that has not finished.")

	if split_status == BlackjackStatus.WON:
		game.winnings += game.wager
		payout += game.wager * 2
	elif split_status == BlackjackStatus.LOST:
		game.winnings += -game.wager
	elif split_status == BlackjackStatus.PUSHED:
		payout += game.wager

	gambler.pay_account(game.currency, payout)

	if game.winnings:
		currency_log = CurrencyLog(
			user_id=gambler.id,
			currency=game.currency,
			amount=game.winnings,
			reason="Blackjack bet",
		)
		g.db.add(currency_log)
		if game.currency == 'coins':
			currency_log.balance = gambler.coins
		else:
			currency_log.balance = gambler.marseybux

	if status in {BlackjackStatus.BLACKJACK, BlackjackStatus.WON} or split_status in {BlackjackStatus.WON}:
		distribute_wager_badges(gambler, game.wager, won=True)
	elif status == BlackjackStatus.LOST or split_status == BlackjackStatus.LOST:
		distribute_wager_badges(gambler, game.wager, won=False)

	game.active = False
	g.db.add(game)

	return payout


def remove_exploitable_information(state):
	safe_state = state

	if len(safe_state['dealer']) >= 2:
		safe_state['dealer'][1] = '?'

	safe_state['dealer_value'] = '?'
	return safe_state


action_handlers = {
	BlackjackAction.DEAL: handle_blackjack_deal,
	BlackjackAction.HIT: handle_blackjack_hit,
	BlackjackAction.STAY: handle_blackjack_stay,
	BlackjackAction.DOUBLE_DOWN: handle_blackjack_double_down,
	BlackjackAction.BUY_INSURANCE: handle_blackjack_buy_insurance,
	BlackjackAction.SPLIT: handle_split,
}


def dispatch_action(gambler, action, is_split = False):
	game = get_active_twentyone_game(gambler)
	handler = action_handlers[action]

	if not game:
		raise Exception(
			'Gambler has no active blackjack game.')
	if not handler:
		raise Exception(
			f'Illegal action {action} passed to Blackjack#dispatch_action.')

	state = game.game_state_json

	if action == BlackjackAction.BUY_INSURANCE:
		if not can_purchase_insurance(state):
			raise Exception("Insurance cannot be purchased.")

		charge_gambler(gambler, floor(game.wager / 2), game.currency)
	if action == BlackjackAction.DOUBLE_DOWN:
		if not can_double_down(state):
			raise Exception("Cannot double down.")

		charge_gambler(gambler, game.wager, game.currency)
		game.wager *= 2

	if action == BlackjackAction.SPLIT:
		if not can_split(state):
			raise Exception("Cannot split")

		charge_gambler(gambler, game.wager, game.currency)

	new_state = handler(state, is_split)
	new_state['player_value'] = get_value_of_hand(new_state['player'])
	new_state['dealer_value'] = get_value_of_hand(new_state['dealer'])
	new_state['player_split_value'] = get_value_of_hand(new_state['player_split'])


	game_over, final_state = check_for_completion(new_state)

	new_state['actions'] = get_available_actions(new_state)
	game.game_state = json.dumps(new_state)
	g.db.add(game)

	if game_over:
		payout = handle_payout(gambler, final_state, game)
		final_state['actions'] = [BlackjackAction.DEAL]
		final_state['payout'] = payout
		return final_state
	else:
		safe_state = remove_exploitable_information(new_state)
		return safe_state


def shuffle(collection):
	random.shuffle(collection)
	return collection


def build_deck(state):
	card_counts = {}

	for card in deck:
		card_counts[card] = deck_count

	cards_already_dealt = state['player'].copy()
	cards_already_dealt.extend(state['player_split'].copy())
	cards_already_dealt.extend(state['dealer'].copy())

	for card in cards_already_dealt:
		card_counts[card] = card_counts[card] - 1

	deck_without_already_dealt_cards = []

	for card in deck:
		amount = card_counts[card]

		for _ in range(amount):
			deck_without_already_dealt_cards.append(card)

	return shuffle(deck_without_already_dealt_cards)


def get_value_of_card(card):
	rank = card[0]
	return 0 if rank == "A" else min(ranks.index(rank) + 2, 10)


def get_value_of_hand(hand):
	without_aces = sum(map(get_value_of_card, hand))
	ace_count = sum("A" in c for c in hand)
	possibilities = []

	for i in range(ace_count + 1):
		value = without_aces + (ace_count - i) + i * 11
		possibilities.append(-1 if value > 21 else value)

	return max(possibilities)


def get_available_actions(state):
	actions = []

	if state['status'] == BlackjackStatus.PLAYING:
		actions.append(BlackjackAction.HIT)
		actions.append(BlackjackAction.STAY)

	if state['has_player_split'] and state['status_split'] == BlackjackStatus.PLAYING:
		actions.append(BlackjackAction.HIT_SPLIT)
		actions.append(BlackjackAction.STAY_SPLIT)

	if can_double_down(state):
		actions.append(BlackjackAction.DOUBLE_DOWN)

	if can_purchase_insurance(state):
		actions.append(BlackjackAction.BUY_INSURANCE)

	if can_split(state):
		actions.append(BlackjackAction.SPLIT)

	return actions
