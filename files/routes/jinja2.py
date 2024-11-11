import time
import math
import datetime
import random

from os import environ, listdir, path

from flask import g, session, has_request_context, request
from jinja2 import pass_context
from PIL import ImageColor
from sqlalchemy import text, func

from files.classes.user import User
from files.classes.orgy import get_running_orgy
from files.classes.emoji import Emoji
from files.classes.group import Group
from files.helpers.assetcache import assetcache_path
from files.helpers.config.const import *
from files.helpers.const_stateful import *
from files.helpers.regex import *
from files.helpers.settings import *
from files.helpers.cloudflare import *
from files.helpers.sorting_and_time import make_age_string
from files.helpers.can_see import *
from files.helpers.alerts import send_notification
from files.helpers.useractions import *
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
	return f'{SITE_FULL_IMAGES}/i/{SITE_NAME}/{asset_path}?x=14'

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
	elif request.path.startswith('/shop/'):
		return 'shop'

	return 'home'

@app.template_filter("seeded_random")
def seeded_random(choices, p):
	choices = [x for x in choices if not x.startswith('.')]
	if request.path.startswith('/post/') and p:
		random.seed(p.id)
		chosen = random.choice(choices)
		random.seed()
		return chosen
	return random.choice(choices)

@app.template_filter("expand_art")
def expand_art(url):
	id = int(url.split('?')[0].split('/')[-1].replace('.webp', ''))
	if id < MIN_ART_ID_FOR_HQ: return url
	return f"{SITE_FULL_IMAGES}/asset_submissions/art/original/{id}.webp"

@app.template_filter("commas")
def commas_filter(number):
	return commas(number)

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

	vaxxed = g.db.execute(text("SELECT COUNT(*) FROM users WHERE zombie > 0")).one()[0]
	zombie = g.db.execute(text("SELECT COUNT(*) FROM users WHERE zombie < 0")).one()[0]
	total = g.db.execute(text("SELECT COUNT(*) FROM "
		"(SELECT DISTINCT ON (author_id) author_id AS uid FROM comments "
			f"WHERE created_utc > {t}) AS q1 "
		"FULL OUTER JOIN (SELECT id AS uid FROM users WHERE zombie != 0) as q2 "
		"ON q1.uid = q2.uid")).one()[0]
	total = max(total, 1)

	return [int((vaxxed * 100) / total), int((zombie * 100) / total), vaxxed, zombie]

@cache.cached(make_cache_key=lambda:"emoji_count", timeout=86400)
def emoji_count():
	return g.db.query(Emoji).filter_by(submitter_id=None).count()

@cache.cached(make_cache_key=lambda:"group_count", timeout=86400)
def group_count():
	return g.db.query(Group).count()

@cache.cached(make_cache_key=lambda:"user_count", timeout=86400)
def user_count():
	return g.db.query(User).count()

def top_poster_of_the_day():
	uid = cache.get("top_poster_of_the_day_id") or SNAPPY_ID
	user = g.db.query(User).filter_by(id=uid).one()
	return user


def HOLES():
	HOLES = [x[0] for x in g.db.query(Hole.name).filter_by(dead_utc=None).order_by(Hole.name)]
	if "other" in HOLES:
		HOLES.remove("other")
		HOLES.append("other")
	return HOLES
	

@app.context_processor
def inject_constants():
	return {
			"environ":environ, "SITE":SITE, "SITE_NAME":SITE_NAME, "SITE_FULL":SITE_FULL, "OTHER_SITE_NAME":OTHER_SITE_NAME,
			"AUTOJANNY_ID":AUTOJANNY_ID, "MODMAIL_ID":MODMAIL_ID, "VAPID_PUBLIC_KEY":VAPID_PUBLIC_KEY,
			"listdir":listdir, "os_path":path,
			"GTIX_ID":GTIX_ID, "DEFAULT_COLOR":DEFAULT_COLOR,
			"COLORS":COLORS, "time":time, "PERMS":PERMS, "FEATURES":FEATURES,
			"HOLE_REQUIRED":HOLE_REQUIRED,
			"DEFAULT_THEME":DEFAULT_THEME, "DESCRIPTION":DESCRIPTION,
			"has_sidebar":has_sidebar, "has_logo":has_logo,
			"patron":patron, "get_setting": get_setting,
			"BUG_THREAD":BUG_THREAD, "BADGE_THREAD":BADGE_THREAD, "SNAPPY_THREAD":SNAPPY_THREAD, "CHANGELOG_THREAD":CHANGELOG_THREAD,
			"SNAPPY_SUBMIT_THREAD":SNAPPY_SUBMIT_THREAD, "EMOJI_UPDATE_THREAD":EMOJI_UPDATE_THREAD, "EMOJI_COMMISSION_THREAD":EMOJI_COMMISSION_THREAD,
			"approved_embed_hosts":approved_embed_hosts, "POST_BODY_LENGTH_LIMIT":POST_BODY_LENGTH_LIMIT,
			"SITE_SETTINGS":get_settings(), "EMAIL":EMAIL, "max": max, "min": min, "can_see":can_see,
			"TELEGRAM_ID":TELEGRAM_ID, "TWITTER_ID":TWITTER_ID, "TRUESCORE_MINIMUM":TRUESCORE_MINIMUM,
			"DONATE_LINK":DONATE_LINK, "DONATE_SERVICE":DONATE_SERVICE, "PROGSTACK_ID":PROGSTACK_ID,
			"HOUSE_JOIN_COST":HOUSE_JOIN_COST, "HOUSE_SWITCH_COST":HOUSE_SWITCH_COST, "IMAGE_FORMATS":','.join(IMAGE_FORMATS),
			"PAGE_SIZES":PAGE_SIZES, "THEMES":THEMES, "COMMENT_SORTS":COMMENT_SORTS, "POST_SORTS":POST_SORTS,
			"TIME_FILTERS":TIME_FILTERS, "HOUSES":HOUSES, "TIER_TO_NAME":TIER_TO_NAME, "TIER_TO_MONEY":TIER_TO_MONEY,
			"DEFAULT_CONFIG_VALUE":DEFAULT_CONFIG_VALUE, "IS_LOCALHOST":IS_LOCALHOST, "BACKGROUND_CATEGORIES":BACKGROUND_CATEGORIES, "PAGE_SIZE":PAGE_SIZE, "TAGLINES":TAGLINES, "get_alt_graph":get_alt_graph, "current_registered_users":current_registered_users,
			"git_head":git_head, "max_days":max_days, "EMOJI_KINDS":EMOJI_KINDS,
			"BIO_FRIENDS_ENEMIES_LENGTH_LIMIT":BIO_FRIENDS_ENEMIES_LENGTH_LIMIT,
			"SITE_FULL_IMAGES": SITE_FULL_IMAGES,
			"IS_EVENT":IS_EVENT, "IS_MUSICAL_EVENT":IS_MUSICAL_EVENT, "IS_FISTMAS":IS_FISTMAS, "IS_HOMOWEEN":IS_HOMOWEEN,
			"IS_DKD":IS_DKD, "IS_BDAY":IS_BDAY, "IS_FOURTH":IS_FOURTH,
			"CHUD_PHRASES":CHUD_PHRASES, "hasattr":hasattr, "calc_users":calc_users, "HOLE_INACTIVITY_DEATH":HOLE_INACTIVITY_DEATH,
			"LIGHT_THEMES":LIGHT_THEMES, "DARK_THEMES":DARK_THEMES, "NSFW_EMOJIS":NSFW_EMOJIS, "HOLES":HOLES,
			"MAX_IMAGE_AUDIO_SIZE_MB":MAX_IMAGE_AUDIO_SIZE_MB, "MAX_IMAGE_AUDIO_SIZE_MB_PATRON":MAX_IMAGE_AUDIO_SIZE_MB_PATRON,
			"MAX_VIDEO_SIZE_MB":MAX_VIDEO_SIZE_MB, "MAX_VIDEO_SIZE_MB_PATRON":MAX_VIDEO_SIZE_MB_PATRON,
			"CURSORMARSEY_DEFAULT":CURSORMARSEY_DEFAULT, "SNAPPY_ID":SNAPPY_ID, "ZOZBOT_ID":ZOZBOT_ID, "get_running_orgy":get_running_orgy,
			"bar_position":bar_position, "datetime":datetime, "CSS_LENGTH_LIMIT":CSS_LENGTH_LIMIT, "cache":cache,
			"emoji_count":emoji_count, "group_count":group_count, "user_count":user_count,
			"HOLE_SIDEBAR_COLUMN_LENGTH":HOLE_SIDEBAR_COLUMN_LENGTH, "HOLE_SNAPPY_QUOTES_LENGTH":HOLE_SNAPPY_QUOTES_LENGTH, "USER_SNAPPY_QUOTES_LENGTH":USER_SNAPPY_QUOTES_LENGTH, "top_poster_of_the_day":top_poster_of_the_day,
			"CATEGORIES_ICONS":CATEGORIES_ICONS, "CATEGORIES_HOLES":CATEGORIES_HOLES,
			"HOLE_COST":HOLE_COST, "BAN_REASON_LENGTH_LIMIT":BAN_REASON_LENGTH_LIMIT,
		}
