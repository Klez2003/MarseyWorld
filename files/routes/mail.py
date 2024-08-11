import time

from files.classes import *
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.mail import *
from files.helpers.useractions import *
from files.routes.wrappers import *
from files.routes.users import claim_rewards_all_users
from files.__main__ import app, limiter

@app.post("/verify_email")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit('3/day', deduct_when=lambda response: response.status_code < 400)
@limiter.limit('3/day', deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def verify_email(v):
	if v.email_verified:
		stop(400, "Email already verified!")

	send_verification_email(v)
	return {"message": "Email has been sent. Please check your spam folder if you can't find it!"}


@app.get("/activate")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def activate(v):
	email = request.values.get("email", "").strip().lower()

	if not email_regex.fullmatch(email):
		stop(400, "Invalid email")

	id = request.values.get("id", "").strip()
	timestamp = int(request.values.get("time", "0"))
	token = request.values.get("token", "").strip()

	if int(time.time()) - timestamp > 3600:
		stop(410, "This email verification link has expired. Visit your settings to send yourself a new one!")

	user = get_account(id)

	if not validate_hash(f"{email}+{id}+{timestamp}", token):
		stop(403)

	if user.email_verified and user.email == email:
		stop(400, "Email already verified!")

	user.email = email
	user.email_verified = True
	claim_rewards_all_users()

	badge_grant(user=user, badge_id=2)

	g.db.add(user)

	return render_template("message_success.html", v=v, title="Email verified!", message=f"Your email {email} has been verified. Thank you!")
