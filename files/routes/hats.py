from sqlalchemy import func

from files.classes.hats import *
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.useractions import *
from files.routes.wrappers import *
from files.__main__ import app, limiter

@app.get("/shop/hats")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def hats(v):
	owned_hat_ids = [x.hat_id for x in v.owned_hats]

	if v.equipped_hat_ids:
		equipped = g.db.query(HatDef, User).join(HatDef.author).filter(HatDef.submitter_id == None, HatDef.id.in_(owned_hat_ids), HatDef.id.in_(v.equipped_hat_ids)).order_by(HatDef.price, HatDef.name).all()
		not_equipped = g.db.query(HatDef, User).join(HatDef.author).filter(HatDef.submitter_id == None, HatDef.id.in_(owned_hat_ids), HatDef.id.notin_(v.equipped_hat_ids)).order_by(HatDef.price, HatDef.name).all()
		owned = equipped + not_equipped
	else:
		owned = g.db.query(HatDef, User).join(HatDef.author).filter(HatDef.submitter_id == None, HatDef.id.in_(owned_hat_ids)).order_by(HatDef.price, HatDef.name).all()

	not_owned = g.db.query(HatDef, User).join(HatDef.author).filter(HatDef.submitter_id == None, HatDef.id.notin_(owned_hat_ids)).order_by(HatDef.price == 0, HatDef.price, HatDef.name).all()
	hats = owned + not_owned

	sales = g.db.query(func.sum(User.coins_spent_on_hats)).scalar()
	num_of_hats = g.db.query(HatDef).filter(HatDef.submitter_id == None).count()
	return render_template("hats.html", owned_hat_ids=owned_hat_ids, hats=hats, v=v, sales=sales, num_of_hats=num_of_hats)

@app.post("/buy_hat/<int:hat_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit('100/minute;1000/3 days', deduct_when=lambda response: response.status_code < 400)
@limiter.limit('100/minute;1000/3 days', deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def buy_hat(v, hat_id):
	hat = g.db.query(HatDef).filter_by(submitter_id=None, id=hat_id).one_or_none()
	if not hat: abort(404, "Hat not found!")

	existing = g.db.query(Hat).filter_by(user_id=v.id, hat_id=hat.id).one_or_none()
	if existing: abort(409, "You already own this hat!")

	if not hat.is_purchasable:
		abort(403, "This hat is not for sale!")

	charged = v.charge_account('coins/marseybux', hat.price, f"<code>{hat.name}</code> hat cost")
	if not charged[0]:
		abort(400, "Not enough coins/marseybux!")

	v.coins_spent_on_hats += charged[1]
	hat.author.pay_account('coins', hat.price * 0.1, f"Royalties for <code>{hat.name}</code> hat")

	new_hat = Hat(user_id=v.id, hat_id=hat.id)
	g.db.add(new_hat)

	g.db.add(v)
	g.db.add(hat.author)

	send_repeatable_notification(
		hat.author.id,
		f":marseycapitalistmanlet: @{v.username} has just bought `{hat.name}`, you have received your 10% cut ({int(hat.price * 0.1)} coins) :!marseycapitalistmanlet:"
	)

	if v.num_of_owned_hats >= 249:
		badge_grant(user=v, badge_id=154)
	elif v.num_of_owned_hats >= 99:
		badge_grant(user=v, badge_id=153)
	elif v.num_of_owned_hats >= 24:
		badge_grant(user=v, badge_id=152)

	return {"message": f"'{hat.name}' bought!"}


@app.post("/equip_hat/<int:hat_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def equip_hat(v, hat_id):
	hat = g.db.query(Hat).filter_by(hat_id=hat_id, user_id=v.id).one_or_none()
	if not hat: abort(403, "You don't own this hat!")

	hat.equipped = True
	g.db.add(hat)

	return {"message": f"'{hat.name}' equipped!"}

@app.post("/unequip_hat/<int:hat_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def unequip_hat(v, hat_id):
	hat = g.db.query(Hat).filter_by(hat_id=hat_id, user_id=v.id).one_or_none()
	if not hat: abort(403, "You don't own this hat!")

	hat.equipped = False
	g.db.add(hat)

	return {"message": f"'{hat.name}' unequipped!"}

@app.get("/hat_owners/<int:hat_id>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def hat_owners(v, hat_id):
	name = g.db.query(HatDef.name).filter_by(id=hat_id).one()[0]

	href = f'{SITE_FULL_IMAGES}/i/hats/{name}.webp?x=8'

	page = get_page()

	users = g.db.query(User, Hat.created_utc).join(Hat.owners).filter(Hat.hat_id == hat_id)

	total = users.count()

	users = users.order_by(Hat.created_utc.desc()).offset(PAGE_SIZE * (page - 1)).limit(PAGE_SIZE).all()

	return render_template("owners.html", v=v, users=users, page=page, total=total, kind="Hat", name=name, href=href)
