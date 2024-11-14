import gevent.monkey

gevent.monkey.patch_all()

import faulthandler
from os import environ
from sys import argv, stdout

import redis
import gevent
from flask import Flask
from flask_caching import Cache
from flask_compress import Compress
from flask_limiter import Limiter

from files.helpers.config.const import *
from files.helpers.const_stateful import const_initialize
from files.helpers.settings import reload_settings, start_watching_settings

app = Flask(__name__, template_folder='templates')
app.url_map.strict_slashes = False
app.jinja_env.cache = {}
app.jinja_env.auto_reload = True
app.jinja_env.add_extension('jinja2.ext.do')
faulthandler.enable()

def _startup_check():
	'''
	Performs some sanity checks on startup to make sure we aren't attempting
	to startup with obviously invalid values that won't work anyway
	'''
	if not SITE: raise TypeError("SITE environment variable must exist and not be None")
	if SITE.startswith('.'): raise ValueError("Domain must not start with a dot")

app.config['SERVER_NAME'] = SITE
app.config['SECRET_KEY'] = environ.get('SECRET_KEY').strip()
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 3153600
_startup_check()
if not IS_LOCALHOST:
	app.config["SESSION_COOKIE_SECURE"] = True

app.config["SESSION_COOKIE_NAME"] = "session_" + environ.get("SITE_NAME").strip().lower()
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024 if SITE == 'watchpeopledie.tv' else 100 * 1024 * 1024
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 24 * 999
app.config['SESSION_REFRESH_EACH_REQUEST'] = True

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config["CACHE_KEY_PREFIX"] = f"{SITE}_flask_cache_"
app.config["CACHE_TYPE"] = "RedisCache"
app.config["CACHE_REDIS_URL"] = environ.get("REDIS_URL").strip()
app.config["CACHE_DEFAULT_TIMEOUT"] = 0
app.config["CACHE_SOURCE_CHECK"] = True

#to allow session cookie to work on submit.watchpeopledie.tv
if SITE == 'watchpeopledie.tv':
	app.config["SESSION_COOKIE_DOMAIN"] = SITE

def get_IP():
	with app.app_context():
		x = request.headers.get('CF-Connecting-IP')
		if not x:
			x = request.headers.get('X-Forwarded-For')
		return x

limiter = Limiter(
	app=app,
	key_func=get_IP,
	default_limits=[DEFAULT_RATELIMIT],
	application_limits=["10/second;200/minute;5000/hour;30000/day"],
	storage_uri=app.config["CACHE_REDIS_URL"],
	default_limits_deduct_when=lambda response: response.status_code < 400,
)

const_initialize()

reload_settings()

if "cron" not in argv:
	start_watching_settings()

cache = Cache(app)
Compress(app)

from files.routes.allroutes import *

if "load_chat" in argv:
	from files.routes.chat import *
else:
	from files.routes import *

stdout.flush()
