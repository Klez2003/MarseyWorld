from files.routes.wrappers import *
from files.__main__ import app
from flask import request, g
from files.classes.push_subscriptions import PushSubscription

@app.post("/push_subscribe")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def push_subscribe(v):
	subscription_json = request.values.get("subscription_json")

	subscription = g.db.query(PushSubscription).filter_by(
		user_id=v.id,
		subscription_json=subscription_json,
	).one_or_none()

	if not subscription:
		subscription = PushSubscription(
			user_id=v.id,
			subscription_json=subscription_json,
		)
		g.db.add(subscription)

	return ''
