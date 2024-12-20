from math import floor
import random

from files.helpers.config.const import *
from files.helpers.lottery import *

special_min = 100
special_max = 200
standard_min = 12
standard_max = 100
lotterizer_rate = 33

def check_for_treasure(from_comment, in_text):
	user = from_comment.author

	if not FEATURES['GAMBLING']: return

	seed = random.randint(1, 1000)
	is_special = seed == 1000
	is_standard = seed >= 990
	amount = 0

	if is_special:
		amount = random.randint(special_min, special_max)
	elif is_standard:
		amount = random.randint(standard_min, standard_max)
		if random.randint(1, 100) > 90:
			amount = -amount


	if amount != 0:
		if amount > 0:
			lottery_tickets_seed = random.randint(1, 100)
			lottery_tickets_instead = lottery_tickets_seed <= lotterizer_rate
			if lottery_tickets_instead and get_active_lottery():
				ticket_count = floor(amount / LOTTERY_TICKET_COST)
				grant_lottery_tickets_to_user(user, ticket_count)
				from_comment.treasure_amount = f'l{ticket_count}'
				return

		user.pay_account('coins', amount, f"Found treasure in {from_comment.textlink}")
		from_comment.treasure_amount = str(amount)
