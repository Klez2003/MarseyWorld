import secrets

from files.helpers.const import *
from files.helpers.settings import get_setting
from files.helpers.cloudflare import CLOUDFLARE_AVAILABLE
from files.routes.wrappers import *
from files.__main__ import app, limiter

def session_init():
	if not session.get("session_id"):
		session.permanent = True
		session["session_id"] = secrets.token_hex(49)

@app.before_request
def before_request():
	g.desires_auth = False
	if SITE == 'marsey.world' and request.path != '/kofi':
		abort(404)

	g.agent = request.headers.get("User-Agent", "")
	if not g.agent and request.path != '/kofi':
		return 'Please use a "User-Agent" header!', 403

	ua = g.agent.lower()

	if request.host != SITE:
		return {"error": "Unauthorized host provided"}, 403

	if request.headers.get("CF-Worker"): return {"error": "Cloudflare workers are not allowed to access this website."}, 403

	if not get_setting('bots') and request.headers.get("Authorization"): abort(403)

	if '; wv) ' in ua:
		g.browser = 'webview'
	elif ' firefox/' in ua:
		g.browser = 'firefox'
	elif 'iphone' in ua or 'ipad' in ua or 'ipod' in ua or 'mac os' in ua:
		g.browser = 'apple'
	else:
		g.browser = 'chromium'

	g.is_tor = request.headers.get("cf-ipcountry") == "T1"

	request.path = request.path.rstrip('/')
	if not request.path: request.path = '/'
	request.full_path = request.full_path.rstrip('?').rstrip('/')
	if not request.full_path: request.full_path = '/'

	session_init()
	limiter.check()
	g.db = db_session()


@app.after_request
def after_request(response:Response):
	_fix_frozen_sessions(response)
	if response.status_code < 400:
		_set_cloudflare_cookie(response)
		_commit_and_close_db()
	return response


@app.teardown_appcontext
def teardown_request(error):
	_rollback_and_close_db()
	stdout.flush()

def _set_cloudflare_cookie(response:Response) -> None:
	'''
	Sets a cookie that can be used by an upstream DDoS protection and caching provider
	'''
	if not g.desires_auth: return
	if not CLOUDFLARE_AVAILABLE or not CLOUDFLARE_COOKIE_VALUE: return
	logged_in = bool(getattr(g, 'v', None))
	response.set_cookie("lo", CLOUDFLARE_COOKIE_VALUE if logged_in else '', 
						max_age=60*60*24*365 if logged_in else 1, samesite="Lax",
						domain=app.config["COOKIE_DOMAIN"])

def _fix_frozen_sessions(response:Response) -> None:
	'''
	Deletes bad session cookies, hopefuly resolving an ongoing issue with sessions becoming
	frozen. This deletes cookies whose domain don't start with a dot (on domains that have
	at least one dot in them)
	'''
	domain = app.config["SESSION_COOKIE_DOMAIN"]
	if IS_LOCALHOST or not '.' in domain: return # "dotless" domains in general aren't really supportable

	bad_domain = domain.replace('.', '', 1)
	cookie_header = request.headers.get("Cookie")
	response.delete_cookie(app.config["SESSION_COOKIE_NAME"], domain=bad_domain, httponly=True, secure=True)
	if not cookie_header or not f'domain={bad_domain}' in cookie_header: return

def _commit_and_close_db() -> bool:
	if not getattr(g, 'db', None): return False
	g.db.commit()
	g.db.close()
	del g.db
	return True

def _rollback_and_close_db() -> bool:
	if not getattr(g, 'db', None): return False
	g.db.rollback()
	g.db.close()
	del g.db
	return True
