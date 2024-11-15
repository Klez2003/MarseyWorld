import secrets
from os import environ

from files.helpers.config.const import *
from files.helpers.settings import get_setting
from files.helpers.cloudflare import CLOUDFLARE_AVAILABLE
from files.routes.wrappers import *
from files.__main__ import app, limiter, get_IP

if FEATURES['IP_LOGGING']:
	from files.classes.ip_logs import *

@app.before_request
def before_request():
	g.v = None

	if request.host != SITE:
		stop(403, "Unauthorized host provided!")

	if SITE == 'marsey.world' and request.path not in {'/kofi','/av'}:
		stop(404)

	if request.headers.get("CF-Worker"):
		stop(403, "Cloudflare workers are not allowed to access this website!")

	g.agent = request.headers.get("User-Agent", "")
	if not g.agent and request.path not in {'/kofi','/av'}:
		stop(403, 'Please use a "User-Agent" header!')

	if not get_setting('bots') and request.headers.get("Authorization"):
		stop(403)

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

				if FEATURES['IP_LOGGING'] and not session.get("GLOBAL") and g.v.admin_level < PERMS['EXEMPT_FROM_IP_LOGGING']:
					ip = get_IP()
					if ip:
						existing = g.db.query(IPLog).filter_by(user_id=user_id, ip=ip).one_or_none()
						if existing:
							existing.last_used = time.time()
							g.db.add(existing)
						else:
							ip_log = IPLog(
								user_id=user_id,
								ip=ip,
								)
							g.db.add(ip_log)

		_commit_and_close_db()

	if request.method == "POST":
		redis_instance.delete(f'LIMITER/{get_IP()}/{request.endpoint}:{request.path}/1/1/second')
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
