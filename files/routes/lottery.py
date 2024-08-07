from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.lottery import *
from files.routes.wrappers import *

from files.__main__ import app, limiter

@app.post("/lottery/buy")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("100/minute;500/hour;1000/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("100/minute;500/hour;1000/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def lottery_buy(v):
	try: quantity = int(request.values.get("quantity"))
	except: abort(400, "Invalid ticket quantity!")

	success, message = purchase_lottery_tickets(v, quantity)
	lottery, participants = get_active_lottery_stats()


	if success:
		return {"message": message, "stats": {"user": v.lottery_stats, "lottery": lottery, "participants": participants}}
	else:
		return {"error": message, "stats": {"user": v.lottery_stats, "lottery": lottery, "participants": participants}}


@app.get("/lottery/active")
@limiter.limit("100/minute;500/hour;1000/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("100/minute;500/hour;1000/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def lottery_active(v):
	lottery, participants = get_active_lottery_stats()

	return {"message": "", "stats": {"user": v.lottery_stats, "lottery": lottery, "participants": participants}}

@app.get("/admin/lottery/participants")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['LOTTERY_VIEW_PARTICIPANTS'])
def lottery_admin(v):
	participants = get_users_participating_in_lottery()
	return render_template("admin/lottery.html", v=v, participants=participants)
