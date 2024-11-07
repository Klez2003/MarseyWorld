import string
from copy import deepcopy

from flask import g, request
from sqlalchemy import func

from files.classes.award import AwardRelationship
from files.classes.userblock import UserBlock
from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.slurs_and_profanities import censor_slurs_profanities
from files.helpers.config.awards import *
from files.helpers.get import *
from files.helpers.regex import *
from files.helpers.sanitize import *
from files.helpers.useractions import *
from files.routes.wrappers import *
from files.routes.routehelpers import get_alt_graph_ids
from files.__main__ import app, cache, limiter

from .front import frontlist

@app.get("/shop")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def shop_awards(v):
	return redirect('/shop/awards')

@app.get("/shop/awards")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def shop(v):
	AWARDS = deepcopy(AWARDS_ENABLED(v))

	for val in AWARDS.values(): val["owned"] = 0

	for useraward in g.db.query(AwardRelationship).filter(AwardRelationship.user_id == v.id, AwardRelationship.post_id == None, AwardRelationship.comment_id == None):
		if useraward.kind in AWARDS: AWARDS[useraward.kind]["owned"] += 1

	for val in AWARDS.values():
		val["baseprice"] = int(val["price"])
		val["price"] = int(val["price"] * v.award_discount)
		if v.house.endswith(' Founder') and val["kind"] in {"earlylife", "rainbow", "sharpen", "owoify", "bite"}:
			val["price"] = int(val["price"] * 0.75)

	sales = g.db.query(func.sum(User.currency_spent_on_awards)).scalar()
	return render_template("shop.html", awards=list(AWARDS.values()), v=v, sales=sales)


def buy_awards(v, kind, AWARDS, quantity):
	og_price = AWARDS[kind]["price"]
	price = int(og_price * v.award_discount)
	if v.house.endswith(' Founder') and kind in {"earlylife", "rainbow", "sharpen", "owoify", "bite"}:
		price = int(price * 0.75)

	if kind == "grass":
		currency = 'coins'
	elif kind == "benefactor":
		currency = 'marseybux'
	else:
		currency = 'coins/marseybux'

	if quantity == 1:
		s = ""
		es = ""
	else:
		s = "s"
		es = "es"

	charged = v.charge_account(currency, price*quantity, f"Cost of {quantity} {AWARDS[kind]['title']} award{s}")
	if not charged:
		stop(400, f"Not enough {currency}!")

	v.currency_spent_on_awards += price*quantity
	if v.currency_spent_on_awards >= 1000000:
		badge_grant(badge_id=73, user=v)
	if v.currency_spent_on_awards >= 500000:
		badge_grant(badge_id=72, user=v)
	if v.currency_spent_on_awards >= 250000:
		badge_grant(badge_id=71, user=v)
	if v.currency_spent_on_awards >= 100000:
		badge_grant(badge_id=70, user=v)
	if v.currency_spent_on_awards >= 10000:
		badge_grant(badge_id=69, user=v)
	g.db.add(v)

	if kind == "lootbox":
		lootbox_items = []
		for _ in range(LOOTBOX_ITEM_COUNT*quantity): # five items per lootbox
			LOOTBOX_CONTENTS = [x["kind"] for x in AWARDS_ENABLED(v).values() if x["included_in_lootbox"]]
			lb_award = random.choice(LOOTBOX_CONTENTS)
			lootbox_items.append(AWARDS[lb_award]['title'])
			lb_award = AwardRelationship(user_id=v.id, kind=lb_award, price_paid=0)
			g.db.add(lb_award)

		v.lootboxes_bought += quantity
		lootbox_msg = f"You open your lootbox{es} and receive: " + ', '.join(lootbox_items)
		send_repeatable_notification(v.id, lootbox_msg)

		if v.lootboxes_bought == 10:
			badge_grant(badge_id=76, user=v)
		elif v.lootboxes_bought == 50:
			badge_grant(badge_id=77, user=v)
		elif v.lootboxes_bought == 150:
			badge_grant(badge_id=78, user=v)

		return {"message": lootbox_msg}
	else:
		award_objects = []
		for x in range(quantity):
			award_object = AwardRelationship(user_id=v.id, kind=kind, price_paid=price)
			g.db.add(award_object)
			award_objects.append(award_object)

		if CARP_ID and v.id != CARP_ID and og_price >= 5000:
			award_title = AWARDS[kind]['title']
			send_repeatable_notification(CARP_ID, f"@{v.username} has bought {quantity} `{award_title}` award{s}!")

		return award_objects


@app.post("/buy/<kind>")
@limiter.limit('1/second', scope=rpath) #Needed to fix race condition
@limiter.limit('1/second', scope=rpath, key_func=get_ID) #Needed to fix race condition
@limiter.limit("100/minute;400/hour;1000/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("100/minute;400/hour;1000/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def buy(v, kind):
	AWARDS = deepcopy(AWARDS_ENABLED(v))

	if kind not in AWARDS: stop(400)

	award_title = AWARDS[kind]['title']

	award = buy_awards(v, kind, AWARDS, 1)

	if isinstance(award, dict):
		return award

	return {"message": f"{award_title} award bought!"}

def alter_body(obj):
	obj.body_html = sanitize(obj.body, limit_pings=5, obj=obj, author=obj.author)
	if isinstance(obj, Post):
		obj.title_html = filter_emojis_only(obj.title, golden=False, obj=obj, author=obj.author)

@app.post("/award/<thing_type>/<int:id>")
@limiter.limit('1/second', scope=rpath) #Needed to fix race condition
@limiter.limit('1/second', scope=rpath, key_func=get_ID) #Needed to fix race condition
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def award_thing(v, thing_type, id):
	kind = request.values.get("kind", "").strip()

	if thing_type == 'post':
		obj = get_post(id)
	elif thing_type == 'comment':
		obj = get_comment(id)
		if not obj.parent_post and not obj.wall_user_id: stop(404) # don't let users award messages
	else:
		stop(400)

	author = obj.author

	AWARDS = deepcopy(AWARDS_ENABLED(v))

	if kind not in AWARDS:
		stop(404, "This award doesn't exist.")

	if kind == "grass" and v.id == author.id:
		stop(403, "You can't grass yourself.")

	award_title = AWARDS[kind]['title']

	quantity = int(request.values.get("quantity", "1").strip() or 1)
	if quantity < 1 or quantity > 30:
		quantity = 1
	
	if quantity == 1:
		s = ""
		it = "it"
		was = "was"
		has = "has"
	else:
		s = "s"
		it = "they"
		was = "were"
		has = "have"

	if v.shadowbanned:
		return {"message": f"{quantity} {award_title} award{s} given to {thing_type} successfully!"}

	if obj.is_longpost and kind in {"ectoplasm", "candycorn", "candycane", "stab", "glowie", "tilt", "queen", "chud", "marsify", "owoify", "sharpen", "rainbow"}:
		stop(403, f'Long posts and comments are immune to the {award_title} award!')

	if obj.distinguished and (AWARDS[kind]['cosmetic'] or AWARDS[kind]['negative']):
		stop(403, 'Distinguished posts and comments are immune to cosmetic and negative awards!')

	note = request.values.get("note", "").strip()
	if len(note) > 200:
		stop(400, "Award note is too long (max 200 characters)")

	safe_username = f"@{obj.author_name} is"

	if AWARDS[kind]['negative'] and author.immune_to_negative_awards(v):
		if author.new_user and not author.alts:
			stop(403, "New users are immune to negative awards!")
		stop(403, f"{safe_username} immune to negative awards!")

	if isinstance(obj, Post) and obj.id == 210983:
		stop(403, "You can't award this post!")

	if kind == "benefactor":
		if author.id == v.id:
			stop(403, "You can't use this award on yourself!")
		if author.id in get_alt_graph_ids(v.id):
			stop(403, "You can't use this award on your alts!")

	if obj.ghost and not AWARDS[kind]['ghost']:
		stop(403, "This kind of award can't be used on ghost posts!")

	if kind == 'marsify' and author.marsify == 1:
		stop(409, f"{safe_username} already permanently marsified!")

	if kind == 'spider' and author.spider == 1:
		stop(409, f"{safe_username} already best friends with a spider!")

	awards = g.db.query(AwardRelationship).filter(
		AwardRelationship.kind == kind,
		AwardRelationship.user_id == v.id,
		AwardRelationship.post_id == None,
		AwardRelationship.comment_id == None
	).order_by(AwardRelationship.id).limit(quantity).all()
	num_owned = len(awards)

	if quantity > num_owned:
		bought = buy_awards(v, kind, AWARDS, quantity-num_owned)
		if isinstance(bought, dict):
			return bought
		awards.extend(bought)

	if v.id == author.id and kind == "zombiebite":
		stop(403, "You can't bite yourself!")

	if v.id != author.id:
		if author.deflector and v.deflector and AWARDS[kind]['deflectable'] and v.admin_level < PERMS['IMMUNE_TO_DEFLECTIONS']:
			msg = f"@{v.username} has tried to give {obj.textlink} {quantity} {award_title} award{s} but {it} {was} deflected on them, they also had a deflector up, so {it} bounced back and forth until {it} vaporized!"
			send_repeatable_notification(author.id, msg)

			msg = f"{safe_username} under the effect of a deflector award; your {award_title} award{s} {has} been deflected back to you but your deflector protected you, the award{s} bounced back and forth until {it} vaporized!"
			send_repeatable_notification(v.id, msg)

			for award in awards:
				g.db.delete(award)

			return {"message": f"{quantity} {award_title} award{s} given to {thing_type} successfully!"}

		if author.deflector and AWARDS[kind]['deflectable'] and v.admin_level < PERMS['IMMUNE_TO_DEFLECTIONS']:
			author = v
			safe_username = f"Your award{s} {has} been deflected but failed since you're"

			if kind == 'shit':
				not_from_lootbox_quantity = len([award for award in awards if award.price_paid])
				awarded_coins = int(AWARDS[kind]['price'] * COSMETIC_AWARD_COIN_AWARD_PCT) * not_from_lootbox_quantity
				v.charge_account('coins', awarded_coins, f"{quantity} deflected Shit award{s} on {obj.textlink}", should_check_balance=False)
				obj.author.pay_account('coins', awarded_coins, f"{quantity} deflected Shit award{s} on {obj.textlink}")
		elif kind != 'spider':
			not_from_lootbox_quantity = len([award for award in awards if award.price_paid])
			if AWARDS[kind]['cosmetic']:
				awarded_coins = int(AWARDS[kind]['price'] * COSMETIC_AWARD_COIN_AWARD_PCT) * not_from_lootbox_quantity
			else:
				awarded_coins = 0

			if awarded_coins:
				if kind == 'shit':
					author.charge_account('coins', awarded_coins, f"{quantity} Shit award{s} on {obj.textlink}", should_check_balance=False)
					v.pay_account('coins', awarded_coins, f"{quantity} Shit award{s} on {obj.textlink}")
				else:
					author.pay_account('coins', awarded_coins, f"{quantity} {award_title} award{s} on {obj.textlink}")

	can_alter_body = not obj.author.deflector or v == obj.author

	for award in awards:
		if isinstance(obj, Post): award.post_id = obj.id
		else: award.comment_id = obj.id
		award.awarded_utc = int(time.time())
		award.note = note
		g.db.add(award)

	if kind in {"ban", "grass"}:
		if author.is_suspended and author.ban_reason.startswith('Grass award used by @'):
			stop(400, f"You can't give a {kind} award to an already-grassed user!")

		ban_reason_link = f"/{thing_type}/{obj.id}"
		if isinstance(obj, Comment):
			ban_reason_link += '#context'
		ban_reason = f'{award_title} award{s} used by @{v.username} on <a href="{ban_reason_link}">{ban_reason_link}</a>'
		author.ban_reason = ban_reason


	if kind == "pause":
		if author.has_badge(68):
			stop(409, f"@{obj.author_name} already has this profile upgrade!")
		badge_grant(badge_id=68, user=author)
	elif kind == "unpausable":
		if author.has_badge(67):
			stop(409, f"@{obj.author_name} already has this profile upgrade!")
		badge_grant(badge_id=67, user=author)
	elif kind == "eye":
		if author.has_badge(83):
			stop(409, f"@{obj.author_name} already has this profile upgrade!")
		badge_grant(badge_id=83, user=author)
	elif kind == "offsitementions":
		if author.has_badge(140):
			stop(409, f"@{obj.author_name} already has this profile upgrade!")
		author.offsite_mentions = True
		badge_grant(user=author, badge_id=140)
	elif kind == "alt":
		if author.has_badge(84):
			stop(409, f"@{obj.author_name} already has this profile upgrade!")
		badge_grant(badge_id=84, user=author)
	elif kind == "unblockable":
		if author.has_badge(87):
			stop(409, f"@{obj.author_name} already has this profile upgrade!")
		badge_grant(badge_id=87, user=author)
		blocks = g.db.query(UserBlock).filter(
				or_(
					UserBlock.user_id == author.id,
					UserBlock.target_id == author.id,
				)
			)
		for block in blocks:
			g.db.delete(block)
	elif kind == "beano":
		if author.has_badge(128):
			stop(409, f"@{obj.author_name} already has this profile upgrade!")
		badge_grant(user=author, badge_id=128)
	elif kind == "checkmark":
		if author.has_badge(150):
			stop(409, f"@{obj.author_name} already has this profile upgrade!")
		author.verified = "Verified"
		badge_grant(user=author, badge_id=150)
	elif kind == "pride":
		if author.has_badge(303):
			stop(409, f"@{obj.author_name} already has this profile upgrade!")
		badge_grant(user=author, badge_id=303)
	elif kind == "grinch":
		if author.grinch:
			stop(409, f"@{obj.author_name} already has this profile upgrade!")
		author.grinch = True
		if v.id == author.id:
			session['event_music'] = False
	elif kind == "emoji":
		emoji_behavior = request.values.get("emoji_behavior").strip()

		for award in awards:
			award.note = award.note.strip(":").lower()
			if emoji_behavior == "horizontal":
				award.kind = "emoji-hz"

		emoji = g.db.query(Emoji).filter_by(name=award.note).one_or_none()
		if not emoji:
			stop(404, f'an Emoji with the name "{award.note}" was not found!')
	elif kind == "ban":
		if author.is_permabanned:
			stop(400, f"{safe_username} already permabanned!")
		author.ban(reason=ban_reason, days=quantity, modlog=False)
		send_repeatable_notification(author.id, f"Your account has been banned for **{quantity} day{s}** for {obj.textlink}. It sucked and you should feel bad.")
	elif kind == "unban":
		if not author.is_suspended or not author.unban_utc:
			stop(403)

		if not author.ban_reason.startswith('Ban award'):
			stop(400, "You can only use unban awards to undo the effect of ban awards!")

		if author.unban_utc - time.time() > 86400 * quantity:
			author.unban_utc -= 86400 * quantity
			send_repeatable_notification(author.id, f"Your ban duration has been reduced by {quantity} day{s}!")
		else:
			author.unban_utc = None
			author.is_banned = None
			author.ban_reason = None
			send_repeatable_notification(author.id, "You have been unbanned!")
	elif kind == "grass":
		new_unban_utc = int(time.time()) + 30 * 86400 * quantity
		if author.is_banned and (not author.unban_utc or author.unban_utc > new_unban_utc):
			stop(403, f"{safe_username} already banned for more than 30 days!")

		author.ban(reason=ban_reason, days=30, modlog=False)
		send_repeatable_notification(author.id, f"@{v.username} gave you {quantity} grass award{s} on {obj.textlink} and as a result you have been banned! You must [send the admins](/contact) a timestamped picture of you touching grass/snow/sand/ass to get unbanned!")
	elif kind == "hieroglyphs":
		if author.hieroglyphs: author.hieroglyphs += 86400 * quantity
		else: author.hieroglyphs = int(time.time()) + 86400 * quantity
		badge_grant(user=author, badge_id=98)
	elif kind == "progressivestack":
		if not FEATURES['PINS']:
			stop(403)

		if author.progressivestack != 1:
			if author.progressivestack: author.progressivestack += 21600 * quantity
			else: author.progressivestack = int(time.time()) + 21600 * quantity
			badge_grant(user=author, badge_id=94)
	elif kind == "benefactor":
		if not author.patron:
			author.patron = 1
		if author.patron_utc: author.patron_utc += 2629746 * quantity
		else: author.patron_utc = int(time.time()) + 2629746 * quantity
		author.pay_account('marseybux', 1250 * quantity, f"Benefactor award on {obj.textlink}")
		badge_grant(user=v, badge_id=103)
	elif kind == "rehab":
		if author.rehab: author.rehab += 86400 * quantity
		else: author.rehab = int(time.time()) + 86400 * quantity
		badge_grant(user=author, badge_id=109)
	elif kind == "deflector":
		if author.id in IMMUNE_TO_NEGATIVE_AWARDS:
			stop(400, f"{safe_username} immune to negative awards!")
		if author.deflector: author.deflector += 36000 * quantity
		else: author.deflector = int(time.time()) + 36000 * quantity
	elif kind == 'marsify':
		if not author.marsify or author.marsify != 1:
			if author.marsify: author.marsify += 86400 * quantity
			else: author.marsify = int(time.time()) + 86400 * quantity
		badge_grant(user=author, badge_id=170)

		if can_alter_body:
			alter_body(obj)
	elif kind == "bite":
		if author.bite: author.bite += 86400 * quantity
		else:
			if author.house.startswith("Vampire"):
				stop(400, f"{safe_username} already a permanent vampire!")

			author.bite = int(time.time()) + 86400 * quantity
			author.old_house = author.house
			author.house = "Vampire"

		badge_grant(user=author, badge_id=168)
	elif kind == "earlylife":
		if author.earlylife: author.earlylife += 21600 * quantity
		else: author.earlylife = int(time.time()) + 21600 * quantity
		badge_grant(user=author, badge_id=169)
	elif kind == "owoify":
		if author.owoify: author.owoify += 21600 * quantity
		else: author.owoify = int(time.time()) + 21600 * quantity
		badge_grant(user=author, badge_id=167)

		if can_alter_body:
			alter_body(obj)
	elif kind == "sharpen":
		if author.sharpen: author.sharpen += 86400 * quantity
		else: author.sharpen = int(time.time()) + 86400 * quantity
		badge_grant(user=author, badge_id=289)

		if can_alter_body:
			obj.sharpened = True
			alter_body(obj)
	elif kind == "rainbow":
		if author.rainbow: author.rainbow += 86400 * quantity
		else: author.rainbow = int(time.time()) + 86400 * quantity
		badge_grant(user=author, badge_id=171)
		if can_alter_body:
			obj.rainbowed = True
	elif kind == "gold":
		if obj.award_count('glowie', v):
			stop(409, f"This {thing_type} is under the effect of a conflicting award: Glowie award!")
	elif kind == "glowie":
		if obj.award_count('gold', v):
			stop(409, f"This {thing_type} is under the effect of a conflicting award: Gold award!")
	elif kind == "spider":
		if author.spider: author.spider += 86400 * quantity
		else: author.spider = int(time.time()) + 86400 * quantity
		badge_grant(user=author, badge_id=179, notify=False)
	elif kind in {"pin", "gigapin"}:
		if not FEATURES['PINS']: stop(403)
		if obj.is_banned: stop(403)

		if obj.pinned and not obj.pinned_utc:
			stop(400, f"This {thing_type} is already pinned permanently!")

		if SITE_NAME == 'WPD' and isinstance(obj, Comment) and not obj.parent_post:
			stop(400, "You can't pin wall comments!")

		if isinstance(obj, Comment): add = 3600*6 * quantity
		else: add = 3600 * quantity

		if kind == "gigapin":
			add *= 12

		if obj.pinned_utc:
			obj.pinned_utc += add
		else:
			obj.pinned_utc = int(time.time()) + add
			if isinstance(obj, Comment):
				obj.pin_parents()

		obj.pinned = f'{v.username}{PIN_AWARD_TEXT}'

		if isinstance(obj, Post):
			cache.delete_memoized(frontlist)
	elif kind == "unpin":
		if not obj.pinned_utc: stop(400)
		if not obj.author.deflector or v == obj.author:
			if isinstance(obj, Comment):
				t = obj.pinned_utc - 3600*6 * quantity
			else:
				t = obj.pinned_utc - 3600 * quantity

			if time.time() > t:
				obj.pinned = None
				obj.pinned_utc = None
				if isinstance(obj, Post):
					cache.delete_memoized(frontlist)
				else:
					obj.unpin_parents()	
			else: obj.pinned_utc = t
	elif kind == "queen":
		if not author.queen:
			characters = list(filter(str.isalpha, author.username))
			if characters:
				first_character = characters[0].upper()
			else:
				first_character = random.choice(string.ascii_letters).upper()

			available_names = GIRL_NAMES[first_character]
			random.shuffle(available_names)

			broken = False
			for new_name in available_names:
				existing = get_user(new_name, graceful=True)
				if not existing:
					broken = True
					break

			if not broken:
				new_name = new_name + f'-{author.id}'

			if not author.prelock_username:
				author.prelock_username = author.username
			author.username = new_name

		if author.queen and time.time() < author.queen: author.queen += 86400 * quantity
		else: author.queen = int(time.time()) + 86400 * quantity

		author.namechanged = author.queen

		badge_grant(user=author, badge_id=285)

		if can_alter_body:
			obj.queened = True
			alter_body(obj)
	elif kind == "chud":
		if isinstance(obj, Post) and obj.hole == 'chudrama' \
			or isinstance(obj, Comment) and obj.post and obj.post.hole == 'chudrama':
			stop(403, "You can't give the chud award in /h/chudrama")

		if author.chud == 1:
			stop(409, f"{safe_username} already permanently chudded!")

		if author.chud and time.time() < author.chud: author.chud += 86400 * quantity
		else: author.chud = int(time.time()) + 86400 * quantity

		if not note: stop(400, "Missing phrase!")

		if note not in CHUD_PHRASES:
			stop(400, "Invalid phrase!")

		author.chud_phrase = note

		badge_grant(user=author, badge_id=58)

		if can_alter_body:
			obj.chudded = True
			complies_with_chud(obj)
	elif kind == "flairlock":
		new_flair = note

		if len(new_flair) > 100:
			stop(400, "New flair is too long (max 100 characters)")

		if not new_flair and author.flairchanged:
			author.flairchanged += 86400 * quantity
		else:
			author.flair = new_flair
			new_flair = filter_emojis_only(new_flair, link=True)
			new_flair = censor_slurs_profanities(new_flair, None)
			if len(new_flair) > 1000: stop(403)
			author.flair_html = new_flair
			author.flairchanged = int(time.time()) + 86400 * quantity
			badge_grant(user=author, badge_id=96)
	elif kind == "namelock":
		new_name = note.strip().lstrip('@').strip()
		if author.namechanged and (not new_name or new_name == author.username):
			author.namechanged += 86400 * quantity
		else:
			if not valid_username_regex.fullmatch(new_name):
				stop(400, "You need to enter a valid username to change the recipient to.")

			if not execute_blackjack(v, None, new_name, f'namelock award attempt on @{author.username}'):
				existing = get_user(new_name, graceful=True)
				if existing and existing.id != author.id:
					stop(400, f"@{new_name} is already taken!")

				if not author.prelock_username:
					author.prelock_username = author.username
				author.username = new_name
				author.namechanged = int(time.time()) + 86400 * quantity
				badge_grant(user=author, badge_id=281)
	elif kind == "pizzashill":
		if author.bird:
			author.bird = 0
			badge = author.has_badge(95)
			if badge: g.db.delete(badge)
		else:
			if author.longpost: author.longpost += 86400 * quantity
			else: author.longpost = int(time.time()) + 86400 * quantity
			badge_grant(user=author, badge_id=97)
	elif kind == "bird":
		if author.longpost:
			author.longpost = 0
			badge = author.has_badge(97)
			if badge: g.db.delete(badge)
		else:
			if author.bird: author.bird += 86400 * quantity
			else: author.bird = int(time.time()) + 86400 * quantity
			badge_grant(user=author, badge_id=95)
	elif kind == "jumpscare":
		author.jumpscare += 1 * quantity
	elif kind == "vax":
		if v.zombie < 0:
			stop(403, "Zombies can't vaccinate others!")
		for award in awards:
			g.db.flush()
			if author.zombie < 0:
				author.zombie = 0
				send_repeatable_notification(author.id, "You are no longer **INFECTED**! Praise Fauci!")

				badge = author.has_badge(181)
				if badge: g.db.delete(badge)
			elif author.zombie >= 0:
				author.zombie += 2
				author.zombie = min(author.zombie, 10)

				badge_grant(user=author, badge_id=182)
	elif kind == "zombiebite":
		if v.zombie >= 0:
			stop(403, "Only zombies can bite others!")
		for award in awards:
			g.db.flush()
			if author.zombie < 0:
				author = v

			if author.zombie == 0:
				author.zombie = -1
				badge_grant(user=author, badge_id=181)

				award_object = AwardRelationship(user_id=author.id, kind='zombiebite')
				g.db.add(award_object)
				send_repeatable_notification(author.id,
					"As the zombie virus washes over your mind, you feel the urge "
					"to… BITE YUMMY BRAINS :marseyzombie:<br>"
					"You receive a free **Zombie Bite** award: pass it on!")

			elif author.zombie > 0:
				author.zombie -= 1
				if author.zombie == 0:
					send_repeatable_notification(author.id, "You are no longer **VAXXMAXXED**! Time for another booster!")

					badge = author.has_badge(182)
					if badge: g.db.delete(badge)


	author = obj.author
	if v.id != author.id:
		if author.deflector and AWARDS[kind]['deflectable'] and v.admin_level < PERMS['IMMUNE_TO_DEFLECTIONS']:
			msg = f"@{v.username} has tried to give {obj.textlink} {quantity} {award_title} award{s} but {it} {was} deflected and applied to them :marseytroll:"
			n = send_repeatable_notification(author.id, msg)
			if n: n.created_utc -= 2

			msg = f"@{obj.author_name} is under the effect of a deflector award; your {award_title} award{s} {has} been deflected back to you :marseytroll:"
			n = send_repeatable_notification(v.id, msg)
			if n: n.created_utc -= 2
		elif kind not in {'spider', 'jumpscare'}:
			msg = f"@{v.username} has given {obj.textlink} {quantity} {award_title} award{s}"

			if kind == 'shit':
				msg += f" and has stolen from you {awarded_coins} coins as a result"
			elif awarded_coins:
				msg += f" and you have received {awarded_coins} coins as a result"

			msg += "!"
			if kind == 'emoji':
				msg += f"\n\n> :{award.note}:"
			elif note:
				note = '\n\n> '.join(note.splitlines())
				if kind == "chud":
					msg += f"\n\n**You now have to say this phrase in all posts and comments you make for {24*quantity} hours:**"
				msg += f"\n\n`{note}`"
				if SITE_NAME == 'rDrama' and kind == "chud":
					msg += f"\n\nPlease keep your chud behavior to /h/chudrama in the future!"
			n = send_repeatable_notification(author.id, msg)
			if n: n.created_utc -= 2

	if author.received_award_count: author.received_award_count += quantity
	else: author.received_award_count = quantity
	g.db.add(author)

	g.db.add(obj)

	return {"message": f"{quantity} {award_title} award{s} given to {thing_type} successfully!"}

@app.post("/trick_or_treat")
@limiter.limit("1/hour", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("1/hour", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def trick_or_treat(v):
	if v.client:
		stop(403, "Not allowed from the API")
	if not IS_HOMOWEEN():
		stop(403)

	result = random.choice([0,1])

	if result == 0:
		message = "Trick!"
	else:
		choices = [x["kind"] for x in AWARDS_ENABLED(v).values() if x["included_in_lootbox"]]
		award = random.choice(choices)
		award_object = AwardRelationship(user_id=v.id, kind=award)
		g.db.add(award_object)

		award_title = AWARDS_ENABLED(v)[award]['title']
		message = f"Treat! You got a {award_title} award!"

	return {"message": f"{message}", "result": f"{result}"}


@app.post("/jumpscare")
@auth_required
def execute_jumpscare(v):
	if v.client:
		stop(403, "Not allowed from the API")
	if not IS_HOMOWEEN():
		stop(403)

	if v.jumpscare > 0:
		v.jumpscare -= 1
		g.db.add(v)

	return {}
