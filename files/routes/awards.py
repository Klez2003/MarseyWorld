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
	AWARDS = deepcopy(AWARDS_ENABLED)

	if v.house:
		AWARDS[v.house] = deepcopy(HOUSE_AWARDS[v.house])

	for val in AWARDS.values(): val["owned"] = 0

	for useraward in g.db.query(AwardRelationship).filter(AwardRelationship.user_id == v.id, AwardRelationship.post_id == None, AwardRelationship.comment_id == None):
		if useraward.kind in AWARDS: AWARDS[useraward.kind]["owned"] += 1

	for val in AWARDS.values():
		val["baseprice"] = int(val["price"])
		if val["kind"].endswith('Founder'):
			val["baseprice"] = int(val["baseprice"] / 0.75)
		val["price"] = int(val["price"] * v.award_discount)

	sales = g.db.query(func.sum(User.coins_spent)).scalar()
	return render_template("shop.html", awards=list(AWARDS.values()), v=v, sales=sales)


def buy_award(v, kind, AWARDS):
	og_price = AWARDS[kind]["price"]
	price = int(og_price * v.award_discount)

	if kind == "grass":
		currency = 'coins'
	elif kind == "benefactor":
		currency = 'marseybux'
	else:
		currency = 'combined'

	charged = v.charge_account(currency, price)
	if not charged[0]:
		abort(400, "Not enough coins/marseybux!")

	v.coins_spent += charged[1]
	if v.coins_spent >= 1000000:
		badge_grant(badge_id=73, user=v)
	elif v.coins_spent >= 500000:
		badge_grant(badge_id=72, user=v)
	elif v.coins_spent >= 250000:
		badge_grant(badge_id=71, user=v)
	elif v.coins_spent >= 100000:
		badge_grant(badge_id=70, user=v)
	elif v.coins_spent >= 10000:
		badge_grant(badge_id=69, user=v)
	g.db.add(v)

	if kind == "lootbox":
		lootbox_items = []
		for _ in range(LOOTBOX_ITEM_COUNT): # five items per lootbox
			LOOTBOX_CONTENTS = [x["kind"] for x in AWARDS_ENABLED.values() if x["included_in_lootbox"]]
			lb_award = random.choice(LOOTBOX_CONTENTS)
			lootbox_items.append(AWARDS[lb_award]['title'])
			lb_award = AwardRelationship(user_id=v.id, kind=lb_award, price_paid=price // LOOTBOX_ITEM_COUNT)
			g.db.add(lb_award)

		v.lootboxes_bought += 1
		lootbox_msg = "You open your lootbox and receive: " + ', '.join(lootbox_items)
		send_repeatable_notification(v.id, lootbox_msg)

		if v.lootboxes_bought == 10:
			badge_grant(badge_id=76, user=v)
		elif v.lootboxes_bought == 50:
			badge_grant(badge_id=77, user=v)
		elif v.lootboxes_bought == 150:
			badge_grant(badge_id=78, user=v)

		return {"message": lootbox_msg}
	else:
		award_object = AwardRelationship(user_id=v.id, kind=kind, price_paid=price)
		g.db.add(award_object)

	g.db.add(v)

	if CARP_ID and v.id != CARP_ID and og_price >= 5000:
		award_title = AWARDS[kind]['title']
		send_repeatable_notification(CARP_ID, f"@{v.username} has bought a `{award_title}` award!")

	return award_object


@app.post("/buy/<kind>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("100/minute;200/hour;1000/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("100/minute;200/hour;1000/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def buy(v, kind):
	AWARDS = deepcopy(AWARDS_ENABLED)

	if v.house:
		AWARDS[v.house] = HOUSE_AWARDS[v.house]

	if kind not in AWARDS: abort(400)

	award_title = AWARDS[kind]['title']

	award = buy_award(v, kind, AWARDS)

	if isinstance(award, dict):
		return award

	return {"message": f"{award_title} award bought!"}

def alter_body(thing):
	thing.body_html = sanitize(thing.body, limit_pings=5, showmore=True, obj=thing, author=thing.author)
	if isinstance(thing, Post):
		thing.title_html = filter_emojis_only(thing.title, golden=False, obj=thing, author=thing.author)

@app.post("/award/<thing_type>/<int:id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def award_thing(v, thing_type, id):
	kind = request.values.get("kind", "").strip()

	if thing_type == 'post':
		thing = get_post(id)
	elif thing_type == 'comment':
		thing = get_comment(id)
		if not thing.parent_post and not thing.wall_user_id: abort(404) # don't let users award messages
	else:
		abort(400)

	author = thing.author

	AWARDS = deepcopy(AWARDS_ENABLED)
	if v.house:
		AWARDS[v.house] = HOUSE_AWARDS[v.house]

	if kind not in AWARDS: abort(404, "This award doesn't exist")

	award_title = AWARDS[kind]['title']

	award = g.db.query(AwardRelationship).filter(
		AwardRelationship.kind == kind,
		AwardRelationship.user_id == v.id,
		AwardRelationship.post_id == None,
		AwardRelationship.comment_id == None
	).first()

	if not award: 
		award = buy_award(v, kind, AWARDS)
		if isinstance(award, dict):
			return award

	if thing_type == 'post': award.post_id = thing.id
	else: award.comment_id = thing.id
	award.awarded_utc = int(time.time())

	g.db.add(award)

	note = request.values.get("note", "").strip()[:200]
	award.note = note

	safe_username = f"@{thing.author_name} is"

	if AWARDS[kind]['negative'] and author.immune_to_negative_awards(v):
		abort(403, f"{safe_username} immune to negative awards!")

	if thing_type == 'post' and thing.id == 210983:
		abort(403, "You can't award this post!")

	if thing_type == 'post' and thing.distinguish_level and AWARDS[kind]['cosmetic']:
		abort(403, "Distinguished posts are immune to cosmetic awards!")

	if kind == "benefactor":
		if author.id == v.id:
			abort(403, "You can't use this award on yourself!")
		if author.id in get_alt_graph_ids(v.id):
			abort(403, "You can't use this award on your alts!")

	if thing.ghost and not AWARDS[kind]['ghost']:
		abort(403, "This kind of award can't be used on ghost posts!")

	if v.id != author.id:
		if author.deflector and v.deflector and AWARDS[kind]['deflectable']:
			msg = f"@{v.username} has tried to give your [{thing_type}]({thing.shortlink}) the {award_title} Award but it was deflected on them, they also had a deflector up, so it bounced back and forth until it vaporized!"
			send_repeatable_notification(author.id, msg)

			msg = f"{safe_username} under the effect of a deflector award; your {award_title} Award has been deflected back to you but your deflector protected you, the award bounced back and forth until it vaporized!"
			send_repeatable_notification(v.id, msg)

			g.db.delete(award)

			return {"message": f"{award_title} award given to {thing_type} successfully!"}

		if author.deflector and AWARDS[kind]['deflectable']:
			author = v
			safe_username = f"Your award has been deflected but failed since you're"

			if kind == 'shit':
				awarded_coins = int(AWARDS[kind]['price'] * COSMETIC_AWARD_COIN_AWARD_PCT)
				v.charge_account('coins', awarded_coins, should_check_balance=False)
				thing.author.pay_account('coins', awarded_coins)
		elif kind != 'spider':
			if AWARDS[kind]['cosmetic'] and not AWARDS[kind]['included_in_lootbox']:
				awarded_coins = int(AWARDS[kind]['price'] * COSMETIC_AWARD_COIN_AWARD_PCT)
			else:
				awarded_coins = 0

			if awarded_coins:
				if kind == 'shit':
					author.charge_account('coins', awarded_coins, should_check_balance=False)
					v.pay_account('coins', awarded_coins)
				else:
					author.pay_account('coins', awarded_coins)

			if thing_type == 'comment':
				link_text_in_notif = "your comment"
			else:
				link_text_in_notif = thing.title

	if kind == 'marsify' and author.marsify == 1:
		abort(409, f"{safe_username} already permanently marsified!")

	if kind == 'spider' and author.spider == 1:
		abort(409, f"{safe_username} already best friends with a spider!")

	link = f"[this {thing_type}]({thing.shortlink})"

	can_alter_body = not thing.is_effortpost and (not thing.author.deflector or v == thing.author)

	if kind == "ban":
		link = f"/{thing_type}/{thing.id}"
		if thing_type == 'comment':
			link += '#context'
			link_text_in_notif = link
		else:
			link_text_in_notif = thing.title

		ban_reason = f'1-Day ban award used by <a href="/@{v.username}">@{v.username}</a> on <a href="{link}">{link}</a>'
		if not author.is_suspended:
			author.ban(reason=ban_reason, days=1)
			send_repeatable_notification(author.id, f"Your account has been banned for **a day** for [{link_text_in_notif}]({link}). It sucked and you should feel bad.")
		elif author.unban_utc:
			author.unban_utc += 86400
			author.ban_reason = ban_reason
			send_repeatable_notification(author.id, f"Your account has been banned for **yet another day** for [{link_text_in_notif}]({link}). Seriously man?")
	elif kind == "unban":
		if not author.is_suspended or not author.unban_utc:
			abort(403)

		if not author.ban_reason.startswith('1-Day ban award'):
			abort(400, "You can only use unban awards to undo the effect of ban awards!")

		if author.unban_utc - time.time() > 86400:
			author.unban_utc -= 86400
			send_repeatable_notification(author.id, "Your ban duration has been reduced by 1 day!")
		else:
			author.unban_utc = 0
			author.is_banned = None
			if not author.shadowbanned:
				author.ban_reason = None
			send_repeatable_notification(author.id, "You have been unbanned!")
	elif kind == "grass":
		link3 = f"/{thing_type}/{thing.id}"
		if thing_type == 'comment':
			link3 = f'<a href="{link3}#context">{link3}</a>'
		else:
			link3 = f'<a href="{link3}">{link3}</a>'

		author.is_banned = AUTOJANNY_ID
		author.ban_reason = f"grass award used by @{v.username} on {link3}"
		author.unban_utc = int(time.time()) + 30 * 86400
		send_repeatable_notification(author.id, f"@{v.username} gave you the grass award on {link} and as a result you have been banned! You must [send the admins](/contact) a timestamped picture of you touching grass/snow/sand/ass to get unbanned!")
	elif kind == "pin":
		if not FEATURES['PINS']: abort(403)
		if thing.is_banned: abort(403)

		if thing.stickied and not thing.stickied_utc:
			abort(400, f"This {thing_type} is already pinned permanently!")

		if thing_type == 'comment': add = 3600*6
		else: add = 3600

		if thing.stickied_utc:
			thing.stickied_utc += add
		else:
			thing.stickied_utc = int(time.time()) + add

		thing.stickied = f'{v.username}{PIN_AWARD_TEXT}'
		cache.delete_memoized(frontlist)
	elif kind == "unpin":
		if not thing.stickied_utc: abort(400)
		if not thing.author.deflector or v == thing.author:
			if thing.author_id == LAWLZ_ID and SITE_NAME == 'rDrama': abort(403, "You can't unpin lawlzposts!")

			if thing_type == 'comment':
				t = thing.stickied_utc - 3600*6
			else:
				t = thing.stickied_utc - 3600

			if time.time() > t:
				thing.stickied = None
				thing.stickied_utc = None
				cache.delete_memoized(frontlist)
			else: thing.stickied_utc = t
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

		if author.queen and time.time() < author.queen: author.queen += 86400
		else: author.queen = int(time.time()) + 86400

		author.namechanged = author.queen

		badge_grant(user=author, badge_id=285)

		if can_alter_body:
			thing.queened = True
			alter_body(thing)
	elif kind == "chud":
		if thing_type == 'post' and thing.hole == 'chudrama' \
			or thing_type == 'comment' and thing.post and thing.post.hole == 'chudrama':
			abort(403, "You can't give the chud award in /h/chudrama")

		if author.chud == 1:
			abort(409, f"{safe_username} already permanently chudded!")

		if author.chud and time.time() < author.chud: author.chud += 86400
		else: author.chud = int(time.time()) + 86400

		if not note: abort(400, "Missing phrase!")

		if note not in CHUD_PHRASES:
			abort(400, "Invalid phrase!")

		author.chud_phrase = note.lower()

		badge_grant(user=author, badge_id=58)

		if can_alter_body:
			thing.chudded = True
			complies_with_chud(thing)
	elif kind == "flairlock":
		new_name = note[:100]
		if not new_name and author.flairchanged:
			author.flairchanged += 86400
		else:
			author.flair = new_name
			new_name = filter_emojis_only(new_name)
			new_name = censor_slurs_profanities(new_name, None)
			if len(new_name) > 1000: abort(403)
			author.flair_html = new_name
			author.flairchanged = int(time.time()) + 86400
			badge_grant(user=author, badge_id=96)
	elif kind == "namelock":
		new_name = note.strip().lstrip('@')
		if author.namechanged and (not new_name or new_name == author.username):
			author.namechanged += 86400
		else:
			if not valid_username_regex.fullmatch(new_name):
				abort(400, "You need to enter a valid username to change the recipient to.")

			if not execute_blackjack(v, None, new_name, f'namelock award attempt on @{author.username}'):
				existing = get_user(new_name, graceful=True)
				if existing and existing.id != author.id:
					abort(400, f"@{new_name} is already taken!")

				if not author.prelock_username:
					author.prelock_username = author.username
				author.username = new_name
				author.namechanged = int(time.time()) + 86400
				badge_grant(user=author, badge_id=281)
	elif kind == "pause":
		badge_grant(badge_id=68, user=author)
	elif kind == "unpausable":
		badge_grant(badge_id=67, user=author)
	elif kind == "hieroglyphs":
		if author.hieroglyphs: author.hieroglyphs += 86400
		else: author.hieroglyphs = int(time.time()) + 86400
		badge_grant(user=author, badge_id=98)
	elif kind == "pizzashill":
		if author.bird:
			author.bird = 0
			badge = author.has_badge(95)
			if badge: g.db.delete(badge)
		else:
			if author.longpost: author.longpost += 86400
			else: author.longpost = int(time.time()) + 86400
			badge_grant(user=author, badge_id=97)
	elif kind == "bird":
		if author.longpost:
			author.longpost = 0
			badge = author.has_badge(97)
			if badge: g.db.delete(badge)
		else:
			if author.bird: author.bird += 86400
			else: author.bird = int(time.time()) + 86400
			badge_grant(user=author, badge_id=95)
	elif kind == "eye":
		badge_grant(badge_id=83, user=author)
	elif kind == "offsitementions":
		badge_grant(user=author, badge_id=140)
	elif kind == "alt":
		badge_grant(badge_id=84, user=author)
	elif kind == "unblockable":
		badge_grant(badge_id=87, user=author)
		for block in g.db.query(UserBlock).filter_by(target_id=author.id): g.db.delete(block)
	elif kind == "progressivestack":
		if not FEATURES['PINS']:
			abort(403)

		if author.progressivestack != 1:
			if author.progressivestack: author.progressivestack += 21600
			else: author.progressivestack = int(time.time()) + 21600
			badge_grant(user=author, badge_id=94)
	elif kind == "benefactor":
		if not author.patron:
			author.patron = 1
		if author.patron_utc: author.patron_utc += 2629746
		else: author.patron_utc = int(time.time()) + 2629746
		author.pay_account('marseybux', 1250)
		badge_grant(user=v, badge_id=103)
	elif kind == "rehab":
		if author.rehab: author.rehab += 86400
		else: author.rehab = int(time.time()) + 86400
		badge_grant(user=author, badge_id=109)
	elif kind == "deflector":
		if author.deflector: author.deflector += 36000
		else: author.deflector = int(time.time()) + 36000
	elif kind == "beano":
		badge_grant(user=author, badge_id=128)
	elif kind == "checkmark":
		author.verified = "Verified"
		badge_grant(user=author, badge_id=150)
	elif kind == "pride":
		badge_grant(user=author, badge_id=303)
	elif kind == 'marsify':
		if not author.marsify or author.marsify != 1:
			if author.marsify: author.marsify += 86400
			else: author.marsify = int(time.time()) + 86400
		badge_grant(user=author, badge_id=170)

		if can_alter_body:
			alter_body(thing)
	elif "Vampire" in kind and kind == v.house:
		if author.bite: author.bite += 172800
		else:
			if author.house.startswith("Vampire"):
				abort(400, f"{safe_username} already a permanent vampire!")

			author.bite = int(time.time()) + 172800
			author.old_house = author.house
			author.house = "Vampire"

		badge_grant(user=author, badge_id=168)
	elif "Racist" in kind and kind == v.house:
		if author.earlylife: author.earlylife += 86400
		else: author.earlylife = int(time.time()) + 86400
		badge_grant(user=author, badge_id=169)
	elif ("Furry" in kind and kind == v.house) or kind == 'owoify':
		if author.owoify: author.owoify += 21600
		else: author.owoify = int(time.time()) + 21600
		badge_grant(user=author, badge_id=167)

		if can_alter_body:
			alter_body(thing)
	elif ("Edgy" in kind and kind == v.house) or kind == 'sharpen':
		if author.sharpen: author.sharpen += 86400
		else: author.sharpen = int(time.time()) + 86400
		badge_grant(user=author, badge_id=289)

		if can_alter_body:
			thing.sharpened = True
			alter_body(thing)
	elif ("Femboy" in kind and kind == v.house) or kind == 'rainbow':
		if author.rainbow: author.rainbow += 86400
		else: author.rainbow = int(time.time()) + 86400
		badge_grant(user=author, badge_id=171)
		if can_alter_body:
			thing.rainbowed = True
	elif kind == "emoji":
		award.note = award.note.strip(":").lower()
		emoji = g.db.query(Emoji).filter_by(name=award.note).one_or_none()
		if not emoji:
			abort(404, f'an Emoji with the name "{award.note}" was not found!')
	elif IS_FISTMAS():
		if kind == "grinch":
			badge_grant(badge_id=91, user=author)
			if v.id == author.id:
				session['event_music'] = False
		elif kind == "candycane":
			if thing.is_effortpost:
				abort(403, f'Effortposts are protected from the {award_title} award!')
	elif IS_HOMOWEEN():
		if kind == "hallowgrinch":
			badge_grant(badge_id=185, user=author)
			if v.id == author.id:
				session['event_music'] = False
		elif kind in {"ectoplasm", "candy-corn", "stab"}:
			if thing.is_effortpost:
				abort(403, f'Effortposts are protected from the {award_title} award!')
		elif kind == "spider":
			if author.spider: author.spider += 86400
			else: author.spider = int(time.time()) + 86400
			badge_grant(user=author, badge_id=179, notify=False)
		elif kind == "bite":
			if author.zombie < 0:
				author = v

			if author.zombie == 0:
				author.zombie = -1
				badge_grant(user=author, badge_id=181)

				award_object = AwardRelationship(user_id=author.id, kind='bite')
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
		elif kind == "vax":
			if author.zombie < 0:
				author.zombie = 0
				send_repeatable_notification(author.id, "You are no longer **INFECTED**! Praise Fauci!")

				badge = author.has_badge(181)
				if badge: g.db.delete(badge)
			elif author.zombie >= 0:
				author.zombie += 2
				author.zombie = min(author.zombie, 10)

				badge_grant(user=author, badge_id=182)
		elif kind == "jumpscare":
			author.jumpscare += 1

	author = thing.author
	if v.id != author.id:
		if author.deflector and AWARDS[kind]['deflectable']:
			msg = f"@{v.username} has tried to give your [{thing_type}]({thing.shortlink}) the {award_title} Award but it was deflected and applied to them :marseytroll:"
			n = send_repeatable_notification(author.id, msg)
			if n: n.created_utc -= 1

			msg = f"@{thing.author_name} is under the effect of a deflector award; your {award_title} Award has been deflected back to you :marseytroll:"
			n = send_repeatable_notification(v.id, msg)
			if n: n.created_utc -= 1
		elif kind not in {'spider', 'jumpscare'}:
			msg = f"@{v.username} has given [{link_text_in_notif}]({thing.shortlink}) the {award_title} Award"

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
					msg += f"\n\n**You now have to say this phrase in all posts and comments you make for 24 hours:**"
				msg += f"\n\n> {note}"
			n = send_repeatable_notification(author.id, msg)
			if n: n.created_utc -= 1

	if author.received_award_count: author.received_award_count += 1
	else: author.received_award_count = 1
	g.db.add(author)

	g.db.add(thing)

	if award.kind == "emoji":
		emoji_behavior = request.values.get("emoji_behavior").strip()
		if emoji_behavior == "horizontal":
			award.kind = "emoji-hz"

	return {"message": f"{award_title} award given to {thing_type} successfully!"}

@app.post("/trick-or-treat")
@limiter.limit("1/hour", key_func=lambda:f'{SITE}-{session.get("lo_user")}')
@auth_required
def trick_or_treat(v):
	if v.client:
		abort(403, "Not allowed from the API")
	if not IS_HOMOWEEN():
		abort(403)

	result = random.choice([0,1])

	if result == 0:
		message = "Trick!"
	else:
		choices = [x["kind"] for x in AWARDS_ENABLED.values() if x["included_in_lootbox"]]
		award = random.choice(choices)
		award_object = AwardRelationship(user_id=v.id, kind=award)
		g.db.add(award_object)

		award_title = AWARDS_ENABLED[award]['title']
		message = f"Treat! You got a {award_title} award!"

	return {"message": f"{message}", "result": f"{result}"}


@app.post("/jumpscare")
@auth_required
def execute_jumpscare(v):
	if v.client:
		abort(403, "Not allowed from the API")
	if not IS_HOMOWEEN():
		abort(403)

	if v.jumpscare > 0:
		v.jumpscare -= 1
		g.db.add(v)

	return {}
