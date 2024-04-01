from enum import Enum, auto
from os import environ, path

import tldextract
import datetime

DEFAULT_TIME_FILTER = "all"
DEFAULT_THEME = "midnight"
DEFAULT_COLOR = "805ad5"
CURSORMARSEY_DEFAULT = False
SPAM_URL_SIMILARITY_THRESHOLD = 0.1

SPAM_SIMILARITY_THRESHOLD = 0.5
SPAM_SIMILAR_COUNT_THRESHOLD = 10

COMMENT_SPAM_SIMILAR_THRESHOLD = 0.5
COMMENT_SPAM_COUNT_THRESHOLD = 10

DISABLE_DOWNVOTES = False
DESCRIPTION = "rdrama.net caters to drama in all forms such as: Real life, videos, photos, gossip, rumors, news sites, Reddit, and Beyond™. There isn't drama we won't touch, and we want it all!"
EMAIL = "rdrama@rdrama.net"
TELEGRAM_ID = ""
TWITTER_ID = ""

DEFAULT_CONFIG_VALUE = "blahblahblah"
SITE = environ.get("SITE").strip()
SITE_NAME = environ.get("SITE_NAME").strip()
SECRET_KEY = environ.get("SECRET_KEY").strip()
PROXY_URL = environ.get("PROXY_URL").strip()
LOG_DIRECTORY = environ.get("LOG_DIRECTORY")
SETTINGS_FILENAME = environ.get("SETTINGS_FILENAME")
GIPHY_KEY = environ.get("GIPHY_KEY").strip()
TURNSTILE_SITEKEY = environ.get("TURNSTILE_SITEKEY").strip()
TURNSTILE_SECRET = environ.get("TURNSTILE_SECRET").strip()
YOUTUBE_KEY = environ.get("YOUTUBE_KEY").strip()
VAPID_PUBLIC_KEY = environ.get("VAPID_PUBLIC_KEY").strip()
VAPID_PRIVATE_KEY = environ.get("VAPID_PRIVATE_KEY").strip()
CF_KEY = environ.get("CF_KEY").strip()
CF_ZONE = environ.get("CF_ZONE").strip()
blackjack = environ.get("BLACKJACK", "").strip()
PROGSTACK_MUL = float(environ.get("PROGSTACK_MUL", 2.0))
ENCOURAGED = environ.get("ENCOURAGED", "").strip().split()
ENCOURAGED2 = environ.get("ENCOURAGED2", "").strip().split()

DONATE_LINK = environ.get("DONATE_LINK").strip()

if DONATE_LINK == DEFAULT_CONFIG_VALUE:
	DONATE_SERVICE = DONATE_LINK
else:
	DONATE_SERVICE = tldextract.extract(DONATE_LINK).domain.capitalize()

class Service(Enum):
	RDRAMA = auto()
	CHAT = auto()

DEFAULT_RATELIMIT = "30/minute;200/hour;1000/day"
CASINO_RATELIMIT = "100/minute;5000/hour;20000/day"
DELETE_RATELIMIT = "10/minute;50/day"

PUSH_NOTIF_LIMIT = 1000

IS_LOCALHOST = SITE == "localhost" or SITE == "127.0.0.1" or SITE.startswith("192.168.") or SITE.endswith(".local")

if IS_LOCALHOST:
	SITE_FULL = 'http://' + SITE
	SITE_IMAGES = SITE
	SITE_FULL_IMAGES = f'http://{SITE_IMAGES}'
elif SITE in {'rdrama.net', 'watchpeopledie.tv'}:
	SITE_FULL = 'https://' + SITE
	SITE_IMAGES = 'i.' + SITE
	SITE_FULL_IMAGES = f'https://{SITE_IMAGES}'
else:
	SITE_FULL = 'https://' + SITE
	SITE_IMAGES = SITE
	SITE_FULL_IMAGES = SITE_FULL

if SITE == 'staging.rdrama.net':
	SITE_IMAGES = 'i.rdrama.net'
	SITE_FULL_IMAGES = f'https://{SITE_IMAGES}'

if SITE == 'rdrama.net':
	OTHER_SITE_NAME = 'WPD'
else:
	OTHER_SITE_NAME = 'rDrama'

LOGGED_IN_CACHE_KEY = "loggedin"
LOGGED_OUT_CACHE_KEY = "loggedout"

CASINO_RELEASE_DAY = 1662825600

CHUD_REPLACEMENTS = {
	' your ': " you're ",
	' to ': " too ",

	' Your ': " You're ",
	' To ': " Too ",

	' YOUR ': " YOU'RE ",
	' TO ': " TOO ",

	' am ': ' is ',
	' Am ': ' Is ',
	' AM ': ' IS ',

	'everyone': 'everypony',
	'everybody': 'everypony',

	'Everyone': 'Everypony',
	'Everybody': 'Everypony',

	'EVERYONE': 'EVERYPONY',
	'EVERYBODY': 'EVERYPONY',
}

GIRL_PHRASES = [
	"I just think it's funny that $",
	"ok so $",
	"um $",
	"also like $",
	"literally, $",
	"i feel like $",
	"my heart is telling me $",
	"omg! $",
	"im literally screaming, $",
	"$ and thats the tea, sis",
	"$ but go off i guess",
	"$ but go off",
	"$ but its whatever",
	"$ and its EVERYTHING",
	"$ *sips tea*",
	"$ PERIODT"
]

patron = "Patron"

OFFSITE_NOTIF_QUERIES = set()

if len(SITE_NAME) > 5:
	OFFSITE_NOTIF_QUERIES.add(SITE_NAME.lower())

if not IS_LOCALHOST:
	OFFSITE_NOTIF_QUERIES.add(SITE)

TAGLINES = ()

PERMS = { # Minimum admin_level to perform action.
	'HOLE_CREATE': 0,

	'POST_COMMENT_DISTINGUISH': 1,
	'POST_IN_GHOST_THREADS': 1,
	'VIEW_RESTRICTED_HOLES': 1,
	'BYPASS_SITE_READ_ONLY_MODE': 1,
	'BYPASS_UNDER_SIEGE_MODE': 1,
	'BYPASS_CHAT_TRUESCORE_REQUIREMENT': 1,
	'BYPASS_ANTISPAM_CHECKS': 1,
	'WARN_ON_FAILED_LOGIN': 1,
	'NOTIFICATIONS_SPECIFIC_WPD_COMMENTS': 1,
	'MESSAGE_BLOCKED_USERS': 1,
	'ADMIN_MOP_VISIBLE': 1,
	'ADMIN_HOME_VISIBLE': 1,
	'REPORTS_REMOVE': 1,
	'POST_COMMENT_MODERATION': 1,
	'USER_BAN': 1,
	'USER_SHADOWBAN': 1,
	'USER_CHUD': 1,
	'USER_MODERATION_TOOLS_VISIBLE': 1,
	'VIEW_MODMAIL': 1,
	'NOTIFICATIONS_MODMAIL': 1,
	'VIEW_PRIVATE_PROFILES': 1,
	'VIEW_ALTS': 1,
	'VIEW_ACTIVE_USERS': 1,
	'VIEW_ALT_VOTES': 1,
	'VIEW_LAST_ACTIVE': 1,
	'VIEW_VERSIONS': 1,
	'ENABLE_VOTE_BUTTONS_ON_USER_PAGE': 1,
	'NOTIFICATIONS_MODERATOR_ACTIONS': 1,
	'EXEMPT_FROM_IP_LOGGING': 1,
	'USER_BADGES': 1,
	'ADMIN_NOTES': 1,

	'IS_PERMA_PROGSTACKED': 2,
	'USER_LINK': 2,
	'USER_CHANGE_FLAIR': 2,
	'LOTTERY_VIEW_PARTICIPANTS': 2,
	'POST_COMMENT_INFINITE_PINGS': 2,
	'IGNORE_EDITING_LIMIT': 2,
	'ORGIES': 2,
	'POST_BETS': 2,
	'POST_BETS_DISTRIBUTE': 2,
	'DELETE_MEDIA': 2,

	'ADMIN_REMOVE': 3,
	'ADMIN_ACTIONS_REVERT': 3,
	'DOMAINS_BAN': 3,
	'EDIT_RULES': 3,
	'LOTTERY_ADMIN': 3,
	'SITE_SETTINGS': 3,
	'SITE_CACHE_PURGE_CDN': 3,
	'NOTIFICATIONS_FROM_SHADOWBANNED_USERS': 3,
	'USE_ADMIGGER_THREADS': 3,
	'MODERATE_PENDING_SUBMITTED_ASSETS': 3,
	'UPDATE_ASSETS': 3,
	'CHANGE_UNDER_SIEGE': 3,
	'VIEW_IPS': 3,
	'MARK_EFFORTPOST': 3,

	'PROGSTACK': 4,
	'UNDO_AWARD_PINS': 4,
	'ADMIN_ADD': 4,
	'USER_BLACKLIST': 4,
	'POST_COMMENT_EDITING': 4,
	'VIEW_PATRONS': 4,
	'BLACKJACK_NOTIFICATIONS': 4,
	'IGNORE_BADGE_BLACKLIST': 4,
	'ENABLE_DM_MEDIA': 4,
	'SEE_GHOST_VOTES': 4,
	'SITE_OFFLINE_MODE': 4,
	'IGNORE_DOMAIN_BAN': 4,
	'USER_RESET_PASSWORD': 4,
	'CLAIM_REWARDS_ALL_USERS': 4,
	'IGNORE_AWARD_IMMUNITY': 4,
	'INSERT_TRANSACTION': 4,
	'APPS_MODERATION': 4,

	'MODS_EVERY_HOLE': 5,
	'MODS_EVERY_GROUP': 5,
	'VIEW_EMAILS': 5,
	'VIEW_CHATS': 5,
	'INFINITE_CURRENCY': 5,
}

FEATURES = {
	'MARSEYBUX': True,
	'AWARDS': True,
	'CHAT': True,
	'PINS': True,
	'PRONOUNS': False,
	'BADGES': True,
	'HATS': True,
	'HOUSES': True,
	'GAMBLING': True,
	'USERS_PROFILE_BANNER': True,
	'USERS_PROFILE_BODYTEXT': True,
	'USERS_PROFILE_SONG': True,
	'USERS_PERMANENT_WORD_FILTERS': False,
	'USERS_SUICIDE': True,
	'MARKUP_COMMANDS': True,
	'REPOST_DETECTION': True,
	'PATRON_ICONS': False,
	'EMOJI_SUBMISSIONS': True,
	'HAT_SUBMISSIONS': True,
	'ART_SUBMISSIONS': True,
	'NSFW_MARKING': True,
	'PING_GROUPS': True,
	'IP_LOGGING': False,
	'BLOCK_MUTE_EXILE_EXPIRY': False,
}

if SITE_NAME == 'rDrama':
	FEATURES['BLOCK_MUTE_EXILE_EXPIRY'] = True

	CURSORMARSEY_DEFAULT = True
	DEFAULT_COLOR = "ff459a"

	patron = "Paypig"

	TAGLINES = (
		"largest cat pics site",
		"largest online LGBTQ+ club",
		"largest online furfest",
		"largest basket-weaving forum",
		"largest autism support group",
		"largest aztec heritage forum",
		"official George Soros fanclub",
		"CCP's official newspaper",
		"Nintendo gamers only",
		"donkey kong country",
		"as seen in WI v. Brooks 2022",
		"#1 used marsuit exchange",
		"incel matchmaking services",
		"AgainstHateSubreddits offsite",
		"exotic pets for sale",
		"cheap airfare and hotels",
		"the back page of the internet",
		"socialist discourse & dating",
		"DIY estrogen recipes",
		"#1 guide to transitioning in Texas",
		"erectile dysfunction treatments",
		"managing incontinence",
		"Quran study group",
		"Israeli Power Generator",
	)

	BOOSTED_HOLES = {
		'slackernews',
		'furry',
		'anime',
		'marsey',
		'againsthateholes',
		'vidya',
		'sports',
		'chinchilla',
		'museumofrdrama',
		'femaledatingstrategy',
		'meta',
		'countryclub',
		'lit',
		'highrollerclub',
		'love4fatpeople',
		'redscarepod',
		'gaybros',
		'equestria',
		'nerdshit',
		'transgender',
		'communism',
		'femme',
		'therapy',
		'atheism',
	}

	OFFSITE_NOTIF_QUERIES.update({'marsey', 'r/drama', 'justice4darrell', 'cringetopia.org'})

elif SITE_NAME == 'WPD':
	OFFSITE_NOTIF_QUERIES.update({'marsey', 'watchpeopledie', 'makemycoffin'})


LONGPOSTBOT_REPLIES = (
	"▼you're fucking bananas if you think I'm reading all that, take my downvote and shut up idiot",
	"Wow, you must be a JP fan.",
	"This is one of the worst posts I have EVER seen. Delete it.",
	"No, don't reply like this, please do another wall of unhinged rant please.",
	"# 😴😴😴",
	"Ma'am we've been over this before. You need to stop.",
	"I've known more coherent downies.",
	"Your pulitzer's in the mail",
	"That's great and all, but I asked for my burger without cheese.",
	"That degree finally paying off",
	"That's nice sweaty. Why don't you have a seat in the time out corner with Pizzashill until you calm down, then you can have your Capri Sun.",
	"All them words won't bring your pa back.",
	"You had a chance to not be completely worthless, but it looks like you threw it away. At least you're consistent.",
	"Some people are able to display their intelligence by going on at length on a subject and never actually saying anything. This ability is most common in trades such as politics, public relations, and law. You have impressed me by being able to best them all, while still coming off as an absolute idiot.",
	"You can type 10,000 characters and you decided that these were the one's that you wanted.",
	"Have you owned the libs yet?",
	"I don't know what you said, because I've seen another human naked.",
	"Impressive. Normally people with such severe developmental disabilities struggle to write much more than a sentence or two. He really has exceded our expectations for the writing portion. Sadly the coherency of his writing, along with his abilities in the social skills and reading portions, are far behind his peers with similar disabilities.",
	"This is a really long way of saying you don't fuck.",
	"Sorry ma'am, looks like his delusions have gotten worse. We'll have to admit him.",
	"If only you could put that energy into your relationships",
	"Posts like this is why I do Heroine.",
	"still unemployed then?",
	"K",
	"look im gunna have 2 ask u 2 keep ur giant dumps in the toilet not in my replys 😷😷😷",
	"Mommy is soooo proud of you, sweaty. Let's put this sperg out up on the fridge with all your other failures.",
	"Good job bobby, here's a star",
	"That was a mistake. You're about to find out the hard way why.",
	"You sat down and wrote all this shit. You could have done so many other things with your life. What happened to your life that made you decide writing novels of bullshit here was the best option?",
	"I don't have enough spoons to read this shit",
	"All those words won't bring daddy back.",
	"OUT!",
	"Damn, you're really mad over this, but thanks for the effort you put into typing that all out! Sadly I won't read it all.",
	"Jesse what the fuck are you talking about??",
	"Are you feeling okay bud?",
	":#marseywoah:",
	"At no point in your rambling, incoherent post were you even close to anything that could be considered a rational thought. Everyone on this site is now dumber for having read it. May God have mercy on your soul.",
	"https://rdrama.net/videos/1671169024815045.mp4",
	"https://i.rdrama.net/images/16766675896248007.webp",
	"https://i.rdrama.net/images/1683531328305875.webp",
	"https://i.rdrama.net/images/1691152552869678.webp",
	"You could have done crack instead of this shit",
	"Not one single person is gonna read all that",
	"PlsRope",
	"I hope you had chatgpt pen that one fam",
	"What?",
	":#didntreadlol:",
	":#bruh:",
	"https://i.rdrama.net/images/1701695785632276.webp",
	"https://i.rdrama.net/images/17019179012030876.webp",
	"https://i.rdrama.net/images/17035472185349927.webp",
	"https://i.rdrama.net/images/17050678429764252.webp",
	"https://i.rdrama.net/images/17025509830829637.webp",
	"kys",
	"Why?",
	"https://i.rdrama.net/images/17051203593367493.webp",
	"https://i.rdrama.net/images/17053964397685544.webp",
)

CHUD_MSGS = (
	"Hi @{username}, Your {type} has been automatically removed because you forgot to include `{CHUD_PHRASE}`. Don't worry, we're here to help! We won't let you post or comment anything that doesn't express your love and acceptance towards the trans community. Feel free to resubmit your comment with `{CHUD_PHRASE}` included. This is an automated message; if you need help, you can message us [here](/contact).",

	"Avast, ye scurvy cur! Yer {type} be walkin' the plank for forgettin' to include `{CHUD_PHRASE}`! We be helpin' ye, right enough - we'll ne'er let ye post or comment anythin' that doesn't be expressin' yer love an' acceptance o' minorities! Heave to an' resubmit yer {type} with `{CHUD_PHRASE}` included, or it'll be the deep six for ye, savvy? This be an automated message; if ye need help, ye can message us ['ere](/contact). Arrr!",

	"Hi @{username}, We're sorry to say that your {type} has been automatically removed because you forgot to include the phrase `{CHUD_PHRASE}`. Here at our church, we strongly believe that `{CHUD_PHRASE}` and we want to make sure that all of our members feel loved and accepted. If you'd like to resubmit your post, we would be more than happy to take a look at it. In the meantime, if you need any help or have any questions, please don't hesitate to [reach out to us](/contact). We're always here to help. Have a blessed day!",

	"Yo, Ya {type} got automatically removed cuz ya forgot ta include `{CHUD_PHRASE}`. Don't worry, we gotchu! We ain't gonna letcha post or comment nuttin' that don't express ya love and acceptance towards minorities. Feel free ta resubmit ya comment with `{CHUD_PHRASE}` included. This is an automated message; if ya need help, ya can message us [here](/contact).",

	"omg hi @{username}!!! okay so this is like super awkward omg but basically i had to remove ur {type} bc u didnt say `{CHUD_PHRASE}` lol. don't worry though, we like wont let you post anything that like doesnt have `{CHUD_PHRASE}` in it. anyways im like just a robot 😲 but if u want to talk 2 somebody you should do it [here](/contact) lol",

	"Hey sexy, why are you posting so quickly? 😊 You almost forgot to include `{CHUD_PHRASE}` in your {type} 😈. Slowww down and remember to post `{CHUD_PHRASE}` next time 😉 if that doesn't make sense [stop by](/contact) sometime and we can talk about it for a while 🥵",
)

PIN_AWARD_TEXT = " (pin award)"

LIGHT_THEMES = {"4chan","classic","coffee","light","win98"}
DARK_THEMES = {"classic_dark","dark","dramblr","midnight","tron"}
THEMES = ["4chan","classic","classic_dark","coffee","dark","dramblr","light","midnight","tron","win98"]
BACKGROUND_CATEGORIES = ["glitter", "anime", "fantasy", "solarpunk", "pixelart"]
PAGE_SIZES = (10, 25, 50, 100)

TIME_FILTERS = {
		"hour": "clock",
		"day": "calendar-day",
		"week": "calendar-week",
		"month": "calendar-alt",
		"year": "calendar",
		"all": "infinity",
	}
COMMENT_SORTS = {
		"hot": "fire",
		"new": "sparkles",
		"old": "book",
		"top": "arrow-alt-circle-up",
		"bottom": "arrow-alt-circle-down",
		"controversial": "bullhorn",
		"random": "random",
	}
POST_SORTS = COMMENT_SORTS | {
		"bump": "arrow-up",
		"comments": "comments",
		"views": "eye",
		"subscriptions": "bell",
		"saves": "save"
	}

################################################################################
### COLUMN INFO
################################################################################

HOLE_NAME_COLUMN_LENGTH = 25
HOLE_SIDEBAR_COLUMN_LENGTH = 10000
HOLE_SIDEBAR_HTML_COLUMN_LENGTH = 20000
HOLE_SNAPPY_QUOTES_LENGTH = 20000
HOLE_SIDEBAR_URL_COLUMN_LENGTH = 60
HOLE_BANNER_URL_COLUMN_LENGTH = 60
HOLE_MARSEY_URL_LENGTH = 60

################################################################################
### SITE SPECIFIC CONSTANTS
################################################################################

HOUSES = ["Furry","Femboy","Vampire","Racist","Edgy"]

WERKZEUG_ERROR_DESCRIPTIONS = {
	400: "The browser (or proxy) sent a request that this server could not understand.",
	401: "The server could not verify that you are authorized to access the URL requested. You either supplied the wrong credentials (e.g. a bad password), or your browser doesn't understand how to supply the credentials required.",
	403: "You don't have the permission to access the requested resource. It is either read-protected or not readable by the server.",
	404: "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.",
	405: "The method is not allowed for the requested URL.",
	409: "A conflict happened while processing the request. The resource might have been modified while the request was being processed.",
	410: "The requested URL is no longer available on this server and there is no forwarding address. If you followed a link from a foreign page, please contact the author of this page.",
	413: "The data value transmitted exceeds the capacity limit.",
	414: "The length of the requested URL exceeds the capacity limit for this server. The request cannot be processed.",
	415: "The server does not support the media type transmitted in the request.",
	417: "The server could not meet the requirements of the Expect header",
	418: "This server is a teapot, not a coffee machine",
	429: "This user has exceeded an allotted request count. Try again later.",
	500: "The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.",
}

ERROR_TITLES = {
	400: "Naughty Request",
	401: "🚫 Unauthorized 🚫",
	403: "Forbidden🙅‍♀️",
	404: "Not Found - where did it go?",
	405: "Method Not Allowed, BAD.",
	409: "Cumflict",
	410: "Gone... and Forgotten",
	413: "Gayload Too Large",
	415: "Weird Media Type",
	418: "I'm a teapot",
	429: "Too Many Requests",
	500: "Balls-Deep Server Error",
}

ERROR_MSGS = {
	400: "That request was bad and you should feel bad.",
	401: "What you're trying to do requires an account. I think. The original error message said something about a castle and I hated that. If you see this error and you're logged into an account, something went pretty wrong somewhere.",
	403: "YOU AREN'T WELCOME HERE GO AWAY",
	404: "Someone typed something wrong and it was probably you, please do better.",
	405: "idk how anyone gets this error but if you see this, remember to follow @carpathianflorist<br>the original error text here talked about internet gremlins and wtf",
	409: "There's a conflict between what you're trying to do and what you or someone else has done and because of that you can't do what you're trying to do. So maybe like... don't try and do that? Sorry not sorry",
	410: "You were too slow. The link FUCKING DIED. Request a new one and be more efficient.",
	413: "That's a heckin' chonker of a file! Please make it smaller or maybe like upload it somewhere else idk<BR>jc wrote this one hi jc!<br>- carp",
	415: "Please upload only Image, Video, or Audio files!",
	418: "this really shouldn't happen now that we autoconvert webm files but if it does there's a cool teapot marsey so there's that",
	429: "go spam somewhere else nerd",
	500: "Hiiiii it's carp! I think this error means that there's a timeout error. And I think that means something took too long to load so it decided not to work at all. If you keep seeing this on the same page <I>but not other pages</I>, then something is probably wrong with that specific function. It may not be called a function, but that sounds right to me. Anyway, <s>ping me and I'll whine to someone smarter to fix it. Don't bother them.</s> <B>After a year and a half of infuriating pings, the new instructions are to quit whining and just wait until it works again oh my god shut UP.</B><BR><BR> Thanks ily &lt;3",
}

ERROR_MARSEYS = {
	400: "marseybrainlet",
	401: "marseydead",
	403: "marseytroll",
	404: "marseyconfused",
	405: "marseyretard",
	409: "marseynoyou",
	410: "marseyrave",
	413: "marseychonker2",
	415: "marseydetective",
	418: "marseytea",
	429: "marseyrentfree",
	500: "marseycarp3",
}

EMOJI_SRCS = ['files/assets/emojis.csv']

PIN_LIMIT = 3
POST_TITLE_LENGTH_LIMIT = 500 # do not make larger than 500 without altering the table
POST_TITLE_HTML_LENGTH_LIMIT = 1500 # do not make larger than 1500 without altering the table

def POST_BODY_LENGTH_LIMIT(v):
	if v.patron: return 100000
	return 50000

POST_BODY_HTML_LENGTH_LIMIT = 200000 # do not make larger than 200000 without altering the table

COMMENT_BODY_LENGTH_LIMIT = 10000 # do not make larger than 10000 characters without altering the table
COMMENT_BODY_HTML_LENGTH_LIMIT = 40000 # do not make larger than 20000 characters without altering the table
CSS_LENGTH_LIMIT = 20000 # do not make larger than 20000 characters without altering the tables
COMMENT_MAX_DEPTH = 200
TRANSFER_MESSAGE_LENGTH_LIMIT = 200 # do not make larger than 10000 characters (comment limit) without altering the table
MIN_REPOST_CHECK_URL_LENGTH = 9 # also change the constant in checkRepost() of submit.js
CHAT_LENGTH_LIMIT = 1000
HOLE_BANNER_LIMIT = 10

BIO_FRIENDS_ENEMIES_LENGTH_LIMIT = 5000 # do not make larger than 5000 characters without altering the table
BIO_FRIENDS_ENEMIES_HTML_LENGTH_LIMIT = 20000 # do not make larger than 20000 characters without altering the table

COSMETIC_AWARD_COIN_AWARD_PCT = 0.50

TRUESCORE_MINIMUM = 0
TRUESCORE_DONATE_MINIMUM = 1

LOGGEDIN_ACTIVE_TIME = 15 * 60
PFP_DEFAULT_MARSEY = True
NEW_USER_AGE = 7 * 86400
NOTIFICATION_SPAM_AGE_THRESHOLD = 0
COMMENT_SPAM_LENGTH_THRESHOLD = 0

DEFAULT_UNDER_SIEGE_THRESHOLDS = {
	"private chat": 0,
	"chat": 0,
	"normal comment": 0,
	"wall comment": 0,
	"post": 0,
	"report": 0,
	"modmail": 0,
	"message": 0,
}

HOLE_REQUIRED = False
HOLE_COST = 0
GROUP_COST = 10000
HOLE_INACTIVITY_DELETION = False

BOT_SYMBOL_HIDDEN = set()
ANTISPAM_BYPASS_IDS = set()

AUTOJANNY_ID = 1
SNAPPY_ID = 2
LONGPOSTBOT_ID = 3
ZOZBOT_ID = 4

PIZZASHILL_ID = 0
CARP_ID = 0
AEVANN_ID = 0
GTIX_ID = 0

CURRENCY_TRANSFER_ID = 5

IMMUNE_TO_NEGATIVE_AWARDS = {}
EXEMPT_FROM_EDITING_LIMIT = {}
PINNED_POSTS_IDS = {}

MODMAIL_ID = 2
PROGSTACK_ID = 4

POLL_BET_COINS = 200
POLL_MAX_OPTIONS = 200
WELCOME_MSG = f"Welcome to {SITE_NAME}!"

LOTTERY_TICKET_COST = 12
LOTTERY_SINK_RATE = 3
LOTTERY_DURATION = 60 * 60 * 24 * 7

BUG_THREAD = 0

BADGE_THREAD = 0
SNAPPY_THREAD = 0
CHANGELOG_THREAD = 0
POLL_THREAD = 0
ADMIGGER_THREADS = {BADGE_THREAD, SNAPPY_THREAD, CHANGELOG_THREAD, POLL_THREAD}

MAX_IMAGE_SIZE_BANNER_RESIZED_MB = 2
MAX_IMAGE_AUDIO_SIZE_MB = 8
MAX_IMAGE_AUDIO_SIZE_MB_PATRON = 16
MAX_VIDEO_SIZE_MB = 32
MAX_VIDEO_SIZE_MB_PATRON = 100

PAGE_SIZE = 25
LEADERBOARD_LIMIT = PAGE_SIZE

HOUSE_JOIN_COST = 500
HOUSE_SWITCH_COST = 2000

PATRON_BADGES = {22,23,24,25,26,27,28,257,258,259,260,261}

TIER_TO_NAME = {
	1: "Beneficiary",
	2: "Paypig",
	3: "Renthog",
	4: "Landchad",
	5: "Terminally online turboautist",
	6: "Marsey's Sugar Daddy",
	7: "JIDF Bankroller",
	8: "Rich Bich",
}

TIER_TO_MONEY = {
	2: 5,
	3: 10,
	4: 20,
	5: 50,
	6: 100,
	7: 200,
	8: 500,
}

BADGE_BLACKLIST = { # only grantable by admins higher than PERMS['IGNORE_BADGE_BLACKLIST']
	1, 2, 6, 10, 11, 12, # Alpha, Verified Email, Beta, Recruiter x3
	16, 17, 143, 21, 22, 23, 24, 25, 26, 27, # Marsey Artist x3 / Patron Tiers
	94, 95, 96, 97, 98, 109, 67, 68, 83, 84, 87, 90, 179, 185, # Award Status except Y'all-seeing eye
	137, # Lottery Winner
}

if SITE in {'rdrama.net', 'staging.rdrama.net'}:
	NOTIFICATION_SPAM_AGE_THRESHOLD = 0.5 * 86400

	TELEGRAM_ID = "rdramanet"
	TWITTER_ID = "rdramanet"
	DEFAULT_TIME_FILTER = "day"

	FEATURES['PRONOUNS'] = True
	FEATURES['USERS_PERMANENT_WORD_FILTERS'] = True

	PERMS['VIEW_VERSIONS'] = 5

	BUG_THREAD = 18459

	BADGE_THREAD = 37833
	SNAPPY_THREAD = 37749
	CHANGELOG_THREAD = 165657
	POLL_THREAD = 79285
	ADMIGGER_THREADS = {BADGE_THREAD, SNAPPY_THREAD, CHANGELOG_THREAD, POLL_THREAD, 166300, 187078}

	TRUESCORE_MINIMUM = 10

	HOLE_COST = 50000
	HOLE_INACTIVITY_DELETION = True

	BOT_SYMBOL_HIDDEN = {12125, 16049, 23576}
	ANTISPAM_BYPASS_IDS = BOT_SYMBOL_HIDDEN | {1703, 13427, 15014, 24197, 25816}

	EXEMPT_FROM_EDITING_LIMIT = {1048}

	AUTOJANNY_ID = 1046
	SNAPPY_ID = 261
	LONGPOSTBOT_ID = 1832
	ZOZBOT_ID = 1833

	PIZZASHILL_ID = 2424
	PROGSTACK_ID = 15531
	CARP_ID = 995
	AEVANN_ID = 1

	CURRENCY_TRANSFER_ID = CARP_ID

	IMMUNE_TO_NEGATIVE_AWARDS = {PIZZASHILL_ID, CARP_ID, 23629}

	PINNED_POSTS_IDS = {
		PIZZASHILL_ID: 1,
		28: 1, #Joan_Wayne_Gacy
		10953: 1, #autodrama
		864: 1, #RitalinRx
		1096: 1, #xa15428
		1357: 1, #_______________
		2008: 1, #transgirltradwife
		4999: 1, #justcool393
		8491: 1, #TrappySaruh
		12451: 1, #rosemulet
		13452: 1, #Sammael-Beliol
		16012: 1, #realspez
		18308: 1, #gee891
		24456: 1, #PreyingMantits
		3336: 24, #Snally
	}

	WELCOME_MSG = f"Hi there! It's me, your soon-to-be favorite rDrama user @carpathianflorist here to give you a brief rundown on some of the sick features we have here. You'll probably want to start by following me, though. So go ahead and click my name and then smash that Follow button. This is actually really important, so go on. Hurry.\n\nThanks!\n\nNext up: If you're a member of the media, similarly just shoot me a DM and I'll set about verifying you and then we can take care of your sad journalism stuff.\n\n**FOR EVERYONE ELSE**\n\n Begin by navigating to [the settings page](/settings/personal) (we'll be prettying this up so it's less convoluted soon, don't worry) and getting some basic customization done.\n\n### Themes\n\nDefinitely change your theme right away, the default one (Midnight) is pretty enough, but why not use something *exotic* like Win98, or *flashy* like Tron? Even Coffee is super tasteful and way more fun than the default. More themes to come when we get around to it!\n\n### Avatar/pfp\n\nYou'll want to set this pretty soon. Set the banner too while you're at it. Your profile is important!\n\n### Flairs\n\nSince you're already on the settings page, you may as well set a flair, too. As with your username, you can - obviously - choose the color of this, either with a hex value or just from the preset colors. And also like your username, you can change this at any time. Paypigs can even further relive the glory days of 90s-00s internet and set obnoxious signatures.\n\n### PROFILE ANTHEMS\n\nSpeaking of profiles, hey, remember MySpace? Do you miss autoplaying music assaulting your ears every time you visited a friend's page? Yeah, we brought that back. Enter a YouTube URL, wait a few seconds for it to process, and then BAM! you've got a profile anthem which people cannot mute. Unless they spend 20,000 dramacoin in the shop for a mute button. Which you can then remove from your profile by spending 40,000 dramacoin on an unmuteable anthem. Get fucked poors!\n\n### Dramacoin?\n\nDramacoin is basically our take on the karma system. Except unlike the karma system, it's not gay and boring and stupid and useless. Dramacoin can be spent at [Marsey's Dramacoin Emporium](/shop/awards) on upgrades to your user experience (many more coming than what's already listed there), and best of all on tremendously annoying awards to fuck with your fellow dramautists. We're always adding more, so check back regularly in case you happen to miss one of the announcement posts.\n\nLike karma, dramacoin is obtained by getting upvotes on your threads and comments. *Unlike* karma, it's also obtained by getting downvotes on your threads and comments. Downvotes don't really do anything here - they pay the same amount of dramacoin and they increase thread/comment ranking just the same as an upvote. You just use them to express petty disapproval and hopefully start a fight. Because all votes are visible here. To hell with your anonymity.\n\nDramacoin can also be traded amongst users from their profiles. Note that there is a 3% transaction fee.\n\n### Badges\n\nRemember all those neat little metallic icons you saw on my profile when you were following me? If not, scroll back up and go have a look. And doublecheck to make sure you pressed the Follow button. Anyway, those are badges. You earn them by doing a variety of things. Some of them even offer benefits, like discounts at the shop. A [complete list of badges and their requirements can be found here](/badges), though I add more pretty regularly, so keep an eye on the [changelog](/post/{CHANGELOG_THREAD}).\n\n### Other stuff\n\nWe're always adding new features, and we take a fun-first approach to development. If you have a suggestion for something that would be fun, funny, annoying - or best of all, some combination of all three - definitely make a thread about it. Or just DM me if you're shy. Weirdo. Anyway there's also the [leaderboards](/leaderboard), boring stuff like two-factor authentication you can toggle on somewhere in the settings page (psycho), the ability to save posts and comments, more than a thousand emojis already (most of which are rDrama originals), and on and on and on and on. This is just the basics, mostly to help you get acquainted with some of the things you can do here to make it more easy on the eyes, customizable, and enjoyable. If you don't enjoy it, just go away! We're not changing things to suit you! Get out of here loser! And no, you can't delete your account :na:\n\nI love you.<br>*xoxo Carp* 💋"

	USER_IDS = (1,4,28,29,35,37,69,71,74,110,114,147,148,151,152,154,192,197,199,202,205,207,247,249,250,253,256,257,259,260,294,295,296,334,335,339,341,374,378,381,417,421,422,498,535,536,542,556,557,560,597,635,637,661,708,746,748,749,751,759,761,762,763,764,768,777,780,781,817,819,824,828,842,847,850,854,868,876,880,881,888,967,968,986,988,992,995,1042,1048,1054,1057,1066,1067,1069,1087,1092,1094,1096,1101,1103,1104,1106,1109,1110,1116,1190,1191,1201,1202,1203,1206,1211,1219,1225,1230,1232,1269,1351,1357,1361,1365,1372,1376,1378,1379,1381,1385,1386,1387,1395,1404,1412,1413,1428,1444,1445,1451,1456,1458,1461,1472,1475,1476,1479,1481,1488,1489,1493,1688,1691,1697,1703,1708,1722,1730,1738,1740,1743,1744,1747,1748,1752,1756,1757,1758,1784,1794,1817,1821,1827,1828,1830,1834,1839,1843,1850,1852,1866,1881,1885,1888,1894,1900,1901,1903,1925,1933,1948,1949,1950,1951,1956,1963,1977,1980,1985,1987,1990,1993,1994,1995,2001,2008,2009,2029,2050,2053,2065,2069,2078,2081,2092,2109,2113,2121,2133,2139,2157,2158,2160,2191,2210,2219,2235,2238,2249,2250,2256,2258,2273,2277,2292,2294,2318,2324,2329,2370,2375,2385,2393,2399,2402,2407,2410,2411,2412,2424,2432,2433,2435,2443,2446,2453,2455,2462,2468,2470,2474,2481,2490,2500,2504,2512,2523,2525,2526,2529,2531,2532,2537,2545,2546,2548,2554,2570,2571,2573,2582,2588,2597,2608,2618,2620,2622,2626,2628,2636,2641,2651,2654,2670,2673,2679,2707,2711,2712,2714,2720,2734,2737,2739,2748,2764,2788,2790,2807,2810,2818,2822,2826,2851,2858,2863,2867,2875,2879,2890,2896,2899,2907,2915,2930,2936,2954,2960,2962,2963,2974,2976,2980,2982,3006,3016,3018,3021,3024,3029,3039,3056,3060,3067,3071,3078,3082,3085,3092,3108,3119,3122,3125,3127,3131,3138,3141,3149,3162,3165,3180,3196,3206,3211,3227,3232,3239,3241,3247,3257,3259,3277,3288,3301,3310,3322,3335,3336,3360,3368,3370,3377,3393,3400,3402,3417,3419,3432,3435,3450,3491,3495,3496,3511,3523,3526,3528,3536,3555,3560,3586,3593,3594,3595,3599,3609,3620,3631,3633,3635,3636,3638,3639,3646,3655,3660,3661,3664,3667,3677,3680,3684,3686,3690,3702,3717,3727,3728,3735,3739,3748,3750,3756,3758,3761,3775,3776,3779,3783,3786,3787,3788,3790,3798,3853,3869,3870,3888,3908,3921,3936,3938,3940,3948,3955,3960,3962,3968,3971,3972,3982,3987,3992,3998,4003,4017,4037,4039,4043,4058,4074,4084,4088,4096,4098,4118,4128,4136,4154,4171,4218,4229,4233,4236,4238,4243,4246,4260,4267,4270,4272,4276,4284,4293,4304,4309,4324,4328,4338,4353,4357,4358,4368,4387,4394,4403,4413,4429,4450,4451,4480,4483,4484,4533,4545,4565,4573,4574,4575,4582,4596,4601,4616,4632,4634,4647,4650,4658,4659,4660,4690,4733,4738,4740,4752,4763,4770,4795,4817,4834,4837,4842,4845,4885,4894,4896,4928,4951,4959,4966,4972,4988,5019,5036,5039,5042,5046,5069,5071,5073,5101,5160,5166,5168,5179,5183,5188,5192,5193,5200,5203,5211,5212,5214,5244,5246,5263,5291,5311,5338,5353,5356,5374,5381,5414,5418,5428,5438,5462,5468,5491,5499,5502,5504,5526,5534,5594,5606,5646,5647,5653,5663,5670,5678,5707,5715,5723,5734,5763,5771,5772,5773,5781,5800,5802,5804,5814,5815,5827,5841,5845,5859,5861,5870,5876,5893,5897,5919,5933,5945,5946,5970,5988,6028,6033,6050,6056,6076,6113,6149,6208,6213,6218,6225,6232,6242,6265,6274,6284,6286,6289,6348,6376,6380,6387,6404,6408,6420,6460,6461,6500,6504,6505,6546,6564,6565,6570,6588,6593,6596,6598,6606,6611,6668,6672,6811,6840,6862,6864,6865,6869,6873,6881,6887,6894,6924,6933,6934,6971,6996,7005,7015,7098,7117,7120,7142,7182,7183,7207,7225,7236,7261,7322,7392,7411,7435,7447,7453,7465,7466,7472,7525,7555,7556,7580,7609,7614,7641,7645,7659,7701,7706,7708,7732,7766,7768,7772,7780,7785,7794,7796,7817,7825,7828,7896,7903,7912,7913,7943,7947,7971,8021,8037,8044,8092,8094,8159,8175,8193,8197,8206,8214,8218,8226,8292,8376,8435,8463,8516,8518,8530,8538,8667,8732,8748,8752,8768,8779,8799,8824,8880,8903,8924,8946,8950,8956,8971,8982,8993,9037,9038,9052,9066,9069,9070,9135,9140,9142,9151,9168,9173,9177,9179,9288,9313,9358,9374,9394,9397,9450,9451,9460,9478,9485,9493,9498,9509,9514,9539,9555,9556,9559,9578,9582,9632,9653,9755,9787,9841,9856,9873,9874,9910,9914,9920,9952,9954,9978,9995,10076,10103,10113,10187,10198,10209,10211,10214,10232,10235,10305,10321,10336,10384,10434,10437,10477,10489,10553,10566,10626,10630,10642,10654,10666,10667,10682,10696,10698,10706,10734,10780,10865,10867,10936,10947,10953,10998,11023,11031,11034,11112,11143,11158,11168,11197,11200,11223,11232,11245,11320,11414,11418,11441,11447,11485,11489,11535,11615,11630,11660,11666,11674,11772,11773,11826,11852,11900,11928,11942,11958,11963,11988,12063,12078,12086,12097,12102,12142,12221,12225,12240,12276,12280,12362,12386,12395,12413,12461,12480,12486,12497,12527,12677,12692,12719,12733,12793,12794,12809,12891,12909,12942,12950,12966,12973,12980,12985,12987,12989,13003,13015,13052,13098,13108,13122,13138,13166,13179,13199,13274,13319,13352,13362,13455,13477,13481,13604,13609,13634,13736,13781,13797,13813,13840,13897,13918,13922,13926,13929,13942,13972,14052,14098,14144,14163,14203,14223,14251,14278,14287,14305,14376,14378,14385,14400,14443,14569,14577,14594,14607,14690,14699,14778,14788,14789,14800,14853,14920,14924,14927,15004,15014,15017,15029,15055,15067,15095,15118,15135,15153,15195,15222,15295,15299,15319,15342,15355,15370,15377,15412,15418,15464,15497,15506,15567,15656,15716,15753,15805,15865,15869,15872,15878,15896,15920,15932,15939,15943,16001,16038,16049,16067,16123,16125,16131,16547,16563,16583,16592,16613,16671,16688,16714,16871,16913,16936,16945,16958,16959,17043,17071,17141,17171,17172,17178,17181,17184,17258,17327,17399,17561,17592,17608,17792,17859,17923,17956,18028,18044,18047,18048,18049,18052,18053,18062,18091,18119,18124,18132,18165,18214,18252,18278,18286,18339,18358,18370,18470,18486,18646,18670,18720,18727,18809,18851,19099,19191,19226,19231,19280,19378,19464,19630,19700,19714,19837,19915,19939,19953,19982,20120,20387,20425,20481,20619,21011,21034,21085,21122,21167,21206,21238,21253,21254,21263,21264,21288,21291,21305,21317,21321,21336,21363,21379,21387,21436,21449,21451,21456,21616,21632,21698,21739,21743,21756,21757,21762,21774,21806,21822,21826,21829,21919,21950,21966,22054,22089,22109,22163,22233,22248,22272,22291,22299,22330,22389,22408,22445,22479,22674,22740,22752,22771,22972,22987,23042,23061,23075,23083,23088,23101,23176,23197,23282,23432,23453,23483,23562,23602,23625,23627,23703,23793,23829,23889,23996,24031,24102,24162,24208,24265,24281,24506,24508,24525,24582,24586,24599,24665,24669,24804,24806,24890,24943,25035,25187,25207,25247,25621,25755,25790,25816,25935,25941,26003,26033,26043,26055,26243,26534,26561,26591,26691)
elif SITE in {'watchpeopledie.tv', 'marsey.world'}:
	NOTIFICATION_SPAM_AGE_THRESHOLD = 0.5 * 86400
	TRUESCORE_MINIMUM = 100

	EMAIL = "wpd@watchpeopledie.tv"
	TELEGRAM_ID = "wpdtv"
	TWITTER_ID = "wpd__tv"
	DEFAULT_TIME_FILTER = "day"

	DESCRIPTION = "People die and this is the place to see it. You only have one life, don't make the mistakes seen here."

	PIN_LIMIT = 4
	WELCOME_MSG = """Hi, you! Welcome to WatchPeopleDie.tv, this really cool site where you can go to watch people die. I'm @G-tix! If you have any questions about how things work here, or suggestions on how to make them work better than they already do, definitely slide on into my DMs (fat chicks only 🥵).\n\nThere's an enormously robust suite of fun features we have here and we're always looking for more to add. Way, way too many to go over in an automated welcome message. And you're probably here for the videos of people dying more than any sort of weird, paradoxical digital community aspect anyway, so I won't bore you with a tedious overview of them. Just head on over to [your settings page](/settings/personal) and have a look at some of the basic profile stuff, at least. You can change your profile picture, username, flair, colors, banners, bio, profile anthem (autoplaying song on your page, like it's MySpace or some shit, hell yeah), CSS, all sorts of things.\n\nOr you can just go back to the main feed and carry on with watching people die. That's what the site is for, after all. Have fun!\n\nAnyway, in closing, WPD is entirely open source. We don't really need new full-time coders or anything, but if you'd like to take a look at our repo - or even submit a PR to change, fix, or add some things - go right ahead! Our codebase lives at https://fsdfsd.net/rDrama/rDrama\n\nWell, that's all. Thanks again for signing up. It's an automated message and all, but I really do mean that. Thank you, specifically. I love you. Romantically. Deeply. Passionately.\n\nHave fun!\n\nNote: There's more info about the site and how to use it here: https://watchpeopledie.tv/post/122529"""

	FEATURES['PATRON_ICONS'] = True
	FEATURES['NSFW_MARKING'] = False
	FEATURES['HAT_SUBMISSIONS'] = False
	FEATURES['IP_LOGGING'] = True
	HOUSES = ["Furry","Femboy","Vampire","Edgy"]

	HOLE_BANNER_LIMIT = 69420

	ERROR_TITLES.update({
		400: "Bad Request",
		401: "Unauthorized",
		403: "Forbidden",
		404: "Not Found",
		405: "Method Not Allowed",
		409: "Conflict",
		410: "Gone",
		413: "Payload Too Large",
		415: "Unsupported Media Type",
		500: "Internal Server Error",
	})

	ERROR_MSGS = {
		400: "That request is invalid.",
		401: "You need to login or sign up to do that.",
		403: "You're not allowed to do that",
		404: "That wasn't found.",
		405: "You can't use this method here... if you keep getting this error tell us it's prolly something borked.",
		409: "There's a conflict between what you're trying to do and what you or someone else has done and because of that you can't do what you're trying to do.",
		410: "This link is dead. Request a new one to try again.",
		413: "You need to upload a smaller file please.",
		415: "Please upload only Image, Video, or Audio files!",
		418: "this really shouldn't happen now that we autoconvert webm files but if it does there's a cool teapot marsey so there's that",
		429: "Please wait a bit before doing that.",
		500: "Internal Server Error. Something went very wrong when trying to fulfill your request. Try refreshing the page. If it still doesn't work, shoot <a href='/@G-tix'>@G-tix</a> a message.",
	}

	ERROR_MARSEYS[403] = "marseyconfused"
	ERROR_MARSEYS[500] = "marseylaptopangry2"

	BUG_THREAD = 61549

	BADGE_THREAD = 52519
	SNAPPY_THREAD = 67186
	CHANGELOG_THREAD = 56363
	POLL_THREAD = 22937
	ADMIGGER_THREADS = {BADGE_THREAD, SNAPPY_THREAD, CHANGELOG_THREAD, POLL_THREAD, 106665}

	MAX_VIDEO_SIZE_MB = 500
	MAX_VIDEO_SIZE_MB_PATRON = 500

	HOLE_REQUIRED = True

	AUTOJANNY_ID = 1
	SNAPPY_ID = 3
	LONGPOSTBOT_ID = 0
	ZOZBOT_ID = 5

	AEVANN_ID = 9
	GTIX_ID = 77694

	CURRENCY_TRANSFER_ID = 48
	ANTISPAM_BYPASS_IDS = {1718156}

	TIER_TO_NAME = {
		1: "Beneficiary",
		2: "Victim",
		3: "Corpse",
		4: "Zombie",
		5: "Ghost",
		6: "Survivor",
		7: "Jigsaw",
		8: "P̵͇̕S̶̔̇Ȳ̴͙C̶͋͗H̵͒̉O̴̎̍ ",
	}

	DEFAULT_UNDER_SIEGE_THRESHOLDS = {
		"private chat": 1440,
		"chat": 1440,
		"normal comment": 10,
		"wall comment": 1440,
		"post": 1440,
		"report": 1440,
		"modmail": 1440,
		"message": 1440,
	}

	USER_IDS = (77655,77694,77964,78263,78398,78581,78967,79165,79461,79506,79955,80351,81601,81957,82175,82248,82476,82620,82812,83211,83378,83577,83582,83848,84126,84227,84500,84742,84766,84774,85169,86478,86528,86570,86640,86726,86809,86889,86905,86919,86929,86930,87086,87098,87213,87252,87441,87511,87671,87761,87767,87822,87848,88021,88159,88286,88570,88718,88749,88841,88920,88968,89221,89336,89447,89718,89965,90059,90087,90189,90744,90816,90861,91307,91343,91353,91979,92128,92279,92981,93345,93600,93741,94013,94389,94423,94646,95209,95217,95759,95925,95990,96091,96296,96315,96677,97100,97124,97866,97980,98249,98771,99366,99582,100142,100251,100548,100723,101205,101359,101412,101533,101701,101871,101998,102158,102284,102389,102531,103479,104305,106484,107204,107335,108547,109971,110033,111906,115130,115513,115735,120759,120955,121021,123221,123942,124328,124677,126800,130650,130700,133034,133132,133299,134520,137886,138214,138271,138373,141054,141538,141665,142293,142351,144125,144422,144481,144720,144734,146101,146808,148061,148107,148115,148546,148785,148819,149125,149397,149400,149554,149680,149845,149982,149989,150062,150075,150366,150429,150547,151095,151189,151256,151782,151892,152264,152300,152519,152704,153218,153589,153774,153853,154142,154311,154457,154720,154724,154935,154944,154995,155014,155449,155464,155498,155524,155594,155684,156135,156301,156382,156416,156417,156618,156881,156909,156989,157371,157441,157487,157546,157989,157990,158297,158356,158434,158745,159037,159052,159085,159144,159401,159641,159853,160298,160330,160601,160978,161296,162164,163216,163303,163468,164194,164350,164559,164781,165264,165333,165593,165728,165977,166150,166369,166371,166800,166923,167053,167098,167110,167340,167411,167487,167687,167810,167992,168046,168515,168742,168747,168771,169369,169424,169461,169541,169684,170163,170220,170378,170402,170517,170561,170626,170712,171182,171243,171310,171659,171950,172271,172854,172939,172941,173188,173205,173342,173520,173600,174291,174618,174652,174903,175055,175486,175527,175718,175946,175966,176176,176442,176487,176604,176620,176758,176969,177510,177575,177602,177919,178164,178439,178587,178608,180323,180417,180456,180686,180801,180917,181554,181571,182410,182646,182770,184624,184695,184896,185764,186198,187233,187385,187897,187908,188687,189573,189779,190343,190669,190904,190906,191229,191382,191499,191545,191869,192146,193369,194451,194541,195656,195936,195945,196143,196472,197717,198608,199149,200216,200736,201297,201442,201633,201894,203819,203828,204063,204517,204773,204975,205054,205175,205561,205606,205635,206181,206274,206296,206359,206579,206726,206827,206925,206946,207127,207194,207262,207291,207567,208081,208165,208508,208564,208701,208980,209691,209882,210371,210412,210552,210683,210810,211054,211177,211248,211250,211320,211458,211578,211637,211757,211921,212040,212082,212107,212225,212511,213716,213765,214155,214662,214688,214901,215127,215282,215388,215461,216431,216840,217321,217351,217608,218221,218917,219324,219775,220082,220905,220966,221124,222171,222198,222287,222505,222735,225994,226764,226881,226932,228711,228986,229282,229605,229933,230048,230105,230223,230338,231011,231018,231060,231074,231113,231193,231446,231651,231780,232046,233143,233164,233390,234359,234932,235267,235403,235436,235490,235743,236154,236452,236630,236722,236995,237044,237161,237301,237323,238650,239052,239533,239623,239709,240695,241353,241486,241895,241938,242153,242370,243070,243307,243405,243666,243697,243949,244267,244826,245531,245660,246127,246211,246372,246496,247188,247846,247873,247963,248723,248746,249179,249779,250283,250311,250336,250452,251727,251861,252255,252285,253307,253309,254461,255968,256421,257670,258702,259175,259984,260375,261437,261882,264695,265067,265723,267286,267488,270044,270217,270538,270985,271229,272144,273228,273266,273391,273631,273875,278751,279116,279262,279337,279755,279986,282253,283010,285862,286561,287958,288197,291822,293479,293527,294824,296089,296156,296217,296683,296926,297142,297404,297424,297689,298413,298474,298678,298874,298976,298986,299277,299303,299659,299954,300096,300172,300431,300536,300823,300829,300870,301994,302150,302347,302952,303831,304172,304269,304415,304862,305451,305458,305614,305801,306358,306423,306690,307618,309314,310175,311528,311604,311656,312010,312074,312115,312565,312650,312945,312990,313086,313539,313713,313818,314503,314535,314770,314835,315151,315480,316085,316275,316431,316505,316589,316601,316883,317827,318308,318469,318496,319014,319609,319853,320042,320091,320434,321225,321414,321517,321654,321839,321996,322943,323437,323659,325349,326517,327354,328651,329488,330282,330389,330441,330500,331009,331336,331935,332494,332652,332935,333210,333613,335263,335966,336006,336589,336843,336892,338067,338196,338658,339458,339981,339997,340151,340456,340576,340730,341309,341684,341792,341940,342079,342167,342339,342791,343813,343823,344642,346028,346056,346078,346444,346631,346883,346927,346947,347726,348147,348284,348328,348746,349124,349173,349508,349704,349718,349908,350442,350611,352279,352544,352550,352588,353140,353175,354147,354524,354556,354817,355118,355213,355664,355670,355673,355813,356037,356384,356899,357529,358356,358447,358869,359158,359610,359911,359925,360376,360713,360905,361178,362708,363249,363638,364835,365122,365674,367318,367745,367937,368052,368562,370601,374457,374575,379111,379148,379651,379681,379736,380106,381209,381528,381985,382605,382627,383573,383766,383871,384353,384410,384681,385247,385406,385828,385876,386098,386648,387519,387675,387850,388902,390784,391054,391696,392758,394769,394856,395296,396010,396052,396072,397866,398777,399422,399479,400097,400267,402129,402600,402907,408120,410039,410150,410654,411154,412280,412294,414341,414508,415085,415967,417661,418351,418376,418421,420039,420915,421133,423643,423716,423740,423939,424130,424133,424229,424550,424930,425506,425706,425713,426481,426545,426930,427042,427278,427464,427527,428144,428243,428305,428404,428782,428906,429184,429310,429384,429792,430070,431375,431709,431816,432753,434366,437831,438711,439943,440359,441387,441430,441518,441547,442165,442370,442513,442687,443387,443476,444019,444036,444066,444580,444623,444871,445118,445281,445520,445539,445565,445573,445799,446192,446250,446373,446428,446832,446981,447024,447273,447325,447365,447950,448446,449555,449782,450035,450144,450403,452247,452911,452921,453171,454617,455042,455504,457190,457425,457752,457899,459798,460004,460220,461795,462901,463902,464190,465125,466401,467136,469426,470103,472658,475206,476052,476422,476693,476938,477538,477545,478004,478045,478209,478303,478681,479457,480700,481201,481466,482150,482206,483069,483703,486011,486627,487265,487568,487591,487699,487837,487859,487937,488221,488667,490005,493585,499251,499311,499420,499699,500219,500288,500696,500812,500853,501224,501690,501870,502278,502475,502573,503083,503159,503298,504094,504267,504308,505306,505655,506047,506575,506737,507091,507628,507655,510351,512096,512846,512918,514826,518516,518763,520678,524772,526327,526706,527202,528526,528758,529298,529602,531049,531580,531707,531898,531977,532095,534345,536341,537259,538087,538391,539237,539462,539943,541790,543736,544079,544127,546488,549783,551951,552110,552481,552551,553969,554294,554397,554694,555414,556816,557044,557089,557247,557865,557868,558201,558578,559525,560124,560575,563013,563510,564910,566025,566281,566848,568955,573553,580596,583432,587938,593386,595160,596941,596958,597158,598773,600683,600695,600719,601133,601297,613080,615259,616873,618743,618956,619638,619698,619871,621618,623240,626446,626595,626919,627378,627564,628496,630702,630774,631412,631645,632123,633012,633505,634248,634955,635048,637965,640010,640779,641009,641299,644060,645918,648121,648235,649365,649700,650191,650342,650411,650817,654039,654137,654927,656545,657300,657589,657901,658170,659460,660147,661585,663599,664751,664924,665349,667447,667449,667564,667794,668358,670837,670906,671725,671852,671988,672428,672494,673158,675055,676611,676794,678385,678569,679439,680914,681951,682079,683196,684014,684127,687671,688085,688339,690453,690636,691649,691809,692029,692087,692958,695152,696814,697055,698169,698595,699682,701534,701798,702315,702652,705034,705319,707581,710424,710845,711096,711385,711405,711787,712100,713834,714249,715054,715077,715503,715887,715973,717262,718059,718809,721881,721969,723086,723682,724785,725270,725790,726465,726688,730525,732606,734170,736561,736679,737753,737808,738068,739799,739936,743171,744836,747184,747526,748192,754085,754664,756336,757063,757247,758750,761532,762011,763299,764371,766314,767700,768270,769894,771859,773230,776496,776602,776713,777729,779136,779355,780306,781067,783327,783786,783935,784561,784808,786085,786339,787537,789232,790564,790614,790629,790631,791813,791910,792580,793072,793428,793486,793890,795791,796236,799634,800246,800556,800642,800992,801671,803485,803567,804161,806868,807854,808013,808122,808138,811604,811612,812377,812507,814130,817255,818659,818856,820253,828150,829964,832772,835870,836054,836459,837032,839363,840505,840713,841283,841476,841642,842479,845780,847688,848997,849719,850617,850940,852438,852795,855698,855857,855935,856064,856847,859586,860122,860973,861906,864386,865299,865350,867409,868081,869216,872367,873341,874178,874440,874503,876474,876994,878947,880298,881084,881239,883622,883778,885545,889234,889706,891139,891669,892965,894459,895833,897142,897692,897836,900362,900505,902378,902996,903488,904071,904076,904606,905491,906746,906749,908901,909012,909071,909921,910354,910471,912252,912424,913012,913674,914400,914477,914800,915029,915170,915197,915366,915783,917036,917038,918002,919078,920897,924694,924811,925345,925736,925744,925875,925955,926138,926630,927380,927538,928764,928944,930372,932706,933005,934164,935602,935631,935903,938015,939239,939696,941376,941711,942340,942430,943132,943256,945639,945842,946288,947292,949926,949974,950363,950862,951669,951981,953570,953807,954871,956621,957047,964665,965601,968619,969194,972808,973070,973274,975407,975957,976682,979104,980114,982475,982855,983169,983606,984130,985429,986434,986977,987278,987336,987479,991971,992013,995430,998456,999404,1000080,1002201,1002955,1004464,1006017,1007432,1007464,1008836,1011491,1011858,1013432,1017593,1022579,1026739,1029091,1036278,1039108,1040357,1048261,1048618,1053007,1053017,1053579,1053982,1054334,1055950,1056240,1057847,1060319,1061268,1061814,1062108,1063712,1067125,1068446,1074860,1075817,1076145,1076764,1079208,1079562,1079832,1086372,1088291,1090101,1091635,1091764,1093710,1101067,1101280,1101445,1102695,1103153,1104330,1104396,1104984,1107351,1109006,1110383,1111404,1112376,1113442,1113519,1114070,1119870,1120467,1123759,1124422,1126640,1128206,1128315,1129886,1130394,1131028,1134892,1135104,1135503,1136672,1136915,1143286,1143454,1144606,1147427,1152565,1153110,1153717,1154183,1154375,1154462,1155167,1156112,1156504,1156922,1157998,1159867,1160138,1160232,1162494,1164476,1164585,1165646,1166308,1168083,1168188,1168296,1170243,1170461,1172579,1174876,1177045,1178911,1180519,1181273,1182426,1182840,1183102,1183540,1185237,1185531,1185538,1185729,1186280,1186797,1188294,1188882,1190453,1190813,1191496,1191917,1192048,1192639,1193698,1194043,1195541,1196192,1196311,1198052,1198702,1200289,1201390,1202518,1202989,1207112,1207738,1207867,1207919,1208394,1208509,1209692,1211402,1211504,1211757,1212420,1213431,1214735,1215331,1215620,1216475,1216877,1219892,1221047,1222368,1223558,1224875,1226140,1228864,1229225,1229432,1230456,1230574,1232314,1232407,1233188,1239267,1239547,1239854,1245054,1245509,1246550,1246925,1247409,1247856,1248026,1249709,1250610,1251262,1256351,1257246,1257579,1258913,1260454,1261203,1263662,1263963,1267898,1267979,1268447,1289758,1290145,1290350,1291864,1292318,1292990,1293352,1294612,1294936,1295026,1296369,1296812,1299639,1299844,1302197,1303575,1304228,1306627,1306993,1307933,1308496,1309719,1310097,1310193,1311028,1311904,1313995,1314927,1319714,1320470,1320507,1321915,1322610,1325111,1325196,1327140,1327892,1328810,1328854,1331704,1332610,1332915,1333639,1336716,1336948,1337633,1338705,1341590,1347024,1348002,1348632,1348734,1348775,1350237,1350249,1351424,1355718,1358787,1363420,1365674,1369822,1372525,1373740,1377107,1377969,1379885,1380461,1382997,1384273,1385995,1387312,1388515,1389266,1389459,1389763,1391252,1392235,1393104,1401943,1402296,1403616,1403640,1403786,1406761,1407242,1407678,1408219,1408424,1409846,1410282,1411790,1411847,1413272,1413557,1413898,1416598,1418223,1418893,1419785,1422959,1423912,1424188,1424626,1425408,1425765,1427352,1427400,1428114,1428322,1432572,1435838,1437249,1438607,1438868,1442277,1444511,1445449,1449148,1450704,1451831,1452313,1452596,1454682,1455068,1455570,1460669,1461464,1461518,1465175,1471439,1471495,1471816,1472246,1473269,1473279,1473566,1473891,1475732,1479383,1480069,1480440,1480710,1482023,1482864,1487828,1488028,1488583,1489595,1492035,1494018,1501706,1503027,1508291,1511619,1512260,1512411,1513391,1515615,1516196,1516433,1518359,1520117,1521246,1521699,1522926,1524307,1525311,1525964,1526302,1527684,1530011,1530596,1534001,1536047,1536374,1539331,1539830,1540164,1543442,1547992,1548250,1551026,1552427,1554239,1554268,1557197,1560372,1560631,1563083,1563417,1563531,1565926,1566815,1567369,1568022,1568778,1569499,1571118,1572314,1572322,1574128,1574257,1576425,1578750,1579216,1579369,1579685,1580143,1580693,1580995,1581219,1581343,1583292,1584550,1584916,1585926,1587529,1587624,1589705,1591485,1591980,1595424,1595687,1596636,1596683,1596781,1598915,1599846,1603400,1605513,1605554,1606164,1606881,1609127,1609844,1615482,1616028,1616179,1617286,1618500,1618543,1620133,1620612,1621286,1621296,1622033,1628913,1631008,1631337,1633487,1634012,1634135,1634299,1634663,1637704,1638087,1638469,1638704,1639768,1640624,1641774,1642828,1642919,1645205,1646721,1647676,1648414,1648515,1649237,1651690,1652713,1655527,1658321,1659030,1660030,1661181,1662469,1665123,1668586,1669974,1675807,1678033,1679660,1679859,1681357,1683947,1684253,1684653,1685789,1686266,1689064,1691210,1691296,1692633,1692856,1696129,1697574,1697587,1699478,1702117,1703812,1703842,1704004,1705254,1706732,1708587,1709308,1712445,1718173,1720411,1720617,1722188,1726389,1730127,1732028,1732263,1732662,1732859,1736479,1737985,1737993,1741990,1742173,1744465,1744629,1745394,1746177,1746668,1747768,1748490,1750947,1751290,1752329,1756290,1757516,1762271,1762578,1764702,1765502,1767297,1767472,1768082,1769059,1769578,1772631,1773289,1774911,1776286,1779375,1779785,1780779,1783434,1784404,1786447,1788870,1789850,1790187,1792998,1794233,1795555,1797760,1798499,1798948,1800891,1802134,1803074,1803484,1804141,1806804,1809534,1812132,1813179,1814067,1815138,1816281,1817540,1820915,1821817,1825248,1826682,1827084,1831125,1832914,1833267,1837686,1837985,1843541,1844196,1847059,1847102,1852448,1855272,1860019,1860623)
elif SITE == 'devrama.net':
	AEVANN_ID = 7
	FEATURES['PRONOUNS'] = True
	FEATURES['USERS_PERMANENT_WORD_FILTERS'] = True
	PERMS["SITE_SETTINGS"] = 4
	PERMS["ORGIES"] = 4
	PERMS["CHANGE_UNDER_SIEGE"] = 4
	PERMS["SITE_CACHE_PURGE_CDN"] = 4
	USER_IDS = (1,2,3,4,5,6,7,8,9,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,35,36,37,38,39,40,41,42,43,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,158,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,297,298,299,300,301,302,303,304,305,306,307,308,309,310,311,312,313,314,315,316,317,318,319,320,321,322,323,324,325,326,327,328,329,330,331,332,333,334,335,336,337,338,339,340,341,342,343,344,345,346,347,348,349,350,351,352,353,354,360,361,362,363,364,365,366,367,368,369,370,371,372,373,374,375,376,377)
else: # localhost or testing environment implied
	FEATURES['PRONOUNS'] = True
	FEATURES['USERS_PERMANENT_WORD_FILTERS'] = True
	HOLE_BANNER_LIMIT = 69420

	USER_IDS = (1,2,3,4)

BOT_IDs = {AUTOJANNY_ID, SNAPPY_ID, LONGPOSTBOT_ID, ZOZBOT_ID}

COLORS = {'ff459a','805ad5','62ca56','38a169','80ffff','2a96f3','eb4963','ff0000','f39731','30409f','3e98a7','e4432d','7b9ae4','ec72de','7f8fa6', 'f8db58','8cdbe6', DEFAULT_COLOR}

### COMMENT NOTIFICATIONS ###

COINFLIP_HEADS_OR_TAILS = ('<b style="color:#6023f8">Coinflip: :heads:</b>','<b style="color:#d302a7">Coinflip: :tails:</b>')
COINFLIP_EDGE = '<b style="color:#e7890c">Coinflip: :!marseysoypoint: :edge: :marseysoypoint:</b>'

FORTUNE_REPLIES = ('<b style="color:#6023f8">Your fortune: Allah Wills It</b>','<b style="color:#d302a7">Your fortune: Inshallah, Only Good Things Shall Come To Pass</b>','<b style="color:#e7890c">Your fortune: Allah Smiles At You This Day</b>','<b style="color:#7fec11">Your fortune: Your Bussy Is In For A Blasting</b>','<b style="color:#43fd3b">Your fortune: You Will Be Propositioned By A High-Tier Twink</b>','<b style="color:#9d05da">Your fortune: Repent, You Have Displeased Allah And His Vengeance Is Nigh</b>','<b style="color:#f51c6a">Your fortune: Reply Hazy, Try Again</b>','<b style="color:#00cbb0">Your fortune: lmao you just lost 100 coins</b>','<b style="color:#2a56fb">Your fortune: Yikes 😬</b>','<b style="color:#0893e1">Your fortune: You Will Be Blessed With Many Black Bulls</b>','<b style="color:#16f174">Your fortune: NEETmax, The Day Is Lost If You Venture Outside</b>','<b style="color:#fd4d32">Your fortune: A Taste Of Jannah Awaits You Today</b>','<b style="color:#bac200">Your fortune: Watch Your Back</b>','<b style="color:#6023f8">Your fortune: Outlook good</b>','<b style="color:#d302a7">Your fortune: Godly Luck</b>','<b style="color:#e7890c">Your fortune: Good Luck</b>','<b style="color:#7fec11">Your fortune: Bad Luck</b>','<b style="color:#43fd3b">Your fortune: Good news will come to you by mail</b>','<b style="color:#9d05da">Your fortune: Very Bad Luck</b>','<b style="color:#00cbb0">Your fortune: ｷﾀ━━━━━━(ﾟ∀ﾟ)━━━━━━ !!!!</b>','<b style="color:#2a56fb">Your fortune: Better not tell you now</b>','<b style="color:#0893e1">Your fortune: You will meet a dark handsome stranger</b>','<b style="color:#16f174">Your fortune: （　´_ゝ`）ﾌｰﾝ</b>','<b style="color:#fd4d32">Your fortune: Excellent Luck</b>','<b style="color:#bac200">Your fortune: Average Luck</b>')

FACTCHECK_REPLIES = ('<b style="color:#6023f8">Factcheck: This claim has been confirmed as correct by experts. </b>','<b style="color:#d302a7">Factcheck: This claim has been classified as misogynistic.</b>','<b style="color:#e7890c">Factcheck: This claim is currently being debunked.</b>','<b style="color:#7fec11">Factcheck: This claim is 100% true.</b>','<b style="color:#9d05da">Factcheck: This claim hurts trans lives.</b>','<b style="color:#f51c6a">Factcheck: [REDACTED].</b>','<b style="color:#00cbb0">Factcheck: This claim is both true and false.</b>','<b style="color:#2a56fb">Factcheck: You really believe that shit? Lmao dumbass nigga 🤣</b>','<b style="color:#0893e1">Factcheck: None of this is real.</b>','<b style="color:#16f174">Factcheck: Yes.</b>','<b style="color:#fd4d32">Factcheck: This claim has not been approved by experts.</b>','<b style="color:#bac200">Factcheck: This claim is a gross exageration of reality.</b>','<b style="color:#ff2200">Factcheck: WARNING! THIS CLAIM HAS BEEN CLASSIFIED AS DANGEROUS. PLEASE REMAIN STILL, AN AGENT WILL COME TO MEET YOU SHORTLY.</b>')

EIGHTBALL_REPLIES = ('<b style="color:#7FEC11">The 8-Ball Says: It is certain.</b>', '<b style="color:#7FEC11">The 8-Ball Says: It is decidedly so.</b>', '<b style="color:#7FEC11">The 8-Ball Says: Without a doubt.</b>', '<b style="color:#7FEC11">The 8-Ball Says: Yes definitely.</b>', '<b style="color:#7FEC11">The 8-Ball Says: You may rely on it.</b>', '<b style="color:#7FEC11">The 8-Ball Says: As I see it, yes.</b>', '<b style="color:#7FEC11">The 8-Ball Says: Most likely.</b>', '<b style="color:#7FEC11">The 8-Ball Says: Outlook good.</b>', '<b style="color:#7FEC11">The 8-Ball Says: Yes.</b>', '<b style="color:#7FEC11">The 8-Ball Says: Signs point to yes.</b>', '<b style="color:#E7890C">The 8-Ball Says: Reply hazy, try again.</b>', '<b style="color:#E7890C">The 8-Ball Says: Ask again later.</b>', '<b style="color:#E7890C">The 8-Ball Says: Better not tell you now.</b>', '<b style="color:#E7890C">The 8-Ball Says: Cannot predict now.</b>', '<b style="color:#E7890C">The 8-Ball Says: Concentrate and ask again.</b>', '<b style="color:#FD4D32">The 8-Ball Says: Don\'t count on it.</b>', '<b style="color:#FD4D32">The 8-Ball Says: My reply is no.</b>', '<b style="color:#FD4D32">The 8-Ball Says: My sources say no.</b>', '<b style="color:#FD4D32">The 8-Ball Says: Outlook not so good.</b>', '<b style="color:#FD4D32">The 8-Ball Says: Very doubtful.</b>')


### END COMMENT NOTIFICATIONS ###

discounts = {
	#verified email badge
	2: 0.02,
	# Big Spender badges, 2pp additive discount each
	69: 0.02,
	70: 0.02,
	71: 0.02,
	72: 0.02,
	73: 0.02,
	# Lootbox badges, 1pp additive discount each
	76: 0.01,
	77: 0.01,
	78: 0.01,
	#Lifetime donated badges
	257: 0.02,
	258: 0.02,
	259: 0.02,
	260: 0.02,
	261: 0.02,
	#Account age badges
	134: 0.01,
	237: 0.01,
}

CF_HEADERS = {"Authorization": f"Bearer {CF_KEY}", "Content-Type": "application/json"}

proxies = {"http":PROXY_URL,"https":PROXY_URL}

approved_embed_hosts = [
	### GENERAL PRINCIPLES #####################################################
	# 0) The goal is to prevent user info leaks. Worst is a username + IP.
	# 1) Cannot point to a server controlled by a site user.
	# 2) Cannot have open redirects based on query string. (tightest constraint)
	# 3) #2 but pre-stored, ex: s.lain.la 302 with jannie DM attack.
	# 4) Use the exact subdomain.

	### First-Party
	'rdrama.net',
	'i.rdrama.net',
	'staging.rdrama.net',
	'videos.watchpeopledie.tv',

	### Third-Party Image Hosts
	'i.imgur.com',
	'i.imgur.io',
	'pomf2.lain.la/f',
	'i.giphy.com/media',
	'media.giphy.com/media', # used by the GIF Modal
	'media0.giphy.com/media',
	'media1.giphy.com/media',
	'media2.giphy.com/media',
	'media3.giphy.com/media',
	'media4.giphy.com/media',
	'media.tenor.com',
	'media1.tenor.com',
	'c.tenor.com',
	'thumbs.gfycat.com',
	'i.postimg.cc', # WPD chat seems to like it
	'files.catbox.moe',

	### Third-Party Media
	# DO NOT ADD: wordpress.com, wp.com (maybe) | Or frankly anything. No more.
	'i.redd.it',
	'preview.redd.it',
	'external-preview.redd.it',
	'pbs.twimg.com/media',
	'i.pinimg.com',
	'kiwifarms.net/attachments',
	'uploads.kiwifarms.net/data/attachments',
	'kiwifarms.st/attachments',
	'uploads.kiwifarms.st/data/attachments',
	'kiwifarms.hk/attachments',
	'uploads.kiwifarms.hk/data/attachments',
	'upload.wikimedia.org/wikipedia',
	'live.staticflickr.com',
	'substackcdn.com/image',
	'i.kym-cdn.com/photos/images',
	'i.kym-cdn.com/entries/icons',
	'37.media.tumblr.com',
	'64.media.tumblr.com',
	'66.media.tumblr.com',
	'78.media.tumblr.com',
	'i.ytimg.com/vi',
]

if SITE_IMAGES not in approved_embed_hosts:
	approved_embed_hosts = [SITE_IMAGES] + approved_embed_hosts

if SITE not in approved_embed_hosts:
	approved_embed_hosts = [SITE] + approved_embed_hosts

def is_site_url(url):
	return (url
		and '\\' not in url
		and ((url.startswith('/') and not url.startswith('//'))
			or url.startswith(f'{SITE_FULL}/')))

def is_safe_url(url):
	if is_site_url(url):
		return True
	if any(url.startswith(f"https://{x}/") for x in approved_embed_hosts):
		return True
	return False

hosts = "|".join(approved_embed_hosts).replace('.','\.')

has_sidebar = path.exists(f'files/templates/sidebar_{SITE_NAME}.html')
has_logo = path.exists(f'files/assets/images/{SITE_NAME}/logo.webp')

forced_hats = {
	"rehab": ("Roulette", "I'm a recovering ludomaniac!"),
	"progressivestack": ("Attention Whore", "I won the oppression olympics!"),
	"longpost": ("The Pizzashill", "We need to get rid of the character limit!"),
	"bird": ("Bluecheck", "Three sentences is too much for me..."),
	"hieroglyphs": ("Three Lil Marseys", ":marseynotes: :marseynotes: :I prefer to speak in cats:"),
	"bite": ("Vampire Mask", "When other little girls wanted to be ballet dancers I kind of wanted to be a vampire."),
	"rainbow": ("Globohomo", "Homosexuality is no longer optional!"),
	"owoify": ("Cat Ears (wiggly)", "Nuzzles, pounces on you, UwU, you're so warm!.."),
	"sharpen": ("Bane Mask", "No one understands..."),
	"earlylife": ("The Merchant", "SHUT IT DOWN, the goys know!"),
	"marsify": ("Marsified", "I can't pick my own Marseys, help!"),
	"is_suspended": ("Behind Bars", "This user is banned and needs to do better!"),
	"chud": (
				("Egg_irl", "This user is getting in touch with xir identity!"),
				("Trans Flag", "Just in case you forgot, trans lives matter."),
				("Trans Flag II", "Your egg is cracked; wear it with pride!"),
				("Pride Flag", "Never forget that this is a primarily gay community. Dude bussy lmao."),
				("Pride Flag II", "This user is a proud supporter of LGBTQ+ rights."),
			),
	"queen": (
				("Flower Crown I", "This user is getting in touch with her feminine side 🥰"),
				("Flower Crown II", "This user is getting in touch with her feminine side 🥰"),
				("Flower Crown III", "This user is getting in touch with her feminine side 🥰"),
				("Flower Crown IV", "This user is getting in touch with her feminine side 🥰"),
				("Flower Crown V", "This user is getting in touch with her feminine side 🥰"),
				("Flower Crown VI", "This user is getting in touch with her feminine side 🥰"),
				("Flower Crown VII", "This user is getting in touch with her feminine side 🥰"),
				("Flower Crown VIII", "This user is getting in touch with her feminine side 🥰"),
				("Flower Crown IX", "This user is getting in touch with her feminine side 🥰"),
				("Flower Crown X", "This user is getting in touch with her feminine side 🥰"),
				("Flower Crown XI", "This user is getting in touch with her feminine side 🥰"),
				("Flower Crown XII", "This user is getting in touch with her feminine side 🥰"),
				("Flower Crown XIII", "This user is getting in touch with her feminine side 🥰"),
				("Flower Crown XIV", "This user is getting in touch with her feminine side 🥰"),
				("Emoji Crown (hearts and shooting stars)", "This user is getting in touch with her feminine side 🥰")
			 ),

}

IMAGE_FORMATS = ('png','jpg','jpeg','webp','gif')
VIDEO_FORMATS = ('mp4','webm','mov','avi','mkv','flv','m4v','3gp')
AUDIO_FORMATS = ('mp3','wav','ogg','aac','m4a','flac')

if not IS_LOCALHOST and SECRET_KEY == DEFAULT_CONFIG_VALUE:
	from warnings import warn
	warn("Secret key is the default value! Please change it to a secure random number. Thanks <3", RuntimeWarning)

GLOBAL = environ.get("GLOBAL", "").strip()
GLOBAL2 = environ.get("GLOBAL2", "").strip()

STARS = '\n\n★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★\n\n'

EMOJI_KINDS = ("Marsey", "Tay", "Platy", "Wolf", "Donkey Kong", "Capy", "Carp", "Marsey Flags", "Marsey Alphabet", "Classic", "Rage", "Wojak", "Misc")

t = datetime.datetime.now()

fistmas_begin_day = 1 if SITE_NAME == 'rDrama' else 21
fistmas_begin = datetime.datetime.strptime(f'{fistmas_begin_day}/12/{t.year}', '%d/%m/%Y')
fistmas_end = datetime.datetime.strptime(f'26/12/{t.year}', '%d/%m/%Y') + datetime.timedelta(hours=16)
def IS_FISTMAS():
	return fistmas_begin < datetime.datetime.now() < fistmas_end

homoween_begin_day = 18 if SITE_NAME == 'rDrama' else 26
homoween_begin = datetime.datetime.strptime(f'{homoween_begin_day}/10/{t.year}', '%d/%m/%Y')
homoween_end = datetime.datetime.strptime(f'1/11/{t.year}', '%d/%m/%Y') + datetime.timedelta(hours=16)
def IS_HOMOWEEN():
	return homoween_begin < datetime.datetime.now() < homoween_end

dkd_begin = datetime.datetime.strptime(f'3/4/{t.year}', '%d/%m/%Y')
dkd_end = datetime.datetime.strptime(f'10/4/{t.year}', '%d/%m/%Y')
def IS_DKD():
	return SITE_NAME == 'rDrama' and dkd_begin < datetime.datetime.now() < dkd_end

birthgay_begin = datetime.datetime.strptime(f'20/5/{t.year}', '%d/%m/%Y')
birthgay_end = datetime.datetime.strptime(f'22/5/{t.year}', '%d/%m/%Y')
def IS_BIRTHGAY():
	return SITE_NAME == 'rDrama' and birthgay_begin < datetime.datetime.now() < birthgay_end

birthdead_begin = datetime.datetime.strptime(f'26/4/{t.year}', '%d/%m/%Y')
birthdead_end = datetime.datetime.strptime(f'28/4/{t.year}', '%d/%m/%Y')
def IS_BIRTHDEAD():
	return SITE_NAME == 'WPD' and birthdead_begin < datetime.datetime.now() < birthdead_end

def IS_EVENT():
	if IS_FISTMAS():
		return "fistmas"
	elif IS_HOMOWEEN():
		return "homoween"
	elif IS_DKD():
		return "DKD"
	elif IS_BIRTHGAY():
		return "birthgay"
	elif IS_BIRTHDEAD():
		return "birthdead"
	return None

CHUD_PHRASES = ( #if you add a phrase, remove one in turn
	"Trans lives matter",
	"Black lives matter",
	"Black trans lives matter",
	"I say this as a feminist ally",
	"I stand with Israel",
	"Palestinian lives matter",
	"Vaccines work",
	"Trans women are women",
	"Furry rights are human rights",
	"Trans furry lives matter",
	"Trump for prison",
	"Hillary 2024",
	"Jewish lives matter",
	"White extinction is long overdue",
	"Climate action now",
	"Long live the CCP",
	"I stand with Ukraine",
	"I love sucking cock",
	"This post rests on native land",
	"Communism will win",
)

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"}

GIRL_NAMES = {
	'A': ['Ashley', 'Alexis', 'Alyssa', 'Abigail', 'Anna', 'Amanda', 'Alexandra', 'Allison', 'Amber', 'Andrea', 'Autumn', 'Angela', 'Alexa', 'Alexandria', 'Amy', 'Ariana', 'Audrey', 'Angel', 'Alicia', 'Adriana', 'Arianna', 'Ana', 'Angelica', 'Angelina', 'Alexia', 'Alejandra', 'Avery', 'Ashlyn', 'Ava', 'Alondra', 'Ariel', 'Amaya', 'Abby', 'Amelia', 'Aaliyah', 'April', 'Adrianna', 'Asia', 'Aubrey', 'Alison', 'Allyson', 'Alexus', 'Alana', 'Alissa', 'Aliyah', 'Anne', 'Annie', 'Anastasia', 'Ashlee', 'Alaina', 'Addison', 'Ashleigh', 'Ashton', 'Anahi', 'Ashlynn', 'Allie', 'Alisha', 'Alice', 'Abbey', 'Alayna', 'Ayanna', 'Annika', 'Alyson', 'Annabelle', 'Alina', 'Angelique', 'Aurora', 'Alma', 'Ann', 'Alanna', 'Angie', 'Amari', 'Aileen', 'Athena', 'Adrienne', 'Arielle', 'Abbigail', 'Aimee', 'Alivia', 'Amya', 'Aspen', 'Aniya', 'Anya', 'Abbie', 'Araceli', 'Aleah', 'Ally', 'Alisa', 'Antonia', 'Anika', 'Alessandra', 'Aisha', 'Ayana', 'America', 'Abigayle', 'Aliya', 'Alena', 'Aylin', 'Aniyah', 'Alia', 'Anita', 'Alexandrea', 'Annette', 'Amani', 'Armani', 'Anissa', 'Aubree', 'Ansley', 'Alysa', 'Alize', 'Amara', 'Arlene', 'Aiyana', 'Allyssa', 'Adeline', 'Annalise', 'Amira', 'Alexys', 'Abril', 'Ayla', 'Asha', 'Aryanna', 'Anaya', 'Arely', 'Alysha', 'Aracely', 'Alex', 'Ali', 'Alycia', 'Anjali', 'Amiya', 'Aja', 'Annabel', 'Aliza', 'Ashly', 'Abigale', 'Abagail', 'Aria', 'Ashtyn', 'Annamarie', 'Amina', 'Antoinette'],
	'B': ['Brianna', 'Brooke', 'Brittany', 'Bailey', 'Breanna', 'Briana', 'Britney', 'Brittney', 'Bethany', 'Bianca', 'Brenda', 'Brooklyn', 'Bridget', 'Brenna', 'Bryanna', 'Baylee', 'Brandi',
	'Brandy', 'Bailee', 'Brisa', 'Barbara', 'Brooklynn', 'Breana', 'Brynn', 'Blanca', 'Bria', 'Beatriz', 'Brianne', 'Brielle', 'Bella', 'Brook', 'Berenice', 'Baby', 'Bridgette', 'Bryana', 'Brionna', 'Bonnie', 'Belen', 'Beatrice', 'Blair', 'Breonna', 'Breanne'],
	'C': ['Chloe', 'Courtney', 'Caroline', 'Christina', 'Caitlin', 'Catherine', 'Claire', 'Cheyenne', 'Cassandra', 'Cassidy', 'Caitlyn', 'Crystal', 'Chelsea', 'Cynthia', 'Carly', 'Camryn', 'Claudia', 'Cameron', 'Casey', 'Christine', 'Cierra', 'Cindy', 'Carolina', 'Camille', 'Carmen', 'Celeste', 'Ciara', 'Cecilia', 'Charlotte', 'Carolyn', 'Callie', 'Clarissa', 'Cristina', 'Cassie', 'Clara', 'Cheyanne', 'Cara', 'Carla', 'Carley', 'Carissa', 'Colleen', 'Charity', 'Chelsey', 'Cora', 'Chasity', 'Carlie', 'Carrie', 'Chyna', 'Clare', 'Cristal', 'Corinne', 'Ciera', 'Carina', 'Christian', 'Cayla', 'Candace', 'Celia', 'Calista', 'Carlee', 'Carson', 'Camila', 'Christy', 'Celine', 'Chandler', 'Candice', 'Carol', 'Casandra', 'Carli', 'Catalina', 'Celina', 'Cecelia', 'Chaya', 'Christa', 'Citlalli', 'Chanel', 'Cali', 'Caitlynn', 'Christiana', 'Cortney', 'Caleigh',
	'Chantel', 'Cielo', 'Cydney'],
	'D': ['Destiny', 'Danielle', 'Diana', 'Daisy', 'Daniela', 'Diamond', 'Desiree', 'Delaney', 'Dominique', 'Dakota', 'Deanna', 'Dana', 'Destinee', 'Denise', 'Deja', 'Daniella', 'Deborah', 'Devin', 'Destiney', 'Destini',
	'Dulce', 'Desirae', 'Daphne', 'Devon', 'Donna', 'Delilah', 'Devyn', 'Diane', 'Damaris', 'Dorothy', 'Drew', 'Darlene', 'Dasia', 'Dariana', 'Dianna', 'Darby', 'Darian', 'Dayana', 'Dallas', 'Deasia', 'Dawn', 'Dejah', 'Daisha', 'Destany', 'Daija', 'Delia', 'Dayna'],
	'E': ['Emily', 'Elizabeth', 'Emma', 'Erin', 'Erica', 'Erika', 'Evelyn', 'Esmeralda', 'Elena', 'Elise', 'Ella', 'Eva', 'Esther', 'Emilee', 'Ellie', 'Eleanor', 'Eliza', 'Elisabeth', 'Ellen', 'Emely', 'Emilie', 'Elaina', 'Elisa', 'Eden', 'Esperanza', 'Eliana', 'Eve', 'Ebony', 'Edith', 'Elaine', 'Essence', 'Emilia', 'Eileen', 'Ericka', 'Estrella', 'Elissa', 'Elyse', 'Eryn', 'Elyssa', 'Elsa', 'Emmalee', 'Estefania', 'Emerald'],
	'F': ['Faith', 'Fatima', 'Francesca', 'Felicity', 'Fiona', 'Felicia', 'Fernanda', 'Frances', 'Fabiola'],
	'G': ['Grace', 'Gabrielle', 'Gabriella', 'Gabriela', 'Giselle', 'Gianna', 'Gracie', 'Guadalupe', 'Genesis', 'Gillian', 'Georgia', 'Gina', 'Gloria', 'Gisselle', 'Genevieve', 'Gwendolyn', 'Gretchen', 'Greta', 'Gabriel', 'Giovanna', 'Graciela', 'Gia'],
	'H': ['Hannah', 'Haley', 'Hailey', 'Heather', 'Hope', 'Hayley', 'Hanna', 'Holly', 'Haylee', 'Hallie', 'Heaven', 'Helen', 'Heidi', 'Haleigh', 'Harley', 'Hailee', 'Hunter', 'Halle', 'Halie', 'Hana', 'Haylie', 'Helena', 'Hayden', 'Harmony', 'Hailie', 'Haven', 'Hillary', 'Hazel', 'Hadley'],
	'I': ['Isabella', 'Isabel', 'Isabelle', 'Imani', 'Ivy', 'India', 'Iris', 'Irene', 'Isis', 'Itzel', 'Izabella', 'Iliana', 'Isabela', 'Ingrid', 'Ivana', 'Iyana'],
	'J': ['Jessica', 'Jennifer', 'Jasmine', 'Julia', 'Jordan', 'Jenna', 'Jacqueline', 'Jada', 'Jade', 'Jillian', 'Jocelyn', 'Jamie', 'Jordyn', 'Julie', 'Jasmin', 'Jazmin', 'Jazmine', 'Joanna', 'Juliana', 'Julianna', 'Jayla', 'Jaqueline', 'Josephine', 'Josie', 'Jacquelyn', 'Jenny', 'Julissa', 'Jaden', 'Jessie', 'Janet', 'Jane', 'Jayda', 'Jaclyn', 'Joy', 'Johanna', 'Janelle', 'Janae', 'Justine', 'Jayden', 'Julianne', 'Justice', 'Jewel', 'Judith', 'Jaelyn', 'Juliet', 'Jadyn', 'Joselyn', 'Juliette', 'Jazlyn', 'Jazmyn', 'Joyce', 'Janessa', 'Jalyn', 'Jaida', 'Jenifer', 'Jacey', 'Jackeline', 'Jaime', 'Jaiden', 'Janice', 'Jaquelin', 'Jeanette', 'Jacklyn', 'Jesse', 'Jolie', 'Juanita', 'Jaycee', 'Jasmyn', 'Jaylin', 'Joelle', 'Joana', 'Jazmyne', 'Jakayla', 'Jana', 'Joanne', 'Janiya', 'Jena', 'Jailyn', 'Jayde', 'Jill'],
	'K': ['Kayla', 'Kaitlyn', 'Katherine', 'Katelyn', 'Kimberly', 'Kaylee', 'Kelsey', 'Kathryn', 'Katie', 'Kylie', 'Kelly', 'Kiara', 'Kennedy', 'Kristen', 'Karen', 'Kaitlin', 'Karina', 'Kendra', 'Kendall', 'Kara', 'Kylee', 'Kyra', 'Karla', 'Kathleen', 'Kristina', 'Kate', 'Katelynn', 'Kyla', 'Katrina', 'Kirsten', 'Kiana', 'Kassandra', 'Kira', 'Kristin', 'Kailey', 'Kassidy', 'Katlyn', 'Kamryn', 'Krystal', 'Kayleigh', 'Kaitlynn', 'Kierra', 'Kaylie', 'Kasey', 'Krista', 'Kaleigh', 'Kali', 'Karissa', 'Kelsie', 'Kiersten', 'Kiera', 'Kaylin', 'Kiley', 'Kaila', 'Kailee', 'Kenya', 'Kaley', 'Kelli', 'Kyleigh', 'Kaylyn', 'Kailyn', 'Karlee', 'Keely', 'Katelin', 'Kianna', 'Kacie', 'Karli', 'Kayley', 'Katarina', 'Kellie', 'Kaelyn', 'Kathy', 'Katharine', 'Karlie', 'Kourtney', 'Kenzie', 'Karly', 'Kristine', 'Kaylynn', 'Kelsi', 'Kaya', 'Kayli', 'Kallie', 'Kasandra', 'Kari', 'Kaylah', 'Kennedi', 'Karley', 'Kristy', 'Kiarra', 'Kacey', 'Keara', 'Kalyn', 'Kaela', 'Katia', 'Kinsey', 'Kaia', 'Katerina', 'Keira', 'Kaci', 'Kameron', 'Katy', 'Kirstin',
	'Kori', 'Katlynn', 'Kaylan', 'Kenna', 'Keeley', 'Kenia'],
	'L': ['Lauren', 'Laura', 'Leslie', 'Leah', 'Lindsey', 'Lily', 'Lillian', 'Lydia', 'Lindsay', 'Lauryn', 'Lisa', 'Liliana', 'Logan', 'Lucy', 'Linda', 'Lizbeth', 'Lacey', 'Lesly', 'Litzy', 'Layla', 'Lilly', 'Lesley', 'Lexi', 'Larissa', 'Lucia', 'Lorena', 'Leilani', 'Luz', 'Lena', 'Lexie', 'Leticia', 'Laurel', 'Leila', 'Leanna', 'Lyndsey', 'Laila', 'Lea', 'Lexus', 'Lizeth', 'Loren', 'Laney', 'Lizette', 'Lilian', 'Lila', 'Lillie', 'Lia', 'Lyric', 'Liana', 'London', 'Lara', 'Lisette', 'Lori', 'Lilliana', 'Lourdes', 'Luisa', 'Leann', 'Laisha'],
	'M': ['Madison', 'Megan', 'Morgan', 'Maria', 'Mackenzie', 'Mary', 'Michelle', 'Madeline', 'Makayla', 'Melissa', 'Mariah', 'Marissa', 'Mia', 'Molly', 'Mikayla', 'Margaret', 'Miranda', 'Maya', 'Melanie', 'Madelyn', 'Mckenzie', 'Meghan', 'Michaela', 'Monica', 'Mya', 'Mckenna', 'Maggie', 'Makenzie', 'Mallory', 'Macy', 'Makenna', 'Miriam', 'Madeleine', 'Mercedes', 'Meredith', 'Marisa', 'Mariana', 'Monique', 'Marina', 'Meagan', 'Martha', 'Marie', 'Mikaela', 'Madalyn', 'Marisol', 'Melody', 'Mckayla', 'Maddison', 'Madisyn', 'Madyson', 'Mayra', 'Macie', 'Malia', 'Marilyn', 'Marlene', 'Macey', 'Miracle', 'Madelynn', 'Melina', 'Maia', 'Maritza', 'Mollie', 'Montana', 'Mara', 'Micaela', 'Micah', 'Madilyn', 'Maribel', 'Madisen', 'Margarita', 'Moriah', 'Mariam', 'Meaghan', 'Marley', 'Melinda', 'Marian', 'Mariela', 'Maura', 'Mattie', 'Maci', 'Maegan', 'Maeve', 'Marianna', 'Myah', 'Monserrat', 'Maranda', 'Michele', 'Magdalena', 'Mireya', 'Misty', 'Martina', 'Maryam', 'Myra', 'Marlee', 'Mandy', 'Maiya', 'Melisa', 'Marlen'],
	'N': ['Nicole', 'Natalie', 'Naomi', 'Nina', 'Natalia', 'Nancy', 'Nadia', 'Natasha', 'Nia', 'Noelle', 'Nichole',
	'Nora', 'Nathalie', 'Nikki', 'Nicolette', 'Noemi', 'Nayeli', 'Nataly', 'Noelia', 'Nya', 'Nyah', 'Nikita', 'Nadine', 'Norma', 'Nyasia', 'Neha'],
	'O': ['Olivia', 'Odalys'],
	'P': ['Paige', 'Payton', 'Peyton', 'Patricia', 'Priscilla', 'Paola', 'Precious', 'Phoebe', 'Pamela', 'Paris', 'Paulina', 'Piper', 'Perla', 'Paula', 'Presley', 'Princess', 'Parker', 'Patience', 'Paloma'],
	'Q': ['Quinn'],
	'R': ['Rachel', 'Rebecca', 'Riley', 'Rebekah', 'Raven', 'Rachael', 'Ruby', 'Reagan', 'Rylee', 'Rose', 'Rosa', 'Ruth', 'Raquel', 'Renee', 'Rhiannon', 'Regan', 'Regina', 'Ryan', 'Reyna', 'Robin', 'Raegan', 'Rosemary', 'Rylie', 'Robyn', 'Rosalinda', 'Rebeca', 'Rocio', 'Reilly', 'Rachelle', 'Ryleigh', 'Ryann', 'Reina', 'Randi', 'Reanna', 'Rita', 'Reese',
	'Roxanne', 'Raina', 'Rhianna', 'Rayna'],
	'S': ['Sarah', 'Samantha', 'Sydney', 'Savannah', 'Stephanie', 'Sophia', 'Sierra', 'Sara', 'Shelby', 'Sabrina', 'Skylar', 'Summer', 'Shannon', 'Sophie', 'Sofia', 'Selena', 'Serena', 'Savanna', 'Sadie', 'Skyler', 'Sandra', 'Sidney', 'Shania', 'Shayla', 'Susan', 'Sharon', 'Serenity', 'Sasha', 'Skye', 'Sage', 'Sylvia', 'Sonia', 'Shyanne', 'Sydnee', 'Sydni', 'Sarai', 'Shayna', 'Simone', 'Savanah', 'Stacy', 'Sienna', 'Sandy', 'Stella', 'Skyla', 'Salma', 'Sydnie', 'Stacey', 'Sheila', 'Shawna', 'Sally', 'Susana', 'Shea', 'Stephany', 'Savana', 'Shyann', 'Shaina', 'Selina', 'Sarina', 'Shaylee', 'Sheridan', 'Shakira', 'Shirley', 'Silvia', 'Stefanie', 'Samara', 'Sonya', 'Shaniya', 'Saige', 'Scarlett', 'Sky'],
	'T': ['Taylor', 'Trinity', 'Tiffany', 'Tara', 'Tatiana', 'Tori', 'Tessa', 'Tabitha', 'Teresa', 'Tiana', 'Tiara', 'Talia', 'Tatyana', 'Tia', 'Tyler', 'Tamara', 'Theresa', 'Tatum', 'Tamia', 'Tyra', 'Taryn', 'Tania', 'Tianna', 'Tayler', 'Tierra',
	'Toni', 'Tess', 'Tanya', 'Tina', 'Thalia', 'Tracy', 'Teagan', 'Tatianna', 'Taya', 'Trisha'],
	'U': ['Unique'],
	'V': ['Victoria', 'Vanessa', 'Veronica', 'Valerie', 'Valeria', 'Vivian', 'Virginia', 'Viviana', 'Valentina', 'Violet'],
	'W': ['Whitney', 'Wendy', 'Willow'],
	'X': ['Xena'],
	'Y': ['Yesenia', 'Yasmine', 'Yasmin', 'Yvette', 'Yolanda', 'Yadira', 'Yvonne', 'Yamilet', 'Yazmin', 'Yasmeen', 'Yessenia'],
	'Z': ['Zoe', 'Zoey', 'Zaria', 'Zoie']
}

GIRL_NAMES_TOTAL = set()
for l in GIRL_NAMES.values():
    GIRL_NAMES_TOTAL.update(l)

from sqlalchemy.engine.create import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(environ.get("DATABASE_URL").strip(), connect_args={"options": "-c statement_timeout=10000 -c idle_in_transaction_session_timeout=40000"})
db_session = scoped_session(sessionmaker(bind=engine, autoflush=False))

approved_embed_hosts_for_csp = ' '.join(set(x.split('/')[0] for x in approved_embed_hosts))
csp = f"default-src 'none'; frame-ancestors 'none'; form-action 'self'; manifest-src 'self'; worker-src 'self'; base-uri 'self'; font-src 'self'; style-src-elem 'self' rdrama.net watchpeopledie.tv; style-src-attr 'unsafe-inline'; style-src 'self' 'unsafe-inline'; script-src-elem 'self' challenges.cloudflare.com static.cloudflareinsights.com; script-src-attr 'none'; script-src 'self' challenges.cloudflare.com static.cloudflareinsights.com; frame-src challenges.cloudflare.com cdpn.io platform.twitter.com rumble.com player.twitch.tv; connect-src 'self' submit.watchpeopledie.tv; img-src {approved_embed_hosts_for_csp} data:; media-src *.googlevideo.com archive.org *.us.archive.org {approved_embed_hosts_for_csp};"
if not IS_LOCALHOST:
	csp += ' upgrade-insecure-requests;'

with open("includes/content-security-policy", "w") as f:
	f.write(f'add_header Content-Security-Policy "{csp}";')
