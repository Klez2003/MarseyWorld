import secrets
from os import environ

from files.helpers.config.const import *
from files.helpers.settings import get_setting
from files.helpers.cloudflare import CLOUDFLARE_AVAILABLE
from files.routes.wrappers import *
from files.__main__ import app, limiter, get_CF, redis_instance

@app.before_request
def before_request():
	g.v = None

	if request.host != SITE:
		abort(403, "Unauthorized host provided!")

	if SITE == 'marsey.world' and request.path != '/kofi':
		abort(404)

	if request.headers.get("CF-Worker"):
		abort(403, "Cloudflare workers are not allowed to access this website!")

	g.agent = request.headers.get("User-Agent", "")
	if not g.agent and request.path != '/kofi':
		abort(403, 'Please use a "User-Agent" header!')

	if not get_setting('bots') and request.headers.get("Authorization"):
		abort(403)

	g.desires_auth = False

	ua = g.agent.lower()

	if '; wv) ' in ua:
		g.browser = 'webview'
	elif ' firefox/' in ua:
		g.browser = 'firefox'
	elif 'iphone' in ua or 'ipad' in ua or 'ipod' in ua:
		g.browser = 'iphone'
	elif 'mac os' in ua:
		g.browser = 'mac'
	else:
		g.browser = 'chromium'

	request.path = request.path.rstrip('/')
	if not request.path: request.path = '/'
	request.full_path = request.full_path.rstrip('?').rstrip('/')
	if not request.full_path: request.full_path = '/'

	g.db = db_session()

	g.nonce = secrets.token_urlsafe(31)


@app.after_request
def after_request(response):
	user_id = None

	if response.status_code < 400:
		if hasattr(g, 'v') and g.v:
			user_id = g.v.id

			if not session.get("GLOBAL") and request.method == "POST":
				timestamp = int(time.time())
				if (g.v.last_active + LOGGEDIN_ACTIVE_TIME) < timestamp:
					g.v.last_active = timestamp
					g.db.add(g.v)

		_commit_and_close_db()

	if request.method == "POST":
		redis_instance.delete(f'LIMITER/{get_CF()}/{request.endpoint}:{request.path}/1/1/second')
		if user_id:
			redis_instance.delete(f'LIMITER/{SITE}-{user_id}/{request.endpoint}:{request.path}/1/1/second')

	cookie_name = app.config["SESSION_COOKIE_NAME"]

	if SITE == 'watchpeopledie.tv' and request.path == '/':
		value = request.cookies.get(cookie_name)
		if value:
			response.set_cookie(cookie_name, 'test', max_age=0)
			response.set_cookie(cookie_name, value, max_age=1723908553, domain=f".{SITE}")

	if SITE == 'rdrama.net':
		if len(request.cookies.getlist(cookie_name)) > 1:
			response.set_cookie(cookie_name, 'test', max_age=0, domain=f".{SITE}")
			response.set_cookie(cookie_name, 'test', max_age=0)
			session.clear()
			print(f"{STARS}Cleared {user_id}'s cookies successfully!{STARS}", flush=True)

	return response


@app.teardown_appcontext
def teardown_request(error):
	_rollback_and_close_db()
	stdout.flush()

def _commit_and_close_db():
	if not getattr(g, 'db', None): return False
	g.db.commit()
	g.db.close()
	del g.db
	return True

def _rollback_and_close_db():
	if not getattr(g, 'db', None): return False
	g.db.rollback()
	g.db.close()
	del g.db
	return True
