import time
import secrets
import user_agents
import uuid
from flask import g, request, session

from files.classes.clients import ClientAuth
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.get import get_account
from files.helpers.logging import log_file
from files.helpers.settings import *
from files.helpers.cloudflare import *
from files.routes.routehelpers import validate_formkey
from files.__main__ import app, db_session, limiter

def rpath(n):
	return request.path

def get_ID():
	if request.headers.get("Authorization"):
		x = request.headers.get("Authorization")
	elif session.get("lo_user"):
		x = session.get("lo_user")
	else:
		x = "logged_out"

	return f'{SITE}-{x}'

def calc_users():
	g.loggedin_counter = 0
	g.loggedout_counter = 0
	g.loggedin_chat = 0
	v = getattr(g, 'v', None) if g else None
	if has_request_context and g and g.desires_auth and not g.is_api_or_xhr:
		loggedin = cache.get(LOGGED_IN_CACHE_KEY) or {}
		loggedout = cache.get(LOGGED_OUT_CACHE_KEY) or {}
		g.loggedin_chat = cache.get(CHAT_ONLINE_CACHE_KEY) or 0
		timestamp = int(time.time())

		if not session.get("session_id"):
			session.permanent = True
			session["session_id"] = str(uuid.uuid4())

		if v:
			if session["session_id"] in loggedout: del loggedout[session["session_id"]]
			loggedin[v.id] = timestamp
		else:
			ua = str(user_agents.parse(g.agent))
			if 'spider' not in ua.lower() and 'bot' not in ua.lower():
				loggedout[session["session_id"]] = (timestamp, ua)

		loggedin = {k: v for k, v in loggedin.items() if (timestamp - v) < LOGGEDIN_ACTIVE_TIME}
		loggedout = {k: v for k, v in loggedout.items() if (timestamp - v[0]) < LOGGEDIN_ACTIVE_TIME}
		cache.set(LOGGED_IN_CACHE_KEY, loggedin)
		cache.set(LOGGED_OUT_CACHE_KEY, loggedout)
		g.loggedin_counter = len(loggedin)
		g.loggedout_counter = len(loggedout)

		if SITE == 'watchpeopledie.tv':
			ddos_threshold = 3000
		else:
			ddos_threshold = 1000

		if g.loggedout_counter > ddos_threshold:
			if not get_setting('ddos_detected'):
				toggle_setting('ddos_detected')
				set_security_level('under_attack')
		else:
			if get_setting('ddos_detected'):
				toggle_setting('ddos_detected')
				set_security_level('high')
	return ''

def get_logged_in_user():
	if hasattr(g, 'v') and g.v: return g.v
	if not hasattr(g, 'db'): g.db = db_session()
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
					if not validate_formkey(v, submitted_key):
						v = None
			else:
				session.pop("lo_user")

	if request.method.lower() != "get" and get_setting('read_only_mode') and not (v and v.admin_level >= PERMS['SITE_BYPASS_READ_ONLY_MODE']):
		abort(403, "Site is in read-only mode right now. It will be back shortly!")

	if get_setting('offline_mode') and not (v and v.admin_level >= PERMS['SITE_OFFLINE_MODE']):
		abort(403, "Site is in offline mode right now. It will be back shortly!")

	g.v = v

	if v:
		v.poor = session.get('poor')
		# Check against last_active + ACTIVE_TIME to reduce frequency of
		# UPDATEs in exchange for a ±ACTIVE_TIME margin of error.

		if not session.get("GLOBAL") and request.method == "POST" and not request.path.startswith('/vote/'):
			timestamp = int(time.time())
			if (v.last_active + LOGGEDIN_ACTIVE_TIME) < timestamp:
				v.last_active = timestamp
				g.db.add(v)

	if not v and SITE == 'rdrama.net' and request.headers.get("Cf-Ipcountry") == 'EG':
		abort(404)

	g.is_api_or_xhr = bool((v and v.client) or request.headers.get("xhr"))

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
		if not v and (get_setting('login_required') or get_setting('ddos_detected')):
			abort(401, "You need to login to perform this action!")

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
			abort(401, "You need to login to perform this action!")
		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

def is_not_banned(f):
	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		if not v:
			abort(401, "You need to login to perform this action!")
		if v.is_suspended:
			abort(403, "You can't perform this action while banned!")
		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

def is_not_permabanned(f):
	def wrapper(*args, **kwargs):
		v = get_logged_in_user()
		if not v:
			abort(401, "You need to login to perform this action!")
		if v.is_permabanned:
			abort(403, "You can't perform this action while permabanned!")
		return make_response(f(*args, v=v, **kwargs))
	wrapper.__name__ = f.__name__
	return wrapper

def admin_level_required(x):
	def wrapper_maker(f):
		def wrapper(*args, **kwargs):
			v = get_logged_in_user()
			if not v:
				abort(401, "You need to login to perform this action!")
			if v.admin_level < x:
				abort(403, "Your admin-level is not sufficient enough for this action!")
			if x and SITE != 'devrama.net' and not IS_LOCALHOST and not v.mfa_secret:
				abort(403, "You need to enable two-factor authentication to use admin features!")
			return make_response(f(*args, v=v, **kwargs))

		wrapper.__name__ = f.__name__
		return wrapper
	return wrapper_maker

def feature_required(x):
	def wrapper_maker(f):
		def wrapper(*args, **kwargs):
			if not FEATURES[x]: abort(404)
			return make_response(f(*args, **kwargs))
		wrapper.__name__ = f.__name__
		return wrapper
	return wrapper_maker
