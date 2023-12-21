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
FP = environ.get("FP", "").strip()
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

REDDIT_NOTIFS_SITE = set()
REDDIT_NOTIFS_USERS = {}

if len(SITE_NAME) > 5:
	REDDIT_NOTIFS_SITE.add(SITE_NAME.lower())

if not IS_LOCALHOST:
	REDDIT_NOTIFS_SITE.add(SITE)

TAGLINES = ()

if SITE_NAME == 'rDrama':
	CURSORMARSEY_DEFAULT = True
	DEFAULT_COLOR = "ff459a"

	patron = "Paypig"

	TAGLINES = (
		"largest online LGBTQ+ club",
		"largest online furfest",
		"largest cat pics site",
		"largest basket-weaving forum",
		"largest autism support group",
		"largest aztec heritage forum",
		"official George Soros fanclub",
		"CCP's official newspaper",
		"Nintendo gamers only",
		"donkey kong country",
		"banned from Reddit, Github & Bing!",
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
	)

	BOOSTED_HOLES = {
		'furry',
		'femboy',
		'anime',
		'gaybros',
		'againsthateholes',
		'changelog',
		'programming',
		'slackernews',
		'wallstreetbets',
		'lit',
		'vidya',
		'jihad',
		'museumofrdrama',
		'space',
		'femaledatingstrategy',
		'meta',
		'love4fatpeople',
		'traps',
		'transgender',
		'chinchilla',
		'sports',
	}

	REDDIT_NOTIFS_SITE.update({'marsey', 'r/drama', 'justice4darrell', 'cringetopia.org'})

elif SITE_NAME == 'WPD':
	REDDIT_NOTIFS_SITE.update({'marsey', 'watchpeopledie', 'makemycoffin'})


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

THEMES = ["4chan","classic","classic_dark","coffee","dark","dramblr","light","midnight","tron","win98"]
LIGHT_THEMES = ["4chan","classic","coffee","light","win98"]
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
HOLE_SIDEBAR_URL_COLUMN_LENGTH = 60
HOLE_BANNER_URL_COLUMN_LENGTH = 60
HOLE_CSS_COLUMN_LENGTH = 6000
HOLE_MARSEY_URL_LENGTH = 60

################################################################################
### SITE SPECIFIC CONSTANTS
################################################################################

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
	'NOTIFICATIONS_REDDIT': 1,
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
	'ENABLE_VOTE_BUTTONS_ON_USER_PAGE': 1,
	'NOTIFICATIONS_HOLE_INACTIVITY_DELETION': 1,
	'NOTIFICATIONS_HOLE_CREATION': 1,
	'NOTIFICATIONS_MODERATOR_ACTIONS': 1,

	'IS_PERMA_PROGSTACKED': 2,
	'USER_BADGES': 2,
	'USER_LINK': 2,
	'USER_CHANGE_FLAIR': 2,
	'LOTTERY_VIEW_PARTICIPANTS': 2,
	'POST_COMMENT_INFINITE_PINGS': 2,
	'IGNORE_1MONTH_EDITING_LIMIT': 2,
	'ORGIES': 2,
	'POST_BETS': 2,
	'POST_BETS_DISTRIBUTE': 2,

	'ADMIN_REMOVE': 3,
	'ADMIN_ACTIONS_REVERT': 3,
	'DOMAINS_BAN': 3,
	'EDIT_RULES': 3,
	'LOTTERY_ADMIN': 3,
	'SITE_SETTINGS': 3,
	'SITE_CACHE_PURGE_CDN': 3,
	'NOTIFICATIONS_FROM_SHADOWBANNED_USERS': 3,
	'APPS_MODERATION': 3,
	'USE_ADMIGGER_THREADS': 3,
	'MODERATE_PENDING_SUBMITTED_ASSETS': 3,
	'UPDATE_ASSETS': 3,
	'DELETE_MEDIA': 3,

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
	'MODS_EVERY_HOLE': 4,
	'MODS_EVERY_GROUP': 4,
	'IGNORE_DOMAIN_BAN': 4,
	'USER_RESET_PASSWORD': 4,
	'CLAIM_REWARDS_ALL_USERS': 4,
	'IGNORE_AWARD_IMMUNITY': 4,
	'INSERT_TRANSACTION': 4,

	'VIEW_EMAILS': 5,
	'INFINITE_CURRENCY': 5,
}

FEATURES = {
	'MARSEYBUX': True,
	'AWARDS': True,
	'CHAT': True,
	'CW_MARKING': False,
	'PINS': True,
	'PRONOUNS': False,
	'BADGES': True,
	'HATS': True,
	'HOUSES': False,
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
	'NSFW_MARKING': True,
	'PING_GROUPS': True,
	'BOTS': True,
}

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
CSS_LENGTH_LIMIT = 10000 # do not make larger than 20000 characters without altering the table
COMMENT_MAX_DEPTH = 200
TRANSFER_MESSAGE_LENGTH_LIMIT = 200 # do not make larger than 10000 characters (comment limit) without altering the table
MIN_REPOST_CHECK_URL_LENGTH = 9 # also change the constant in checkRepost() of submit.js
CHAT_LENGTH_LIMIT = 1000
HOLE_BANNER_LIMIT = 10

BIO_FRIENDS_ENEMIES_LENGTH_LIMIT = 5000 # do not make larger than 5000 characters without altering the table
BIO_FRIENDS_ENEMIES_HTML_LENGTH_LIMIT = 20000 # do not make larger than 20000 characters without altering the table

COSMETIC_AWARD_COIN_AWARD_PCT = 0.50

TRUESCORE_MINIMUM = 0

LOGGEDIN_ACTIVE_TIME = 15 * 60
PFP_DEFAULT_MARSEY = True
NEW_USER_AGE = 7 * 86400
NOTIFICATION_SPAM_AGE_THRESHOLD = 0
COMMENT_SPAM_LENGTH_THRESHOLD = 0
UNDER_SIEGE_AGE_THRESHOLD = 10 * 60

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
LAWLZ_ID = 0

IMMUNE_TO_NEGATIVE_AWARDS = {}
EXEMPT_FROM_1MONTH_EDITING_LIMIT = {}

MODMAIL_ID = 2
GIFT_NOTIF_ID = 5
SIGNUP_FOLLOW_ID = 0
PROGSTACK_ID = 4

POLL_BET_COINS = 200
POLL_MAX_OPTIONS = 200
WELCOME_MSG = f"Welcome to {SITE_NAME}!"

LOTTERY_TICKET_COST = 12
LOTTERY_SINK_RATE = 3
LOTTERY_DURATION = 60 * 60 * 24 * 7

BUG_THREAD = 0

SIDEBAR_THREAD = 0
BANNER_THREAD = 0
BADGE_THREAD = 0
SNAPPY_THREAD = 0
CHANGELOG_THREAD = 0
ADMIGGER_THREADS = {SIDEBAR_THREAD, BANNER_THREAD, BADGE_THREAD, SNAPPY_THREAD, CHANGELOG_THREAD}

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

NOTIFIED_USERS = {}

if SITE in {'rdrama.net', 'staging.rdrama.net'}:
	NOTIFICATION_SPAM_AGE_THRESHOLD = 0.5 * 86400

	TELEGRAM_ID = "rdramanet"
	TWITTER_ID = "rdramanet"
	DEFAULT_TIME_FILTER = "day"

	FEATURES['PRONOUNS'] = True
	FEATURES['HOUSES'] = True
	FEATURES['USERS_PERMANENT_WORD_FILTERS'] = True

	BUG_THREAD = 18459

	SIDEBAR_THREAD = 37696
	BANNER_THREAD = 37697
	BADGE_THREAD = 37833
	SNAPPY_THREAD = 37749
	CHANGELOG_THREAD = 165657
	ADMIGGER_THREADS = {SIDEBAR_THREAD, BANNER_THREAD, BADGE_THREAD, SNAPPY_THREAD, CHANGELOG_THREAD, 79285, 166300, 187078}

	TRUESCORE_MINIMUM = 10

	HOLE_COST = 50000
	HOLE_INACTIVITY_DELETION = True

	BOT_SYMBOL_HIDDEN = {12125,16049,23576}
	ANTISPAM_BYPASS_IDS = BOT_SYMBOL_HIDDEN | {1703, 13427, 15014, 24197}

	EXEMPT_FROM_1MONTH_EDITING_LIMIT = {1048}

	AUTOJANNY_ID = 1046
	SNAPPY_ID = 261
	LONGPOSTBOT_ID = 1832
	ZOZBOT_ID = 1833

	PIZZASHILL_ID = 2424
	PROGSTACK_ID = 15531
	CARP_ID = 995
	AEVANN_ID = 1
	LAWLZ_ID = 3833

	IMMUNE_TO_NEGATIVE_AWARDS = {PIZZASHILL_ID, CARP_ID, 23629}

	NOTIFIED_USERS = {
		'aevan': AEVANN_ID,
		'avean': AEVANN_ID,
		' capy': AEVANN_ID,
		'capy ': AEVANN_ID,
		'the rodent': AEVANN_ID,
		'carp': CARP_ID,
		'clit': CARP_ID,
		'pizzashill': PIZZASHILL_ID,

		'joan': 28,
		'pewkie': 28,
		'homocracy': 147,
		'marco': 152,
		'donger': 541,
		'kaam': 1048,
		'august': 1830,
		'klen': 2050,
		'soren': 2546,
		'marseyismywaifu': 3377,
		'mimw': 3377,
		'heymoon': 3635,
		'chiobu': 5214,
		'impassionata': 5800,
		'schizo': 8494,
		'gaslight': 18121,
	}

	GIFT_NOTIF_ID = CARP_ID

	WELCOME_MSG = f"Hi there! It's me, your soon-to-be favorite rDrama user @carpathianflorist here to give you a brief rundown on some of the sick features we have here. You'll probably want to start by following me, though. So go ahead and click my name and then smash that Follow button. This is actually really important, so go on. Hurry.\n\nThanks!\n\nNext up: If you're a member of the media, similarly just shoot me a DM and I'll set about verifying you and then we can take care of your sad journalism stuff.\n\n**FOR EVERYONE ELSE**\n\n Begin by navigating to [the settings page](/settings/profile) (we'll be prettying this up so it's less convoluted soon, don't worry) and getting some basic customization done.\n\n### Themes\n\nDefinitely change your theme right away, the default one (Midnight) is pretty enough, but why not use something *exotic* like Win98, or *flashy* like Tron? Even Coffee is super tasteful and way more fun than the default. More themes to come when we get around to it!\n\n### Avatar/pfp\n\nYou'll want to set this pretty soon. Set the banner too while you're at it. Your profile is important!\n\n### Flairs\n\nSince you're already on the settings page, you may as well set a flair, too. As with your username, you can - obviously - choose the color of this, either with a hex value or just from the preset colors. And also like your username, you can change this at any time. Paypigs can even further relive the glory days of 90s-00s internet and set obnoxious signatures.\n\n### PROFILE ANTHEMS\n\nSpeaking of profiles, hey, remember MySpace? Do you miss autoplaying music assaulting your ears every time you visited a friend's page? Yeah, we brought that back. Enter a YouTube URL, wait a few seconds for it to process, and then BAM! you've got a profile anthem which people cannot mute. Unless they spend 20,000 dramacoin in the shop for a mute button. Which you can then remove from your profile by spending 40,000 dramacoin on an unmuteable anthem. Get fucked poors!\n\n### Dramacoin?\n\nDramacoin is basically our take on the karma system. Except unlike the karma system, it's not gay and boring and stupid and useless. Dramacoin can be spent at [Marsey's Dramacoin Emporium](/shop/awards) on upgrades to your user experience (many more coming than what's already listed there), and best of all on tremendously annoying awards to fuck with your fellow dramautists. We're always adding more, so check back regularly in case you happen to miss one of the announcement posts.\n\nLike karma, dramacoin is obtained by getting upvotes on your threads and comments. *Unlike* karma, it's also obtained by getting downvotes on your threads and comments. Downvotes don't really do anything here - they pay the same amount of dramacoin and they increase thread/comment ranking just the same as an upvote. You just use them to express petty disapproval and hopefully start a fight. Because all votes are visible here. To hell with your anonymity.\n\nDramacoin can also be traded amongst users from their profiles. Note that there is a 3% transaction fee.\n\n### Badges\n\nRemember all those neat little metallic icons you saw on my profile when you were following me? If not, scroll back up and go have a look. And doublecheck to make sure you pressed the Follow button. Anyway, those are badges. You earn them by doing a variety of things. Some of them even offer benefits, like discounts at the shop. A [complete list of badges and their requirements can be found here](/badges), though I add more pretty regularly, so keep an eye on the [changelog](/post/{CHANGELOG_THREAD}).\n\n### Other stuff\n\nWe're always adding new features, and we take a fun-first approach to development. If you have a suggestion for something that would be fun, funny, annoying - or best of all, some combination of all three - definitely make a thread about it. Or just DM me if you're shy. Weirdo. Anyway there's also the [leaderboards](/leaderboard), boring stuff like two-factor authentication you can toggle on somewhere in the settings page (psycho), the ability to save posts and comments, more than a thousand emojis already (most of which are rDrama originals), and on and on and on and on. This is just the basics, mostly to help you get acquainted with some of the things you can do here to make it more easy on the eyes, customizable, and enjoyable. If you don't enjoy it, just go away! We're not changing things to suit you! Get out of here loser! And no, you can't delete your account :na:\n\nI love you.<br>*xoxo Carp* 💋"

	REDDIT_NOTIFS_USERS = {
		'aevann': AEVANN_ID,
		'carpflo': CARP_ID,
		'carpathianflorist': CARP_ID,
		'carpathian florist': CARP_ID,
		'the_homocracy': 147,
	}
elif SITE == 'watchpeopledie.tv':
	NOTIFICATION_SPAM_AGE_THRESHOLD = 0.5 * 86400
	TRUESCORE_MINIMUM = 100

	EMAIL = "wpd@watchpeopledie.tv"
	TELEGRAM_ID = "wpdtv"
	TWITTER_ID = "wpd__tv"
	DEFAULT_TIME_FILTER = "day"

	DESCRIPTION = "People die and this is the place to see it. You only have one life, don't make the mistakes seen here."

	PIN_LIMIT = 4
	WELCOME_MSG = """Hi, you! Welcome to WatchPeopleDie.tv, this really cool site where you can go to watch people die. I'm @CLiTPEELER! If you have any questions about how things work here, or suggestions on how to make them work better than they already do, definitely slide on into my DMs (no fat chicks).\n\nThere's an enormously robust suite of fun features we have here and we're always looking for more to add. Way, way too many to go over in an automated welcome message. And you're probably here for the videos of people dying more than any sort of weird, paradoxical digital community aspect anyway, so I won't bore you with a tedious overview of them. Just head on over to [your settings page](/settings/profile) and have a look at some of the basic profile stuff, at least. You can change your profile picture, username, flair, colors, banners, bio, profile anthem (autoplaying song on your page, like it's MySpace or some shit, hell yeah), CSS, all sorts of things.\n\nOr you can just go back to the main feed and carry on with watching people die. That's what the site is for, after all. Have fun!\n\nAnyway, in closing, WPD is entirely open source. We don't really need new full-time coders or anything, but if you'd like to take a look at our repo - or even submit a PR to change, fix, or add some things - go right ahead! Our codebase lives at https://fsdfsd.net/rDrama/rDrama\n\nWell, that's all. Thanks again for signing up. It's an automated message and all, but I really do mean that. Thank you, specifically. I love you. Romantically. Deeply. Passionately.\n\nHave fun!"""

	FEATURES['BOTS'] = False
	FEATURES['CW_MARKING'] = True
	FEATURES['HAT_SUBMISSIONS'] = False
	FEATURES['NSFW_MARKING'] = False
	FEATURES['PATRON_ICONS'] = True

	PERMS['POST_COMMENT_EDITING'] = 3
	PERMS['MODS_EVERY_HOLE'] = 3
	PERMS['IS_PERMA_PROGSTACKED'] = 4

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
		500: "Internal Server Error. Something went very wrong when trying to fulfill your request. Try refreshing the page. If it still doesn't work, shoot <a href='/@CLiTPEELER'>@CLiTPEELER</a> a message.",
	}

	ERROR_MARSEYS[403] = "marseyconfused"

	BUG_THREAD = 61549

	SIDEBAR_THREAD = 5403
	BANNER_THREAD = 9869
	BADGE_THREAD = 52519
	SNAPPY_THREAD = 67186
	CHANGELOG_THREAD = 56363
	ADMIGGER_THREADS = {SIDEBAR_THREAD, BANNER_THREAD, BADGE_THREAD, SNAPPY_THREAD, CHANGELOG_THREAD, 22937}

	MAX_VIDEO_SIZE_MB = 500
	MAX_VIDEO_SIZE_MB_PATRON = 500

	HOLE_REQUIRED = True

	AUTOJANNY_ID = 1
	SNAPPY_ID = 3
	LONGPOSTBOT_ID = 4
	ZOZBOT_ID = 5

	CARP_ID = 48
	AEVANN_ID = 9
	GTIX_ID = 77694

	GIFT_NOTIF_ID = CARP_ID
	SIGNUP_FOLLOW_ID = CARP_ID

	NOTIFIED_USERS = {
		'aevan': AEVANN_ID,
		'avean': AEVANN_ID,
		' capy': AEVANN_ID,
		'capy ': AEVANN_ID,
		'carp': CARP_ID,
		'clit': CARP_ID,
		'g-tix': GTIX_ID,
		'gtix': GTIX_ID,
	}

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

elif SITE == 'devrama.net':
	AEVANN_ID = 7
	FEATURES['PRONOUNS'] = True
	FEATURES['HOUSES'] = True
	FEATURES['USERS_PERMANENT_WORD_FILTERS'] = True
	PERMS["SITE_SETTINGS"] = 4
	PERMS["ORGIES"] = 4
else: # localhost or testing environment implied
	FEATURES['PRONOUNS'] = True
	FEATURES['HOUSES'] = True
	FEATURES['USERS_PERMANENT_WORD_FILTERS'] = True
	HOLE_BANNER_LIMIT = 69420

HOUSES = ("None","Furry","Femboy","Vampire","Racist","Edgy") if FEATURES['HOUSES'] else ("None")

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

EMOJI_KINDS = ("Marsey", "Platy", "Wolf", "Donkey Kong", "Tay", "Capy", "Carp", "Marsey Flags", "Marsey Alphabet", "Classic", "Rage", "Wojak", "Misc")

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

dkd_begin = datetime.datetime.strptime(f'25/4/{t.year}', '%d/%m/%Y')
dkd_end = datetime.datetime.strptime(f'2/5/{t.year}', '%d/%m/%Y')
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

CHUD_PHRASES = (
	"Trans lives matter",
	"Black lives matter",
	"Black trans lives matter",
	"The future is female",
	"I say this as a feminist ally",
	"I stand with Israel",
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
	"Israeli lives matter",
	"Palestinian lives matter",
	"I love sucking cock",
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

from sqlalchemy.engine.create import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(environ.get("DATABASE_URL").strip(), connect_args={"options": "-c statement_timeout=10000 -c idle_in_transaction_session_timeout=40000"})
db_session = scoped_session(sessionmaker(bind=engine, autoflush=False))

approved_embed_hosts_for_csp = ' '.join(set(x.split('/')[0] for x in approved_embed_hosts))
csp = f"default-src 'none'; frame-ancestors 'none'; form-action 'self'; manifest-src 'self'; worker-src 'self'; base-uri 'self'; font-src 'self'; style-src-elem 'self'; style-src-attr 'unsafe-inline'; style-src 'self' 'unsafe-inline'; script-src-elem 'self' challenges.cloudflare.com; script-src-attr 'none'; script-src 'self' challenges.cloudflare.com; frame-src challenges.cloudflare.com cdpn.io platform.twitter.com rumble.com player.twitch.tv; connect-src 'self' videos.watchpeopledie.tv use1.fptls.com use1.fptls3.com api.fpjs.io; img-src {approved_embed_hosts_for_csp} data:; media-src {approved_embed_hosts_for_csp};"
if not IS_LOCALHOST:
	csp += ' upgrade-insecure-requests;'

with open("includes/content-security-policy", "w") as f:
	f.write(f'add_header Content-Security-Policy "{csp}";')
