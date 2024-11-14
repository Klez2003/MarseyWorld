import secrets

import requests

from files.__main__ import app, cache, get_IP, limiter
from files.classes.follows import Follow
from files.helpers.actions import *
from files.helpers.config.const import *
from files.helpers.settings import get_setting
from files.helpers.get import *
from files.helpers.mail import send_mail, send_verification_email
from files.helpers.logging import log_file
from files.helpers.regex import *
from files.helpers.security import *
from files.helpers.useractions import badge_grant
from files.routes.routehelpers import check_for_alts
from files.routes.wrappers import *


NO_LOGIN_REDIRECT_URLS = ("/login", "/logout", "/signup", "/forgot", "/reset", "/reset_2fa", "/lost_2fa")

@app.get("/login")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_desired
def login_get(v):
	redir = request.values.get("redirect", "").strip().rstrip('?').lower()
	if v:
		if redir and is_site_url(redir) and redir not in NO_LOGIN_REDIRECT_URLS:
			return redirect(redir)
		return redirect('/')
	return render_template("login/login.html", failed=False, redirect=redir)

@app.post("/login")
@limiter.limit('1/second', scope=rpath)
@limiter.limit("6/minute;20/hour;100/day", deduct_when=lambda response: response.status_code < 400)
@auth_desired
def login_post(v):
	if v: stop(400)

	username = request.values.get("username")

	if not username: stop(400)
	username = sanitize_username(username)

	if not username: stop(400)
	if username.startswith('@'): username = username[1:]

	if "@" in username:
		try: account = g.db.query(User).filter(User.email.ilike(username)).one_or_none()
		except: stop(400, "Multiple accounts have this email attached.<br>Please login using a username instead of an email!")
	else: account = get_user(username, graceful=True)

	redir = request.values.get("redirect", "").strip().rstrip('?').lower()

	if not account:
		time.sleep(random.uniform(0, 2))
		return render_template("login/login.html", failed=True, redirect=redir)


	if request.values.get("password"):
		if not account.verifyPass(request.values.get("password")):
			log_failed_admin_login_attempt(account, "password")
			time.sleep(random.uniform(0, 2))
			return render_template("login/login.html", failed=True, redirect=redir)

		if account.mfa_secret or session.get("GLOBAL"):
			now = int(time.time())
			hash = generate_hash(f"{account.id}+{now}+2fachallenge")
			return render_template("login/login_2fa.html",
								v=account,
								time=now,
								hash=hash,
								redirect=request.values.get("redirect", "/")
								)
	elif request.values.get("2fa_token", "x"):
		now = int(time.time())

		try:
			if now - int(request.values.get("time")) > 600:
				return render_template("login/login.html", failed=True, redirect=redir)
		except:
			stop(400)

		formhash = request.values.get("hash")
		if not validate_hash(f"{account.id}+{request.values.get('time')}+2fachallenge", formhash):
			return render_template("login/login.html", failed=True, redirect=redir)

		if not account.validate_2fa(request.values.get("2fa_token", "").strip()):
			hash = generate_hash(f"{account.id}+{now}+2fachallenge")
			log_failed_admin_login_attempt(account, "2FA token")
			return render_template("login/login_2fa.html",
								v=account,
								time=now,
								hash=hash,
								failed=True,
								redirect=redir,
								), 400
	else:
		stop(400)

	session.permanent = True
	session["lo_user"] = account.id
	g.v = account
	g.username = account.username
	session["login_nonce"] = account.login_nonce
	check_for_alts(account, include_current_session=True)

	if account.deletion:
		g.db.delete(account.deletion)

	if redir and is_site_url(redir) and redir not in NO_LOGIN_REDIRECT_URLS:
		return redirect(redir)
	return redirect('/')

def log_failed_admin_login_attempt(account, type):
	if not account or account.admin_level < PERMS['WARN_ON_FAILED_LOGIN']: return
	ip = get_IP()
	print(f"A site admin from {ip} failed to login to account @{account.username} (invalid {type})")
	t = time.strftime("%d/%B/%Y %H:%M:%S UTC", time.gmtime(time.time()))
	log_file(f"{t}, {ip}, {account.username}, {type}", "admin_failed_logins.log")

@app.get("/me")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def me(v):
	if v.client: return v.json
	else: return redirect(v.url)


@app.post("/logout")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def logout(v):
	loggedin = cache.get('loggedin') or {}
	if session.get("lo_user") in loggedin: del loggedin[session["lo_user"]]
	cache.set('loggedin', loggedin, timeout=86400)
	session.pop("lo_user", None)
	return {"message": "Logout successful!"}

@app.get("/signup")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_desired
def sign_up_get(v):
	if not get_setting('signups'):
		stop(403, "New account registration is currently closed. Please come back later!")

	if v: return redirect(SITE_FULL)

	ref = request.values.get("ref")

	ref_user = get_account(ref, graceful=True)

	if ref_user and (ref_user.id in session.get("history", [])):
		return render_template("login/sign_up_failed_ref.html"), 403

	now = int(time.time())
	token = secrets.token_urlsafe(32)
	session["signup_token"] = token

	formkey_hashstr = str(now) + token + g.agent

	formkey = hmac.new(key=bytes(SECRET_KEY, "utf-16"),
					msg=bytes(formkey_hashstr, "utf-16"),
					digestmod='md5'
					).hexdigest()

	error = request.values.get("error")

	redir = request.values.get("redirect", "/").strip().rstrip('?')
	if redir:
		if not is_site_url(redir): redir = "/"

	status_code = 200 if not error else 400

	return render_template("login/sign_up.html",
						formkey=formkey,
						now=now,
						ref_user=ref_user,
						turnstile=TURNSTILE_SITEKEY,
						error=error,
						redirect=redir
						), status_code


@app.post("/signup")
@limiter.limit('1/second', scope=rpath)
@limiter.limit("10/day", deduct_when=lambda response: response.status_code < 400)
@auth_desired
def sign_up_post(v):
	if not get_setting('signups'):
		stop(403, "New account registration is currently closed. Please come back later!")

	if v: stop(403)

	form_timestamp = request.values.get("now", '0')
	form_formkey = request.values.get("formkey", "none")

	username = request.values.get("username", "").strip()
	if not username: stop(400)

	email = request.values.get("email", "").strip().lower()

	ref_id = 0
	try:
		ref_id = int(request.values.get("referred_by", 0))
	except:
		pass

	redir = request.values.get("redirect", "").strip().rstrip('?').lower()

	def signup_error(error):
		if ref_id:
			ref_user = g.db.get(User, ref_id)
		else:
			ref_user = None

		now = int(time.time())
		token = secrets.token_urlsafe(32)
		session["signup_token"] = token
		formkey_hashstr = str(now) + token + g.agent
		formkey = hmac.new(key=bytes(SECRET_KEY, "utf-16"),
						msg=bytes(formkey_hashstr, "utf-16"),
						digestmod='md5'
						).hexdigest()

		return render_template("login/sign_up.html",
							formkey=formkey,
							now=now,
							ref_user=ref_user,
							turnstile=TURNSTILE_SITEKEY,
							error=error,
							redirect=redir,
							username=username,
							email=email,
							), 400

	if username.title() in GIRL_NAMES_TOTAL:
		return signup_error("This name is reserved for a site award.")

	submitted_token = session.get("signup_token", "")
	if not submitted_token:
		session.clear()
		return signup_error(f"An error occurred while attempting to signup. If you get this repeatedly, please make sure cookies are enabled!")

	correct_formkey_hashstr = form_timestamp + submitted_token + g.agent
	correct_formkey = hmac.new(key=bytes(SECRET_KEY, "utf-16"),
								msg=bytes(correct_formkey_hashstr, "utf-16"),
								digestmod='md5'
							).hexdigest()

	now = int(time.time())

	if now - int(form_timestamp) < 5:
		return signup_error("There was a problem. Please try again!")

	if not hmac.compare_digest(correct_formkey, form_formkey):
		if IS_LOCALHOST: return signup_error("There was a problem. Please try again!")
		return signup_error("There was a problem. Please try again!")

	if not request.values.get("password") == request.values.get("password_confirm"):
		return signup_error("Passwords did not match. Please try again!")

	if not valid_username_regex.fullmatch(username):
		return signup_error("Invalid username")

	if not valid_password_regex.fullmatch(request.values.get("password")):
		return signup_error("Password must be between 8 and 100 characters!")

	if email:
		if not email_regex.fullmatch(email):
			return signup_error("Invalid email!")
	else: email = None

	g.db.flush()
	existing_account = get_user(username, graceful=True)
	if existing_account:
		return signup_error("An account with that username already exists!")

	if TURNSTILE_SITEKEY != DEFAULT_CONFIG_VALUE:
		token = request.values.get("cf-turnstile-response")
		if not token:
			return signup_error("Unable to verify captcha [1].")

		data = {"secret": TURNSTILE_SECRET,
				"response": token,
				"sitekey": TURNSTILE_SITEKEY}
		url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"

		try: x = requests.post(url, data=data, timeout=5)
		except: pass
		else:
			try:
				if not x.json().get("success"):
					return signup_error("Unable to verify captcha [2].")
			except:
				return signup_error("Unable to verify captcha [2].")

	session.pop("signup_token")

	profileurl = None
	if PFP_DEFAULT_MARSEY:
		profileurl = '/e/' + random.choice(MARSEYS_CONST) + '.webp'

	new_user = User(
		username=username,
		original_username = username,
		password=request.values.get("password"),
		email=email,
		referred_by=ref_id or None,
		profileurl=profileurl
		)

	g.db.add(new_user)

	g.db.flush()

	if new_user.id == 5:
		new_user.admin_level = 100000000
		new_user.coins = 100000000
		new_user.marseybux = 100000000
		session.pop("history", None)

	if ref_id and ref_id not in session.get("history", []):
		ref_user = get_account(ref_id)

		if ref_user:
			send_notification(ref_user.id, f"A new user - @{new_user.username} - has signed up via your referral link!")

			badge_grant(user=ref_user, badge_id=10)
			if ref_user.referral_count >= 10:
				badge_grant(user=ref_user, badge_id=11)
			if ref_user.referral_count >= 100:
				badge_grant(user=ref_user, badge_id=12)

	if email:
		send_verification_email(new_user)


	session.permanent = True
	session["lo_user"] = new_user.id
	g.v = new_user
	g.username = new_user.username

	send_notification(new_user.id, WELCOME_MSG)

	if SIGNUP_FOLLOW_ID:
		signup_autofollow = get_account(SIGNUP_FOLLOW_ID)
		new_follow = Follow(user_id=new_user.id, target_id=signup_autofollow.id)
		g.db.add(new_follow)
		signup_autofollow.stored_subscriber_count += 1
		g.db.add(signup_autofollow)
	elif CARP_ID:
		send_notification(CARP_ID, f"A new user - @{new_user.username} - has signed up!")

	execute_blackjack(new_user, None, new_user.username, 'username')
	check_name(new_user)

	cache.delete("user_count")

	g.db.commit()
	check_for_alts(new_user, include_current_session=True)

	if redir and is_site_url(redir) and redir not in NO_LOGIN_REDIRECT_URLS:
		return redirect(redir)
	return redirect('/')


@app.get("/forgot")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
def get_forgot():
	return render_template("login/forgot_password.html")


@app.post("/forgot")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('3/day', deduct_when=lambda response: response.status_code < 400)
def post_forgot():
	def error(error):
		return render_template("login/forgot_password.html", error=error), 400

	username_or_email = request.values.get("username_or_email", "").strip().lstrip('@')
	if not username_or_email:
		return error("You need to enter something.")

	if '@' in username_or_email:
		if not email_regex.fullmatch(username_or_email):
			return error("Invalid email.")
		count = g.db.query(User).filter_by(email=username_or_email).count()
		if not count:
			return error("No accounts have this email attached.")
		if count > 1:
			return error("Multiple accounts have this email attached. Please use a username instead.")

		user = g.db.query(User).filter_by(email=username_or_email).one()
	else:
		user = get_user(username_or_email, graceful=True)
		if not user:
			return error("There's no accounts with this username.")
		if not user.email:
			return error("This account doesn't have an email attached.")

	if user.id != GTIX_ID:
		now = int(time.time())
		token = generate_hash(f"{user.id}+{now}+forgot+{user.login_nonce}")
		url = f"{SITE_FULL}/reset?id={user.id}&time={now}&token={token}"

		send_mail(to_address=user.email,
				subject="Password Reset Request",
				html=render_template("email/password_reset.html", action_url=url, v=user),
				)

	return render_template("login/forgot_password.html", msg="An email was sent to you. Please check your spam folder if you can't find it.")


@app.get("/reset")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
def get_reset():
	user_id = request.values.get("id")
	timestamp = 0
	try:
		timestamp = int(request.values.get("time",0))
	except:
		pass
	token = request.values.get("token")
	now = int(time.time())

	if now - timestamp > 600:
		stop(410, "This password reset link has expired!")

	user = get_account(user_id)

	if not validate_hash(f"{user_id}+{timestamp}+forgot+{user.login_nonce}", token):
		stop(400)

	reset_token = generate_hash(f"{user.id}+{timestamp}+reset+{user.login_nonce}")

	return render_template("login/reset_password.html",
						v=user,
						token=reset_token,
						time=timestamp,
						)


@app.post("/reset")
@limiter.limit('1/second', scope=rpath)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_desired
def post_reset(v):
	if v: return redirect('/')
	user_id = request.values.get("user_id")
	timestamp = 0
	try:
		timestamp = int(request.values.get("time"))
	except:
		stop(400)
	token = request.values.get("token")
	password = request.values.get("password")
	confirm_password = request.values.get("confirm_password")

	now = int(time.time())

	if now - timestamp > 600:
		stop(410, "This password reset link has expired!")

	user = get_account(user_id)
	if not validate_hash(f"{user_id}+{timestamp}+reset+{user.login_nonce}", token):
		stop(400)

	if password != confirm_password:
		return render_template("login/reset_password.html",
							v=user,
							token=token,
							time=timestamp,
							error="Passwords didn't match."), 400

	if not valid_password_regex.fullmatch(password):
		return render_template("login/reset_password.html",
							v=user,
							token=token,
							time=timestamp,
							error="Password must be between 8 and 100 characters."), 400

	user.passhash = hash_password(password)
	g.db.add(user)


	return render_template("message_success.html",
						title="Password reset successful!",
						message="Login normally to access your account.")

@app.get("/lost_2fa")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_desired
def lost_2fa(v):
	if v and not v.mfa_secret: stop(400, "You don't have two-factor authentication enabled")
	return render_template("login/lost_2fa.html", v=v)

@app.post("/lost_2fa")
@limiter.limit('1/second', scope=rpath)
@limiter.limit("3/day", deduct_when=lambda response: response.status_code < 400)
@auth_desired
def lost_2fa_post(v):
	username = request.values.get("username")
	user = get_user(username, graceful=True)
	if not user or not user.email or not user.mfa_secret:
		return render_template("message.html",
						title="Removal request received",
						message="If username, password, and email match, we will send you an email.",
						v=v), 202


	email = request.values.get("email").strip().lower()

	if not email_regex.fullmatch(email):
		stop(400, "Invalid email")

	password = request.values.get("password")
	if not user.verifyPass(password):
		return render_template("message.html",
						title="Removal request received",
						message="If username, password, and email match, we will send you an email.",
						v=v), 202

	valid = int(time.time())
	token = generate_hash(f"{user.id}+{user.username}+disable2fa+{valid}+{user.mfa_secret}+{user.login_nonce}")

	action_url = f"{SITE_FULL}/reset_2fa?id={user.id}&t={valid}&token={token}"

	send_mail(to_address=user.email,
			subject="Two-factor Authentication Removal Request",
			html=render_template("email/2fa_remove.html",
								action_url=action_url,
								v=user)
			)

	return render_template("message.html",
						title="Removal request received",
						message="If the username, password, and email match, we will send you an email. Please check your spam folder if you can't find it.",
						v=v), 202

@app.get("/reset_2fa")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
def reset_2fa():
	now = int(time.time())
	t = request.values.get("t")
	if not t: stop(400)
	try:
		t = int(t)
	except:
		stop(400)

	if now > t+3600*24:
		stop(410, "This two-factor authentication reset link has expired!")

	token = request.values.get("token")
	uid = request.values.get("id")

	user = get_account(uid)

	if not validate_hash(f"{user.id}+{user.username}+disable2fa+{t}+{user.mfa_secret}+{user.login_nonce}", token):
		stop(403)

	user.mfa_secret=None
	g.db.add(user)

	return render_template("message_success.html",
						title="Two-factor authentication removed.",
						message="Login normally to access your account.")
