import time
import math
import datetime

from os import environ, listdir, path

from flask import g, session, has_request_context, request
from jinja2 import pass_context
from PIL import ImageColor
from sqlalchemy import text

from files.classes.user import User
from files.classes.orgy import get_running_orgy
from files.classes.emoji import Emoji
from files.helpers.assetcache import assetcache_path
from files.helpers.config.const import *
from files.helpers.const_stateful import OVER_18_EMOJIS
from files.helpers.regex import *
from files.helpers.settings import *
from files.helpers.cloudflare import *
from files.helpers.sorting_and_time import make_age_string
from files.helpers.can_see import *
from files.routes.routehelpers import get_alt_graph, get_formkey
from files.routes.wrappers import calc_users
from files.__main__ import app, cache

from urllib.parse import parse_qs, urlencode,  urlsplit

@app.template_filter("rgb")
def rgb(color):
	return str(ImageColor.getcolor(f"#{color}", "RGB"))[1:-1]

@app.template_filter("formkey")
def formkey(u):
	return get_formkey(u)

@app.template_filter("post_embed")
def post_embed(id, v):
	from flask import render_template

	from files.helpers.get import get_post
	p = get_post(id, v, graceful=True)
	if p: return render_template("post_listing.html", listing=[p], v=v)
	return ''

@app.template_filter("asset")
@pass_context
def template_asset(ctx, asset_path):
	return assetcache_path(asset_path)

@app.template_filter("change_arg")
def template_change_arg(arg, value, url):
	parsed = urlsplit(url)
	query_dict = parse_qs(parsed.query)
	query_dict.pop('page', None)
	query_dict[arg] = value
	query_new = urlencode(query_dict, doseq=True)
	parsed = parsed._replace(query=query_new)
	return parsed.geturl()

@app.template_filter("asset_siteimg")
def template_asset_siteimg(asset_path):
	return f'{SITE_FULL_IMAGES}/i/{SITE_NAME}/{asset_path}?x=6'

@app.template_filter("timestamp")
def timestamp(timestamp):
	return make_age_string(timestamp)

@app.template_filter("selected_tab")
def selected_tab(request):
	if request.path == '/':
		requested_sort = request.values.get('sort')
		if hasattr(g, 'v') and g.v and g.v.defaultsorting == 'new' and requested_sort == 'hot':
			return 'hot'
		elif requested_sort == 'new':
			return 'new'
	elif request.path == '/comments':
		return 'comments'
	elif request.path == '/casino':
		return 'casino'
	elif request.path == '/chat':
		return 'chat'
	elif request.path.startswith('/shop/'):
		return 'shop'

	return 'home'


def current_registered_users():
	return "{:,}".format(g.db.query(User).count())

def git_head():
	# Note: doing zero sanitization. Git branch names are extremely permissive.
	# However, they forbid '..', so I don't see an obvious dir traversal attack.
	# Also, a malicious branch name would mean someone already owned the server
	# or repo, so I think this isn't a weak link.
	with open('.git/HEAD') as head_f:
		head_txt = head_f.read()
		try:
			head_path = git_regex.match(head_txt).group(1)
			with open('.git/' + head_path) as ref_f:
				gitref = ref_f.read()[:7]
		except:
			gitref = 'Error'
	return (gitref, head_txt)

def max_days():
	return int((2147483647-time.time())/86400)

@cache.memoize(timeout=60)
def bar_position():
	t = int(time.time()) - 86400

	db = db_session()
	vaxxed = db.execute(text("SELECT COUNT(*) FROM users WHERE zombie > 0")).one()[0]
	zombie = db.execute(text("SELECT COUNT(*) FROM users WHERE zombie < 0")).one()[0]
	total = db.execute(text("SELECT COUNT(*) FROM "
		"(SELECT DISTINCT ON (author_id) author_id AS uid FROM comments "
			f"WHERE created_utc > {t}) AS q1 "
		"FULL OUTER JOIN (SELECT id AS uid FROM users WHERE zombie != 0) as q2 "
		"ON q1.uid = q2.uid")).one()[0]
	total = max(total, 1)

	return [int((vaxxed * 100) / total), int((zombie * 100) / total), vaxxed, zombie]

@cache.cached(make_cache_key=lambda:"emoji_count")
def emoji_count():
	return g.db.query(Emoji).filter_by(submitter_id=None).count()

@app.context_processor
def inject_constants():
	return {"environ":environ, "SITE":SITE, "SITE_NAME":SITE_NAME, "SITE_FULL":SITE_FULL,
			"AUTOJANNY_ID":AUTOJANNY_ID, "MODMAIL_ID":MODMAIL_ID, "VAPID_PUBLIC_KEY":VAPID_PUBLIC_KEY,
			"listdir":listdir, "os_path":path,
			"PIZZASHILL_ID":PIZZASHILL_ID, "DEFAULT_COLOR":DEFAULT_COLOR,
			"COLORS":COLORS, "time":time, "PERMS":PERMS, "FEATURES":FEATURES,
			"HOLE_REQUIRED":HOLE_REQUIRED,
			"DEFAULT_THEME":DEFAULT_THEME, "DESCRIPTION":DESCRIPTION,
			"has_sidebar":has_sidebar, "has_logo":has_logo,
			"FP":FP, "patron":patron, "get_setting": get_setting,
			"SIDEBAR_THREAD":SIDEBAR_THREAD, "BANNER_THREAD":BANNER_THREAD, "BUG_THREAD":BUG_THREAD,
			"BADGE_THREAD":BADGE_THREAD, "SNAPPY_THREAD":SNAPPY_THREAD, "CHANGELOG_THREAD":CHANGELOG_THREAD,
			"approved_embed_hosts":approved_embed_hosts, "POST_BODY_LENGTH_LIMIT":POST_BODY_LENGTH_LIMIT,
			"SITE_SETTINGS":get_settings(), "EMAIL":EMAIL, "max": max, "min": min, "can_see":can_see,
			"TELEGRAM_ID":TELEGRAM_ID, "TRUESCORE_MINIMUM":TRUESCORE_MINIMUM, "PROGSTACK_ID":PROGSTACK_ID,
			"DONATE_LINK":DONATE_LINK, "DONATE_SERVICE":DONATE_SERVICE,
			"HOUSE_JOIN_COST":HOUSE_JOIN_COST, "HOUSE_SWITCH_COST":HOUSE_SWITCH_COST, "IMAGE_FORMATS":','.join(IMAGE_FORMATS),
			"PAGE_SIZES":PAGE_SIZES, "THEMES":THEMES, "COMMENT_SORTS":COMMENT_SORTS, "POST_SORTS":POST_SORTS,
			"TIME_FILTERS":TIME_FILTERS, "HOUSES":HOUSES, "TIER_TO_NAME":TIER_TO_NAME,
			"DEFAULT_CONFIG_VALUE":DEFAULT_CONFIG_VALUE, "IS_LOCALHOST":IS_LOCALHOST, "BACKGROUND_CATEGORIES":BACKGROUND_CATEGORIES, "PAGE_SIZE":PAGE_SIZE, "TAGLINES":TAGLINES, "get_alt_graph":get_alt_graph, "current_registered_users":current_registered_users,
			"git_head":git_head, "max_days":max_days, "EMOJI_KINDS":EMOJI_KINDS,
			"BIO_FRIENDS_ENEMIES_LENGTH_LIMIT":BIO_FRIENDS_ENEMIES_LENGTH_LIMIT,
			"SITE_FULL_IMAGES": SITE_FULL_IMAGES,
			"IS_EVENT":IS_EVENT, "IS_FISTMAS":IS_FISTMAS, "IS_HOMOWEEN":IS_HOMOWEEN,
			"IS_DKD":IS_DKD, "IS_BIRTHGAY":IS_BIRTHGAY, "IS_BIRTHDEAD":IS_BIRTHDEAD,
			"CHUD_PHRASES":CHUD_PHRASES, "hasattr":hasattr, "calc_users":calc_users, "HOLE_INACTIVITY_DELETION":HOLE_INACTIVITY_DELETION, "LIGHT_THEMES":LIGHT_THEMES, "OVER_18_EMOJIS":OVER_18_EMOJIS,
			"MAX_IMAGE_AUDIO_SIZE_MB":MAX_IMAGE_AUDIO_SIZE_MB, "MAX_IMAGE_AUDIO_SIZE_MB_PATRON":MAX_IMAGE_AUDIO_SIZE_MB_PATRON,
			"MAX_VIDEO_SIZE_MB":MAX_VIDEO_SIZE_MB, "MAX_VIDEO_SIZE_MB_PATRON":MAX_VIDEO_SIZE_MB_PATRON,
			"CURSORMARSEY_DEFAULT":CURSORMARSEY_DEFAULT, "SNAPPY_ID":SNAPPY_ID, "get_running_orgy":get_running_orgy, "TRUESCORE_MINIMUM":TRUESCORE_MINIMUM, "bar_position":bar_position, "datetime":datetime, "CSS_LENGTH_LIMIT":CSS_LENGTH_LIMIT, "cache":cache, "emoji_count":emoji_count,
		}
