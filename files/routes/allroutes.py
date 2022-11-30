import secrets

from files.helpers.const import *
from files.helpers.security import generate_csp_header
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
	# note: deferring csp nonce generation until later
	# csps aren't given out to api clients and error
	# pages shouldn't have any inline elements for security 
	# reasons. generating a nonce and csp for them 
	g.csp_nonce = None
	if request.host != SITE: return Response('', 404, mimetype="text/plain")
	if SITE == 'marsey.world' and request.path != '/kofi':
		abort(404)

	g.agent = request.headers.get("User-Agent", "")
	if not g.agent and request.path != '/kofi':
		abort(403, "User agent header is required")

	ua = g.agent.lower()

	if request.headers.get("CF-Worker"): return {"error": "Cloudflare workers are not allowed to access this website."}, 403

	if not get_setting('bots') and request.headers.get("Authorization"): abort(403)

	g.webview = '; wv) ' in ua

	if ' firefox/' in ua:
		g.type = 'firefox'
	elif 'iphone' in ua or 'ipad' in ua or 'ipod' in ua or 'mac os' in ua:
		g.type = 'apple'
	else:
		g.type = 'chromium'

	g.is_tor = request.headers.get("cf-ipcountry") == "T1"

	request.path = request.path.rstrip('/')
	if not request.path: request.path = '/'
	request.full_path = request.full_path.rstrip('?').rstrip('/')
	if not request.full_path: request.full_path = '/'

	session_init()
	limiter.check()
	g.db = db_session()


@app.after_request
def after_request(response):
	if response.content_type == "text/html":
		response.headers["Content-Security-Policy"] = generate_csp_header(g.csp_nonce)
	if response.status_code < 400:
		if CLOUDFLARE_AVAILABLE and CLOUDFLARE_COOKIE_VALUE and g.desires_auth:
			logged_in = bool(getattr(g, 'v', None))
			response.set_cookie("lo", CLOUDFLARE_COOKIE_VALUE if logged_in else '', 
								max_age=60*60*24*365 if logged_in else 1, samesite="Lax")
		if getattr(g, 'db', None):
			g.db.commit()
			g.db.close()
			del g.db
	return response


@app.teardown_appcontext
def teardown_request(error):
	if getattr(g, 'db', None):
		g.db.rollback()
		g.db.close()
		del g.db
	stdout.flush()
