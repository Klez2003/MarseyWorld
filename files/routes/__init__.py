# import constants then...
from files.helpers.config.const import *

# import flask then...
from flask import g, request, render_template, make_response, redirect, send_file

# import our app then...
from files.__main__ import app

# import route helpers then...
from files.routes.routehelpers import *

# import wrappers then...
from files.routes.wrappers import *

# import jinja2 then... (lmao this was in feeds.py before wtf)
from files.routes.jinja2 import *

# import routes :)
from .admin import *
from .comments import *
from .errors import *
from .reporting import *
from .front import *
from .login import *
from .mail import *
if get_setting('bots') :
	from .oauth import *
from .posts import *
from .search import *
from .settings import *
from .static import *
from .users import *
from .leaderboard import *
from .votes import *
from .feeds import *
if FEATURES['AWARDS']:
	from .awards import *
from .tenor import *
from .holes import *
if FEATURES['GAMBLING']:
	from .lottery import *
	from .casino import *
from .polls import *
from .notes import *
from .notifications import *
if FEATURES['HATS']:
	from .hats import *
if FEATURES['EMOJI_SUBMISSIONS'] or FEATURES['HAT_SUBMISSIONS']:
	from .asset_submissions import *
if FEATURES['ART_SUBMISSIONS']:
	from .art_submissions import *
from .special import *
from .push_notifs import *
if FEATURES['PING_GROUPS']:
	from .groups import *
from .chats import *

if IS_LOCALHOST:
	from sys import argv
	if "cron" not in argv and "load_chat" not in argv:
		from files.helpers.cron import cron_fn
		print('Starting cron tasks!', flush=True)
		gevent.spawn(cron_fn, True, False, False, False)
