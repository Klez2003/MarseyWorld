import time
import secrets
import user_agents
from flask import g, request, session

from files.classes.clients import ClientAuth
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.get import get_account
from files.helpers.logging import log_file
from files.helpers.settings import *
from files.helpers.cloudflare import *
from files.routes.routehelpers import validate_formkey, check_session_id
from files.__main__ import app, limiter

def rpath(n):
	return request.path

def get_ID():
	if request.headers.get("Authorization"):
		x = request.headers.get("Authorization")
	elif session.get("lo_user"):
		x = session.get("lo_user")
	else:
		check_session_id()
		x = f"logged_out-{session['session_id']}"

	return f'{SITE}-{x}'

def calc_users():
	g.loggedin_counter = 0
	g.loggedout_counter = 0
	g.loggedin_chat = 0
	v = getattr(g, 'v', None) if g else None
	if has_request_context and g and g.desires_auth and not g.is_api_or_xhr:
		loggedin = cache.get(LOGGED_IN_CACHE_KEY) or {}
		loggedout = cache.get(LOGGED_OUT_CACHE_KEY) or {}
		g.loggedin_chat = cache.get('loggedin_chat') or 0

		timestamp = int(time.time())

		check_session_id()

		if v:
			if session["session_id"] in loggedout: del loggedout[session["session_id"]]
			loggedin[v.id] = timestamp
		else:
			ua = str(user_agents.parse(g.agent))
			if 'spider' not in ua.lower() and 'bot' not in ua.lower():
				loggedout[session["session_id"]] = (timestamp, ua)

		loggedin = {k: v for k, v in loggedin.items() if (timestamp - v) < LOGGEDIN_ACTIVE_TIME}
		loggedout = {k: v for k, v in loggedout.items() if (timestamp - v[0]) < LOGGEDIN_ACTIVE_TIME}
		cache.set(LOGGED_IN_CACHE_KEY, loggedin, timeout=86400)
		cache.set(LOGGED_OUT_CACHE_KEY, loggedout, timeout=86400)
		g.loggedin_counter = len(loggedin)
		g.loggedout_counter = len(loggedout)

		if SITE != 'watchpeopledie.tv':
			if g.loggedin_counter + g.loggedout_counter > 2000:
				if not get_setting('under_attack'):
					set_setting('under_attack', True)
					set_security_level('under_attack')
			else:
				if get_setting('under_attack'):
					set_setting('under_attack', False)
					set_security_level('high')

	return ''

def get_logged_in_user():
	if hasattr(g, 'v') and g.v: return g.v
	g.desires_auth = True
	v = None
	token = request.headers.get("Authorization","").strip()
	if token:
		client = g.db.query(ClientAuth).filter(ClientAuth.access_token == token).one_or_none()
		if client:
			v = client.user
			v.client = client
	else:
		lo_user = session.get("lo_user")
		if lo_user:
			id = int(lo_user)
			v = get_account(id, graceful=True)
			if v:
				v.client = None
				nonce = session.get("login_nonce", 0)
				if nonce < v.login_nonce or v.id != id:
					session.pop("lo_user")
					v = None

				if v and request.method != "GET":
					submitted_key = request.values.get("formkey")
					if v:
						g.username = v.username
					if not validate_formkey(v, submitted_key):
						v = None
			else:
				session.pop("lo_user")

	if request.path not in {'/contact', '/reply', '/socket.io/'} and v and v.is_underage:
		stop(406)

	if request.method != "GET" and get_setting('read_only_mode') and not (v and v.admin_level >= PERMS['BYPASS_SITE_READ_ONLY_MODE']):
		stop(403, "Site is in read-only mode right now. It will be back shortly!")

	if get_setting('offline_mode') and not (v and v.admin_level >= PERMS['SITE_OFFLINE_MODE']):
		stop(403, "Site is in offline mode right now. It will be back shortly!")

	g.v = v
	if v:
		g.username = v.username

	if not v and SITE == 'rdrama.net' and request.headers.get("Cf-Ipcountry") == 'EG':
		stop(403, "rdrama.net is only available to visitors from the United States and Europe!")

	g.is_api_or_xhr = bool((v and v.client) or request.headers.get("xhr"))

	g.is_tor = (request.headers.get("cf-ipcountry") == "T1" and not (v and v.truescore >= 1000))

	if v and not IS_MUSICAL_EVENT():
		session.pop("event_music", None)

	g.show_nsfw = SITE_NAME == 'WPD' or (v and not v.nsfw_warnings) or session.get('nsfw_cookies', 0) >= int(time.time())

	return v

def auth_desired(f):
	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

def auth_desired_with_logingate(f):
	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		if not v and get_setting('login_required'):
			stop(401, "You need to login to perform this action!")

		# if not v and get_setting('under_attack'):
		# 	stop(418)

		if request.path.startswith('/logged_out'):
			redir = request.full_path.replace('/logged_out','')
			if not redir: redir = '/'
			return redirect(redir)

		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

def auth_required(f):
	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		if not v:
			stop(401, "You need to login to perform this action!")
		if v.is_permabanned and request.method == "POST" and request.path not in {'/contact','/reply','/logout'} and not request.path.startswith('/delete/'):
			stop(403, "You can't perform this action while permabanned!")

		if request.path.startswith('/@deleted~') and v.admin_level < PERMS['VIEW_DELETED_ACCOUNTS']:
			stop(403, "Account is deleted.")

		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

def admin_level_required(x):
	def wrapper_maker(f):
		def wrapper(*args, **kwargs):
			v = get_logged_in_user()
			if not v:
				stop(401, "You need to login to perform this action!")
			if v.admin_level < x:
				stop(403, "Your admin-level is not sufficient enough for this action!")
			if x and SITE != 'devrama.net' and not IS_LOCALHOST and not v.mfa_secret:
				stop(403, "You need to enable two-factor authentication to use admin features!")
			return make_response(f(*args, v=v, **kwargs))

		wrapper.__name__ = f.__name__
		return wrapper
	return wrapper_maker

def feature_required(x):
	def wrapper_maker(f):
		def wrapper(*args, **kwargs):
			if not FEATURES[x]: stop(404)
			return make_response(f(*args, **kwargs))
		wrapper.__name__ = f.__name__
		return wrapper
	return wrapper_maker
