from enum import Enum, auto
from os import environ, path

import tldextract
import datetime

DEFAULT_TIME_FILTER = "all"
DEFAULT_THEME = "midnight"
DEFAULT_COLOR = "805ad5"
CURSORMARSEY_DEFAULT = False

POST_BODY_SPAM_SIMILAR_THRESHOLD = 0.5
POST_URL_SPAM_SIMILAR_THRESHOLD = 0.1
POST_SPAM_COUNT_THRESHOLD = 10

COMMENT_BODY_SPAM_SIMILAR_THRESHOLD = 0.2
COMMENT_SPAM_COUNT_THRESHOLD = 40

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
TENOR_KEY = environ.get("TENOR_KEY").strip()
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

DEFAULT_RATELIMIT = "30/minute;400/hour;1000/day"
CASINO_CSS_RATELIMIT = "100/minute;5000/hour;20000/day"
DELETE_RATELIMIT = "10/minute;50/day"

PUSH_NOTIF_LIMIT = 1000

IS_LOCALHOST = SITE == "localhost" or SITE == "127.0.0.1" or SITE.startswith("192.168.") or SITE.endswith(".local")

if SITE in {'rdrama.net', 'watchpeopledie.tv'}:
	SITE_IMAGES = 'i.' + SITE
elif SITE == 'staging.rdrama.net':
	SITE_IMAGES = 'i.rdrama.net'
else:
	SITE_IMAGES = SITE

if SITE == 'watchpeopledie.tv':
	SITE_VIDEOS = 'videos.watchpeopledie.tv'
else:
	SITE_VIDEOS = f'{SITE}/videos'

if IS_LOCALHOST:
	SITE_FULL = f'http://{SITE}'
	SITE_FULL_IMAGES = f'http://{SITE_IMAGES}'
	SITE_FULL_VIDEOS = f'http://{SITE_VIDEOS}'
else:
	SITE_FULL = f'https://{SITE}'
	SITE_FULL_IMAGES = f'https://{SITE_IMAGES}'
	SITE_FULL_VIDEOS = f'https://{SITE_VIDEOS}'

if SITE == 'marsey.world':
	SITE_FULL_IMAGES = f'https://i.watchpeopledie.tv'

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

	'whose': 'thats',
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

CATEGORIES_ICONS = {}
CATEGORIES_HOLES = {}

TAGLINES = ()

if SITE_NAME == 'rDrama':
	PERMS = { # Minimum admin_level to perform action.
		'HOLE_CREATE': 0,

		'POST_BETS': 1,
		'POST_BETS_DISTRIBUTE': 1,
		'IGNORE_EDITING_LIMIT': 1,
		'ADMIN_MOP_VISIBLE': 1,
		'WARN_ON_FAILED_LOGIN': 1,
		'PINNING_COMMENTS': 1,
		'PINNING_POSTS': 1,
		'ORGIES': 1,
		'CHAT_MUTE': 1,

		'POST_COMMENT_MODERATION': 2,
		'NUKE_USER': 2,
		'ADMIN_HOME_VISIBLE': 2,
		'REPORTS_REMOVE': 2,
		'BYPASS_ANTISPAM_CHECKS': 2,
		'VIEW_ALTS': 2,
		'VIEW_PRIVATE_PROFILES': 2,
		'POST_COMMENT_DISTINGUISH': 2,
		'VIEW_RESTRICTED_HOLES': 2,
		'BYPASS_SITE_READ_ONLY_MODE': 2,
		'BYPASS_UNDER_SIEGE_MODE': 2,
		'BYPASS_CHAT_TRUESCORE_REQUIREMENT': 2,
		'MESSAGE_BLOCKED_USERS': 2,
		'USER_BAN': 2,
		'USER_SHADOWBAN': 2,
		'USER_CHUD': 2,
		'VIEW_MODMAIL': 2,
		'NOTIFICATIONS_MODMAIL': 2,
		'VIEW_ACTIVE_USERS': 2,
		'VIEW_ALT_VOTES': 2,
		'VIEW_LAST_ACTIVE': 2,
		'ENABLE_VOTE_BUTTONS_ON_USER_PAGE': 2,
		'NOTIFICATIONS_MODERATOR_ACTIONS': 2,
		'USER_BADGES': 2,
		'ADMIN_NOTES': 2,
		'IS_PERMA_PROGSTACKED': 2,
		'USER_CHANGE_FLAIR': 2,
		'POST_COMMENT_INFINITE_PINGS': 2,
		'DELETE_MEDIA': 2,
		'DOMAINS_BAN': 2,
		'NOTIFICATIONS_FROM_SHADOWBANNED_USERS': 2,
		'USE_ADMIGGER_THREADS': 2,
		'MARK_EFFORTPOST': 2,
		'EDIT_RULES': 2,

		'ADMIN_ACTIONS_REVERT': 3,
		'SITE_SETTINGS': 3,
		'SITE_CACHE_PURGE_CDN': 3,
		'MODERATE_PENDING_SUBMITTED_ASSETS': 3,
		'UPDATE_ASSETS': 3,
		'PUBLISH_OTHERS_POSTS': 3,

		'POST_COMMENT_EDITING': 4,
		'PROGSTACK': 4,
		'UNDO_AWARD_PINS': 4,
		'USER_BLACKLIST': 4,
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
		'CHANGE_UNDER_SIEGE': 4,
		'VIEW_EMAILS': 4,
		'VIEW_CHATS': 4,
		'VIEW_CHAT_LIST': 4,
		'USER_LINK': 4,
		'ADMIN_ADD': 4,
		'ADMIN_REMOVE': 4,
		'POST_IN_H_ANNOUNCEMENTS': 4,
		'MODS_EVERY_HOLE': 4,
		'MODS_EVERY_GROUP': 4,
		'INFINITE_CURRENCY': 4,
		'VIEW_VERSIONS': 4,

		'IMMUNE_TO_DEFLECTIONS': 5,

		'CSS_DISABLED': 99,
		'VIEW_IPS': 99,
		'EXEMPT_FROM_IP_LOGGING': 99,
		'NOTIFICATIONS_SPECIFIC_WPD_COMMENTS': 99,
	}
else:
	PERMS = { # Minimum admin_level to perform action.
		'POST_COMMENT_MODERATION': 1,
		'ADMIN_MOP_VISIBLE': 1,
		'ADMIN_HOME_VISIBLE': 1,
		'REPORTS_REMOVE': 1,
		'CHAT_MUTE': 1,
		'BYPASS_ANTISPAM_CHECKS': 1,
		'VIEW_ALTS': 1,
		'VIEW_PRIVATE_PROFILES': 1,
		'POST_COMMENT_DISTINGUISH': 1,
		'BYPASS_SITE_READ_ONLY_MODE': 1,
		'BYPASS_CHAT_TRUESCORE_REQUIREMENT': 1,
		'VIEW_LAST_ACTIVE': 1,
		'ADMIN_NOTES': 1,
		'WARN_ON_FAILED_LOGIN': 1,
		'PINNING_COMMENTS': 1,
		'VIEW_VERSIONS': 1,

		'USER_BAN': 2,

		'NUKE_USER': 3,
		'PINNING_POSTS': 3,
		'POST_BETS': 3,
		'POST_BETS_DISTRIBUTE': 3,
		'IGNORE_EDITING_LIMIT': 3,
		'VIEW_RESTRICTED_HOLES': 3,
		'BYPASS_UNDER_SIEGE_MODE': 3,
		'NOTIFICATIONS_SPECIFIC_WPD_COMMENTS': 3,
		'MESSAGE_BLOCKED_USERS': 3,
		'USER_SHADOWBAN': 3,
		'USER_CHUD': 3,
		'VIEW_MODMAIL': 3,
		'NOTIFICATIONS_MODMAIL': 3,
		'VIEW_ACTIVE_USERS': 3,
		'VIEW_ALT_VOTES': 3,
		'ENABLE_VOTE_BUTTONS_ON_USER_PAGE': 3,
		'NOTIFICATIONS_MODERATOR_ACTIONS': 3,
		'EXEMPT_FROM_IP_LOGGING': 3,
		'USER_BADGES': 3,
		'IS_PERMA_PROGSTACKED': 3,
		'USER_CHANGE_FLAIR': 3,
		'POST_COMMENT_INFINITE_PINGS': 3,
		'ORGIES': 3,
		'DELETE_MEDIA': 3,
		'ADMIN_ACTIONS_REVERT': 3,
		'DOMAINS_BAN': 3,
		'EDIT_RULES': 3,
		'SITE_SETTINGS': 3,
		'SITE_CACHE_PURGE_CDN': 3,
		'NOTIFICATIONS_FROM_SHADOWBANNED_USERS': 3,
		'USE_ADMIGGER_THREADS': 3,
		'MODERATE_PENDING_SUBMITTED_ASSETS': 3,
		'UPDATE_ASSETS': 3,
		'MARK_EFFORTPOST': 3,
		'CSS_DISABLED': 3,
		'HOLE_CREATE': 3,
		'MODS_EVERY_HOLE': 3,
		'MODS_EVERY_GROUP': 3,
		'POST_COMMENT_EDITING': 3,
		'PROGSTACK': 3,
		'UNDO_AWARD_PINS': 3,
		'USER_BLACKLIST': 3,
		'VIEW_PATRONS': 3,
		'BLACKJACK_NOTIFICATIONS': 3,
		'IGNORE_BADGE_BLACKLIST': 3,
		'ENABLE_DM_MEDIA': 3,
		'SEE_GHOST_VOTES': 3,
		'SITE_OFFLINE_MODE': 3,
		'IGNORE_DOMAIN_BAN': 3,
		'USER_RESET_PASSWORD': 3,
		'CLAIM_REWARDS_ALL_USERS': 3,
		'IGNORE_AWARD_IMMUNITY': 3,
		'INSERT_TRANSACTION': 3,
		'APPS_MODERATION': 3,
		'CHANGE_UNDER_SIEGE': 3,
		'VIEW_IPS': 3,
		'VIEW_EMAILS': 3,
		'USER_LINK': 3,
		'ADMIN_ADD': 3,
		'ADMIN_REMOVE': 3,
		'POST_IN_H_ANNOUNCEMENTS': 3,
		'VIEW_CHATS': 3,
		'PUBLISH_OTHERS_POSTS': 3,

		'VIEW_CHAT_LIST': 4,
		'INFINITE_CURRENCY': 4,

		'IMMUNE_TO_DEFLECTIONS': 99,
	}

FEATURES = {
	'MARSEYBUX': True,
	'AWARDS': True,
	'CHAT': True,
	'PINS': True,
	'PRONOUNS': True,
	'BADGES': True,
	'HATS': True,
	'HOUSES': True,
	'GAMBLING': True,
	'USERS_PROFILE_BANNER': True,
	'USERS_PROFILE_BODYTEXT': True,
	'USERS_PROFILE_SONG': True,
	'USERS_PERMANENT_WORD_FILTERS': True,
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

DEFAULT_PRONOUNS = None

GET_HELP_MESSAGE = "Hi there,\n\nA [concerned user](/id/{vid}) reached out to us about you.\n\nWhen you're in the middle of something painful, it may feel like you don't have a lot of options. But whatever you're going through, you deserve help and there are people who are here for you.\n\nThere are resources available in your area that are free, confidential, and available 24/7:\n\n- Call, Text, or Chat with Canada's [Crisis Services Canada](https://988.ca).\n\n- Call, Email, or Visit the UK's [Samaritans](https://www.samaritans.org).\n\n- Text CHAT to America's [Crisis Text Line](https://www.crisistextline.org) at 741741.\n\nIf you don't see a resource in your area above, the moderators keep a comprehensive list of resources and hotlines organized by location. Find Someone Now.\n\nIf you think you may be depressed or struggling in another way, don't ignore it or brush it aside. Take yourself and your feelings seriously, and reach out to someone.\n\nIt may not feel like it, but you have options. There are people available to listen to you, and ways to move forward.\n\nYour fellow users care about you and there are people who want to help."

if SITE_NAME == 'rDrama':
	FEATURES['BLOCK_MUTE_EXILE_EXPIRY'] = True

	DEFAULT_PRONOUNS = 'they/them'

	CURSORMARSEY_DEFAULT = True
	DEFAULT_THEME = "dramblr"
	DEFAULT_COLOR = "f04bec"

	patron = "Paypig"

	TAGLINES = (
		# "largest cat pics site",
		# "largest online LGBTQ+ club",
		# "largest online furfest",
		# "largest basket-weaving forum",
		# "largest autism support group",
		# "largest aztec heritage forum",
		# "official George Soros fanclub",
		# "CCP's official newspaper",
		# "Nintendo gamers only",
		# "donkey kong country",
		# "as seen in WI v. Brooks 2022",
		# "#1 used marsuit exchange",
		# "incel matchmaking services",
		# "AgainstHateSubreddits offsite",
		# "exotic pets for sale",
		# "cheap airfare and hotels",
		# "the back page of the internet",
		# "socialist discourse & dating",
		# "DIY estrogen recipes",
		# "#1 guide to transitioning in Texas",
		# "Nintendo Switch ROMs",
		# "erectile dysfunction treatments",
		# "managing incontinence",
		# "Quran study group",
		# "Israeli Power Generator",
		# "/u/bardfinn's fan club",
		# "world's oldest website",
		# "we like trains!",
		# "watch Family Guy online",
		# "r34 Velma vore collection",
		# "like Reddit but worse",
		# "be mindful not to set off the Lunk Alarm",
		# "26000 carp alts, 6 bots, and you",
		# "expired meat enthusiasts",
		# "the sign is a subtle joke",
		# "Rafe Judkins HATE Club",
		# "high IQ individuals, high IQ discourse",
		# "coping with early male baldness",
		# "Chtorrr is NOT trans, just very ugly",
		# "don't google steve huffman 2003 frat party",
		# "Furry Liberation Front",
		# "a JIDF asset",
		# "Taco Bell secret menu items",
		# "how to ask your sister out on a date",
		# "this is Incel Country, foid",
		# "Ben 10 guro mixtapes & OC fics",
		# "a Netflix Original Series",
		# "gently used condom trading",
		# "best easy slow cooker hot chili recipe",
		# "Dasha please notice us",
		# "the worst of all possible worlds",
		# "Columbia University students only",
		# "the Solution to the Yakubian Question",
		# "elbows too pointy",
		# "Star Wars leaks, rumors, and more",
		# "web's best deals on SodaStream refills",
		# "70% off your first order!",
		# "Haitian Pride Worldwide",
		# "second largest Marsey Cat fansite",
		# "why is that fish so fucking ugly",
		# "a global superpower by 2020",
		# "all-natural homeopathic herpes treatment",
		# "vegan dating",
		# "Come for the cats. Stay for the empathy.",
		# "gay cat dating site",
		# "you WILL be trans",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kamala 2024",
		"Kaamrev 2024",
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
		'lit',
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
		'kamala',
		'countryclub',
		'meowr',
		'spongebob',
		'erstory',
	}

	OFFSITE_NOTIF_QUERIES.update({'marsey', 'r/drama', 'justice4darrell', 'cringetopia.org', 'rdramanet.github.io'})

elif SITE_NAME == 'WPD':
	FEATURES['PATRON_ICONS'] = True
	FEATURES['IP_LOGGING'] = True
	FEATURES['USERS_PERMANENT_WORD_FILTERS'] = False
	FEATURES['NSFW_MARKING'] = False
	FEATURES['HAT_SUBMISSIONS'] = False

	TAGLINES = (
		"people dying and cartoon cats <3",
		"The Antisocial Network",
		"come for the gore, stay for the drama",
		"NO ADS NO PORN JUST HORRIFYING SHIT",
		"egg gang egg gang egg gang egg gang",
		"Plex did 9/11",
		"clipter help video wont playing",
		"largest collection of donkey kong emojis",
		"MOM I SWEAR IT'S ABOUT HAIR DYE",
		"bringing peace to the Middle East ",
		"you're just here for the articles",
		"Pokemon FAQs, Trading & More",
		"it's NOT just a phase",
		"please stop reporting Snappy",
		"(sped up nightcore bass-boosted mix)",
		"the ponies did nothing wrong",
		"like TheYNC but not shit",
		"go back to TikTok ",
		"Marsey the Cat's one true home!",
		"is not your therapist",
		"WAKEUPWAKEUPWAKEUPYOUHAVETOWAKEUP",
		"Log off. Call your dad. Go to church.",
		"Taylor Swift for President ",
		"please remember to stay hydrated",
		"Columbine unreleased GoPro footage 4K",
		"mistakes were made.",
		"be sure to drink your Ovaltine",
		"enter now to win reservations at Dorsia!",
		"Mergers & Acquisitions",
		"Enterprise Cloud-Hosting Solutions",
		"free ps5 giveaways every hour",
		"pairs well w/ fava beans & a nice chianti",
		"please help me theyve got me locked in th",
		"home of the Goodburger",
		"shouldn't you be sleeping?",
		"are your doors locked?",
		"don't look out the window.",
		"for fatherless women",
		"Microwave Cooking For One",
		"someone drank their piss here",
		"Equestria roleplay & fanfiction",
		"the bad ending",
		"managing explosive diarrhea at work",
		"heeeeeeeere's Marsey! 😈",
		"I want to play a game",
		"we all float on here",
		"your friend to the end",
		"these statements not evaluated by the FDA",
		"WikiHow: easily remove bloodstains",
		"lathe operator safety tips & tricks",
		"now hiring experienced OTR drivers",
		"#1 distributor of illegal fireworks",
		"please put your pants back on",
		"did you hear that?",
		"Misandry: A Moral Imperative",
		"40% ABV",
		"morbid curiosity? more like morbid obesity",
		"The Truth About Stephen Paddock",
		"Epstein killed himself for h/suicide",
		"not affiliated with AllTrails.com",
		"30-minute full body workouts",
		"Family Guy Funny Moments #82",
	)

	OFFSITE_NOTIF_QUERIES.update({'marsey', 'watchpeopledie', 'makemycoffin'})

	CATEGORIES_ICONS = {
		'Death':'skull',
		'Gore':'droplet',
		'Community':'users',
		'Active Conflicts':'person-rifle',
	}

	CATEGORIES_HOLES = {
		'Death': ('Accident','Animal','Beating','Beheading','Bladed','Burning','Cartel','Combat','Compilation','Disaster','Drowning','Electricity','Execution','Explosions','Falling','Industrial','ISIS','Maiming','Police','Shooting','Suicide','Vehicle','Other'),
		'Gore': ('Aftermath','Fights','Gore','Medical','Request','SelfHarm'),
		'Community': ('Art','Discussion','Meta','Music','Pets','Social'),
		'Active Conflicts': ('Slavshit','Sandshit'),
	}


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
	"Impressive. Normally people with such severe developmental disabilities struggle to write much more than a sentence or two. You really have exceeded our expectations for the writing portion. Sadly the coherency of your writing, along with your abilities in the social skills and reading portions, are far behind your peers with similar disabilities.",
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
	"Damn, you're really mad over this, but thanks for the effort you put into typing that all out! Sadly I won't read it at all.",
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
	"https://i.rdrama.net/images/165178832073224.webp",
	"None of these words are in the Bible",
	"https://i.rdrama.net/images/17189081272030811.webp",
	"https://i.rdrama.net/images/17189984660267773.webp",
	"not reading your substack",
	"https://i.rdrama.net/images/16758166234569614.webp",
	"https://i.rdrama.net/images/16763687631229467.webp",
	"> Blah Blah blah blah\n\n> yap yap yap yap\n\nDidnt read",
	"https://i.rdrama.net/images/17194996128531878.webp",
	"what is bro yapping about :marseyskull:",
	"https://i.rdrama.net/images/17215821618015614.webp",
	"Get raped faggot",
	"https://i.rdrama.net/images/17224743379194624.webp",
	"https://i.rdrama.net/images/1721617343773228.webp",
	"https://i.rdrama.net/images/16844996389783444.webp",
	"https://i.rdrama.net/images/167356368370703.webp",
	"When you look in the mirror, can you tell that you're stupid?",
	"https://i.rdrama.net/images/17224404628678622.webp",
	"Praying Trump gets elected so you get sent to some kind of concentration camp",
	"Didn't read",
	"?",
	"https://i.rdrama.net/images/17225430325674362.webp",
	"tldr?",
	"ok",
	"no way",
	":#marseydoit:",
	"I don't care, sorry boo",
	":#marseywords:",
	"https://i.rdrama.net/images/17227070857606635.webp",
	"https://i.rdrama.net/images/1722961672231166.webp",
	"https://rdrama.net/videos/17237461971773005.mp4",
	"I don't get it :marseyconfused:",
	"I have zero intentions of reading all of that crap",
	"Ok retard",
	"https://i.rdrama.net/images/17238973634696946.webp",
	":#bidenshocked:",
	"https://i.rdrama.net/images/17243457519662082.webp",
	"omg nobody cares??",
	"have sex incel",
	"https://i.rdrama.net/images/17295407689104028.webp",
	"Seek help.",
	" ",
	"https://i.rdrama.net/images/17299120560630205.webp",
	"https://i.rdrama.net/images/17305040437598283.webp",
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
COMMENT_SORTS = COMMENT_SORTS | {"saves": "save"}

USER_SNAPPY_QUOTES_LENGTH = 1000

################################################################################
### COLUMN INFO
################################################################################

HOLE_NAME_COLUMN_LENGTH = 25
HOLE_SIDEBAR_COLUMN_LENGTH = 10000
HOLE_SIDEBAR_HTML_COLUMN_LENGTH = 20000
HOLE_SNAPPY_QUOTES_LENGTH = 50000
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
	406: "The resource identified by the request is only capable of generating response entities which have content characteristics not acceptable according to the accept headers sent in the request.",
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
	406: "THIS IS AN 18+ WEBSITE",
	409: "Cumflict",
	410: "Gone... and Forgotten",
	413: "Gayload Too Large",
	415: "Weird Media Type",
	418: "We need you to login",
	429: "Too Many Requests",
	500: "Balls-Deep Server Error",
}

ERROR_MSGS = {
	400: "That request was bad and you should feel bad.",
	401: "What you're trying to do requires an account. I think. The original error message said something about a castle and I hated that. If you see this error and you're logged into an account, something went pretty wrong somewhere.",
	403: "YOU AREN'T WELCOME HERE GO AWAY",
	404: "Someone typed something wrong and it was probably you, please do better.",
	405: "idk how anyone gets this error but if you see this, remember to follow @carpathianflorist<br>the original error text here talked about internet gremlins and wtf",
	406: "You have been banned for being underage.<br>If this was in error, please contact the admins below.",
	409: "There's a conflict between what you're trying to do and what you or someone else has done and because of that you can't do what you're trying to do. So maybe like... don't try and do that? Sorry not sorry",
	410: "You were too slow. The link FUCKING DIED. Request a new one and be more efficient.",
	413: "That's a heckin' chonker of a file! Please make it smaller or maybe like upload it somewhere else idk<br>jc wrote this one hi jc!<br>- carp",
	415: "Please upload only Image, Video, or Audio files!",
	418: f'''{SITE} is currently being DDOSed. Who is behind it? The Russians? The deep state? The communists? <i>You?</i><br>We have no idea, but you'll need to either <a href="/login">log in</a> or <a href="/signup">create an account</a> to see anything while this is ongoing.<br>Sorry!''',
	429: "go spam somewhere else nerd",
	500: "Hiiiii it's carp! I think this error means that there's a timeout error. And I think that means something took too long to load so it decided not to work at all. If you keep seeing this on the same page <i>but not other pages</i>, then something is probably wrong with that specific function. It may not be called a function, but that sounds right to me. Anyway, <s>ping me and I'll whine to someone smarter to fix it. Don't bother them.</s> <b>After a year and a half of infuriating pings, the new instructions are to quit whining and just wait until it works again oh my god shut UP.</b><br><br> Thanks ily &lt;3",
}

ERROR_MARSEYS = {
	400: "marseybrainlet",
	401: "marseydead",
	403: "marseytroll",
	404: "marseyconfused",
	405: "marseyretard",
	406: "marseynominers",
	409: "marseynoyou",
	410: "marseyrave",
	413: "marseychonker2",
	415: "marseydetective",
	418: "marseyhacker",
	429: "marseyrentfree",
	500: "marseycarp3",
}

EMOJI_SRCS = ['files/assets/emojis.csv']

PIN_LIMIT = 10
POST_TITLE_LENGTH_LIMIT = 500 # do not make larger without altering the table
POST_TITLE_HTML_LENGTH_LIMIT = 5000 # do not make larger without altering the table

def POST_BODY_LENGTH_LIMIT(v):
	if v.patron: return 100000
	return 50000

POST_BODY_HTML_LENGTH_LIMIT = 200000 # do not make larger without altering the table

COMMENT_BODY_LENGTH_LIMIT = 10000 # do not make larger without altering the table
COMMENT_BODY_HTML_LENGTH_LIMIT = 40000 # do not make larger without altering the table
CSS_LENGTH_LIMIT = 50000 # do not make larger without altering the tables
COMMENT_MAX_DEPTH = 200
TRANSFER_MESSAGE_LENGTH_LIMIT = 200 # do not make larger than COMMENT_BODY_LENGTH_LIMIT
MIN_REPOST_CHECK_URL_LENGTH = 9 # also change the constant in checkRepost() of submit.js
HOLE_BANNER_LIMIT = 10

BIO_FRIENDS_ENEMIES_LENGTH_LIMIT = 5000 # do not make larger without altering the table
BIO_FRIENDS_ENEMIES_HTML_LENGTH_LIMIT = 20000 # do not make larger without altering the table

BAN_REASON_LENGTH_LIMIT = 500
BAN_REASON_HTML_LENGTH_LIMIT = 5000 # do not make larger without altering the table

COSMETIC_AWARD_COIN_AWARD_PCT = 0.50

TRUESCORE_MINIMUM = 0

LOGGEDIN_ACTIVE_TIME = 15 * 60
PFP_DEFAULT_MARSEY = True
NEW_USER_AGE = 7 * 86400
NOTIFICATION_SPAM_AGE_THRESHOLD = 0
COMMENT_SPAM_LENGTH_THRESHOLD = 0

DEFAULT_UNDER_SIEGE_THRESHOLDS = {
	"chat": 0,
	"normal comment": 0,
	"wall comment": 0,
	"post": 0,
	"report": 0,
	"modmail": 0,
	"message": 0,
	"ping group application": 0,
}

HOLE_REQUIRED = False
HOLE_COST = 0
GROUP_COST = 10000
HOLE_INACTIVITY_DEATH = False

BOT_SYMBOL_HIDDEN = set()
EXEMPT_FROM_SPAM_FILTER = set()

AUTOJANNY_ID = 1
SNAPPY_ID = 2
LONGPOSTBOT_ID = 3
ZOZBOT_ID = 4

PIZZASHILL_ID = 0
CARP_ID = 0
AEVANN_ID = 0
GTIX_ID = 0
FISHY_ID = 0
CROSSTALK_ID = 0

SIGNUP_FOLLOW_ID = 0
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

SNAPPY_SUBMIT_THREAD = 0
EMOJI_UPDATE_THREAD = 0
EMOJI_COMMISSION_THREAD = 0

MAX_IMAGE_SIZE_BANNER_RESIZED_MB = 2
MAX_IMAGE_AUDIO_SIZE_MB = 8
MAX_IMAGE_AUDIO_SIZE_MB_PATRON = 16
MAX_VIDEO_SIZE_MB = 32
MAX_VIDEO_SIZE_MB_PATRON = 100

PAGE_SIZE = 25
LEADERBOARD_LIMIT = PAGE_SIZE

HOUSE_JOIN_COST = 500
HOUSE_SWITCH_COST = 2000

PATRON_BADGES = (22,23,24,25,26,27,28,257,258,259,260,261,294)

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

TIER_TO_MUL = {
	2: 500,
	3: 550,
	4: 600,
	5: 650,
	6: 700,
	7: 750,
	8: 800,
}

BADGE_BLACKLIST = PATRON_BADGES + ( # only grantable by admins higher than PERMS['IGNORE_BADGE_BLACKLIST']
	1, 2, 6, 10, 11, 12, # Alpha, Verified Email, Beta, Recruiter x3
	16, 17, 143, # Marsey Artist x3
	94, 95, 96, 97, 98, 109, 67, 68, 83, 84, 87, 90, 179, 185, # Award Status except Y'all-seeing eye
	137, # Lottery Winner
)

if SITE in {'rdrama.net', 'staging.rdrama.net'}:
	NOTIFICATION_SPAM_AGE_THRESHOLD = 0.5 * 86400

	TELEGRAM_ID = "rdramanet"
	TWITTER_ID = "rdramanet"
	DEFAULT_TIME_FILTER = "day"

	BUG_THREAD = 18459

	BADGE_THREAD = 37833
	SNAPPY_THREAD = 37749
	CHANGELOG_THREAD = 165657
	POLL_THREAD = 79285
	ADMIGGER_THREADS = {BADGE_THREAD, SNAPPY_THREAD, CHANGELOG_THREAD, POLL_THREAD, 166300, 187078, 258966}

	SNAPPY_SUBMIT_THREAD = 33652
	EMOJI_UPDATE_THREAD = 103085
	EMOJI_COMMISSION_THREAD = 37677

	TRUESCORE_MINIMUM = 10

	HOLE_COST = 100000
	HOLE_INACTIVITY_DEATH = True

	BOT_SYMBOL_HIDDEN = {12125, 16049, 23576}
	EXEMPT_FROM_SPAM_FILTER = BOT_SYMBOL_HIDDEN | {1703, 4003, 13427, 15014, 24197, 25816}

	EXEMPT_FROM_EDITING_LIMIT = {1048}

	AUTOJANNY_ID = 1046
	SNAPPY_ID = 261
	LONGPOSTBOT_ID = 1832
	ZOZBOT_ID = 1833

	PIZZASHILL_ID = 2424
	PROGSTACK_ID = 15531
	CARP_ID = 995
	AEVANN_ID = 1
	CROSSTALK_ID = 26878

	CURRENCY_TRANSFER_ID = CARP_ID

	IMMUNE_TO_NEGATIVE_AWARDS = {PIZZASHILL_ID, CARP_ID, 23629}

	PINNED_POSTS_IDS = {
		PIZZASHILL_ID: 1,
		28: 1, #Joan_Wayne_Gacy
		1096: 1, #xa15428
		2008: 1, #transgirltradwife
		4999: 1, #justcool393
		8491: 1, #TrappySaruh
		12451: 1, #rosemulet
		13452: 1, #Sammael-Beliol
		16012: 1, #realspez
		18308: 1, #gee891
		24031: 1, #PrettyKitty
		24456: 1, #PreyingMantits
		3336: 24, #Snally
	}

	WELCOME_MSG = f"Hi there! It's me, your soon-to-be favorite rDrama user @carpathianflorist here to give you a brief rundown on some of the sick features we have here. You'll probably want to start by following me, though. So go ahead and click my name and then smash that Follow button. This is actually really important, so go on. Hurry.\n\nThanks!\n\nNext up: If you're a member of the media, similarly just shoot me a DM and I'll set about verifying you and then we can take care of your sad journalism stuff.\n\n**FOR EVERYONE ELSE**\n\n Begin by navigating to [the settings page](/settings/personal) and getting some basic customization done.\n\n### Themes\n\nDefinitely change your theme right away, the default one (Midnight) is pretty enough, but why not use something *exotic* like Win98, or *flashy* like Tron? Even Coffee is super tasteful and way more fun than the default. More themes to come when we get around to it!\n\n### Avatar/pfp\n\nYou'll want to set this pretty soon. Set the banner too while you're at it. Your profile is important!\n\n### Flairs\n\nSince you're already on the settings page, you may as well set a flair, too. As with your username, you can - obviously - choose the color of this, either with a hex value or just from the preset colors. And also like your username, you can change this at any time. Paypigs can even further relive the glory days of 90s-00s internet and set obnoxious signatures.\n\n### PROFILE ANTHEMS\n\nSpeaking of profiles, hey, remember MySpace? Do you miss autoplaying music assaulting your ears every time you visited a friend's page? Yeah, we brought that back. Enter a YouTube URL, wait a few seconds for it to process, and then BAM! you've got a profile anthem which people cannot mute. Unless they spend 20,000 dramacoin in the shop for a mute button. Which you can then remove from your profile by spending 40,000 dramacoin on an unmuteable anthem. Get fucked poors!\n\n### Dramacoin?\n\nDramacoin is basically our take on the karma system. Except unlike the karma system, it's not gay and boring and stupid and useless. Dramacoin can be spent at [Marsey's Dramacoin Emporium](/shop/awards) on upgrades to your user experience (many more coming than what's already listed there), and best of all on tremendously annoying awards to fuck with your fellow dramautists. We're always adding more, so check back regularly in case you happen to miss one of the announcement posts.\n\nLike karma, dramacoin is obtained by getting upvotes on your threads and comments. *Unlike* karma, it's also obtained by getting downvotes on your threads and comments. Downvotes don't really do anything here - they pay the same amount of dramacoin and they increase thread/comment ranking just the same as an upvote. You just use them to express petty disapproval and hopefully start a fight. Because all votes are visible here. To hell with your anonymity.\n\nDramacoin can also be traded amongst users from their profiles. Note that there is a 3% transaction fee.\n\n### Badges\n\nRemember all those neat little metallic icons you saw on my profile when you were following me? If not, scroll back up and go have a look. And doublecheck to make sure you pressed the Follow button. Anyway, those are badges. You earn them by doing a variety of things. Some of them even offer benefits, like discounts at the shop. A [complete list of badges and their requirements can be found here](/badges), though I add more pretty regularly, so keep an eye on the [changelog](/post/{CHANGELOG_THREAD}).\n\n### Other stuff\n\nWe're always adding new features, and we take a fun-first approach to development. If you have a suggestion for something that would be fun, funny, annoying - or best of all, some combination of all three - definitely make a thread about it. Or just DM me if you're shy. Weirdo. Anyway there's also the [leaderboards](/leaderboard), boring stuff like two-factor authentication you can toggle on somewhere in the settings page (psycho), the ability to save posts and comments, more than a thousand emojis already (most of which are rDrama originals), and on and on and on and on. This is just the basics, mostly to help you get acquainted with some of the things you can do here to make it more easy on the eyes, customizable, and enjoyable. If you don't enjoy it, just go away! We're not changing things to suit you! Get out of here loser! And no, you can't delete your account :na:\n\nI love you.<br>*xoxo Carp* 💋"
elif SITE in {'watchpeopledie.tv', 'marsey.world'}:
	NOTIFICATION_SPAM_AGE_THRESHOLD = 0.5 * 86400
	TRUESCORE_MINIMUM = 100

	EMAIL = "wpd@watchpeopledie.tv"
	TELEGRAM_ID = "wpdtv"
	TWITTER_ID = "wpd__tv"
	DEFAULT_TIME_FILTER = "day"

	DESCRIPTION = "People die and this is the place to see it. You only have one life, don't make the mistakes seen here."

	WELCOME_MSG = """Hi, you! Welcome to WatchPeopleDie.tv, this really cool site where you can go to watch people die. I'm @CLiTPEELER! If you have any questions about how things work here, or suggestions on how to make them work better than they already do, definitely slide on into my DMs (no fat chicks).\n\nThere's an enormously robust suite of fun features we have here and we're always looking for more to add. Way, way too many to go over in an automated welcome message. And you're probably here for the videos of people dying more than any sort of weird, paradoxical digital community aspect anyway, so I won't bore you with a tedious overview of them. Just head on over to [your settings page](/settings/personal) and have a look at some of the basic profile stuff, at least. You can change your profile picture, username, flair, colors, banners, bio, profile anthem (autoplaying song on your page, like it's MySpace or some shit, hell yeah), CSS, all sorts of things.\n\nOr you can just go back to the main feed and carry on with watching people die. That's what the site is for, after all. Have fun!\n\nAnyway, in closing, WPD is entirely open source. We don't really need new full-time coders or anything, but if you'd like to take a look at our repo - or even submit a PR to change, fix, or add some things - go right ahead! Our codebase lives at https://fsdfsd.net/rDrama/rDrama\n\nWell, that's all. Thanks again for signing up. It's an automated message and all, but I really do mean that. Thank you, specifically. I love you. Romantically. Deeply. Passionately.\n\nHave fun!"""

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
		406: "You have been banned for being underage.<br>If this was in error, please contact the admins below.",
		409: "There's a conflict between what you're trying to do and what you or someone else has done and because of that you can't do what you're trying to do.",
		410: "This link is dead. Request a new one to try again.",
		413: "You need to upload a smaller file please.",
		415: "Please upload only Image, Video, or Audio files!",
		418: f'''{SITE} is currently being DDOSed. Who is behind it? The Russians? The deep state? The communists? <i>You?</i><br>We have no idea, but you'll need to either <a href="/login">log in</a> or <a href="/signup">create an account</a> to see anything while this is ongoing.<br>Sorry!''',
		429: "Please wait a bit before doing that.",
		500: "Internal Server Error. Something went very wrong when trying to fulfill your request. Try refreshing the page. If it still doesn't work, shoot <a href='/@CLiTPEELER'>@CLiTPEELER</a> a message.",
	}

	ERROR_MARSEYS[500] = "marseylaptopangry2"

	BUG_THREAD = 61549

	BADGE_THREAD = 52519
	SNAPPY_THREAD = 67186
	CHANGELOG_THREAD = 56363
	POLL_THREAD = 22937
	ADMIGGER_THREADS = {BADGE_THREAD, SNAPPY_THREAD, CHANGELOG_THREAD, POLL_THREAD, 106665}

	SNAPPY_SUBMIT_THREAD = 140010
	EMOJI_UPDATE_THREAD = 140014
	EMOJI_COMMISSION_THREAD = 140015

	MAX_VIDEO_SIZE_MB = 500
	MAX_VIDEO_SIZE_MB_PATRON = 500

	HOLE_REQUIRED = True

	EXEMPT_FROM_EDITING_LIMIT = {12046,83848,395296}

	AUTOJANNY_ID = 1
	SNAPPY_ID = 3
	LONGPOSTBOT_ID = 0
	ZOZBOT_ID = 5

	AEVANN_ID = 9
	GTIX_ID = 77694
	FISHY_ID = 1391252	
	CARP_ID = 48

	SIGNUP_FOLLOW_ID = CARP_ID
	CURRENCY_TRANSFER_ID = CARP_ID

	EXEMPT_FROM_SPAM_FILTER = {1718156, 1783542}

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
		"chat": 1440,
		"normal comment": 10,
		"wall comment": 1440,
		"post": 1440,
		"report": 1440,
		"modmail": 1440,
		"message": 1440,
		"ping group application": 1440,
	}

	GET_HELP_MESSAGE = "Hi there,\n\nA [concerned user](/id/{vid}) reached out to us about you.\n\nWhen you're in the middle of something painful, it may feel like you don't have a lot of options. But whatever you're going through, you deserve help and there are people who are here for you.\n\nThere are resources available in your area that are free, confidential, and available 24/7:\n\n- Call, Text, or Chat with Canada's [Crisis Services Canada](https://988.ca).\n\n- Call, Email, or Visit the UK's [Samaritans](https://www.samaritans.org).\n\n- Text CHAT to America's [Crisis Text Line](https://www.crisistextline.org) at 741741.\n\nIf you don't see a resource in your area above, here is [a comprehensive list of resources and hotlines organized by location](/h/suicide/post/196839). Find Someone Now.\n\nIf you think you may be depressed or struggling in another way, don't ignore it or brush it aside. Take yourself and your feelings seriously, and reach out to someone.\n\nIt may not feel like it, but you have options. There are people available to listen to you, and ways to move forward.\n\nYour fellow users care about you and there are people who want to help."

elif SITE == 'devrama.net':
	AEVANN_ID = 7
	PERMS["ORGIES"] = 4
	PERMS["SITE_SETTINGS"] = 4
	PERMS["SITE_CACHE_PURGE_CDN"] = 4
else: # localhost or testing environment implied
	HOLE_BANNER_LIMIT = 69420

BOT_IDs = {AUTOJANNY_ID, SNAPPY_ID, LONGPOSTBOT_ID, ZOZBOT_ID}

COLORS = {'ff66ac','ff459a','f04bec','805ad5','62ca56','38a169','80ffff','2a96f3','eb4963','ff0000','f39731','30409f','3e98a7','e4432d','7b9ae4','ec72de','7f8fa6', 'f8db58','8cdbe6', DEFAULT_COLOR}

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

	### dont allow external-content.duckduckgo.com, it gets wiped after 18 months

	### First-Party
	'rdrama.net',
	'i.rdrama.net',
	'watchpeopledie.tv',
	'i.watchpeopledie.tv',
	'videos.watchpeopledie.tv',
	'videos2.watchpeopledie.tv',
	'staging.rdrama.net',
	'marsey.world',

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
	'i.postimg.cc', # WPD chat seems to like it
	'files.catbox.moe',

	### Third-Party Media
	# DO NOT ADD: wordpress.com, wp.com (maybe) | Or frankly anything. No more.
	'i.redd.it',
	'preview.redd.it',
	'external-preview.redd.it',
	'v.redd.it',
	'pbs.twimg.com/media',
	'i.pinimg.com',
	'kiwifarms.net/attachments',
	'uploads.kiwifarms.net/data/attachments',
	'kiwifarms.st/attachments',
	'uploads.kiwifarms.st/data/attachments',
	'uploads.kiwifarms.st/data/video',
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
	'cdn.bsky.app/img/feed_fullsize/plain',
	'dragcave.net/image',
]

for i in (SITE_VIDEOS, SITE_IMAGES, SITE):
	if i not in approved_embed_hosts:
		approved_embed_hosts = [i] + approved_embed_hosts

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
AUDIO_FORMATS = ('mp3','wav','ogg','aac','m4a','flac','oga')

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

homoween_begin_day = 1 if SITE_NAME == 'rDrama' else 26
homoween_begin = datetime.datetime.strptime(f'{homoween_begin_day}/10/{t.year}', '%d/%m/%Y')
homoween_end = datetime.datetime.strptime(f'1/11/{t.year}', '%d/%m/%Y') + datetime.timedelta(hours=16)
def IS_HOMOWEEN():
	return homoween_begin < datetime.datetime.now() < homoween_end

dkd_begin = datetime.datetime.strptime(f'2/4/{t.year}', '%d/%m/%Y')
dkd_end = datetime.datetime.strptime(f'10/4/{t.year}', '%d/%m/%Y')
def IS_DKD():
	return SITE_NAME == 'rDrama' and dkd_begin < datetime.datetime.now() < dkd_end


if SITE_NAME == 'rDrama':
	bday_begin = datetime.datetime.strptime(f'20/5/{t.year}', '%d/%m/%Y')
	bday_end = datetime.datetime.strptime(f'24/5/{t.year}', '%d/%m/%Y')
else:
	bday_begin = datetime.datetime.strptime(f'26/4/{t.year}', '%d/%m/%Y')
	bday_end = datetime.datetime.strptime(f'30/4/{t.year}', '%d/%m/%Y')
def IS_BDAY():
	return bday_begin < datetime.datetime.now() < bday_end

def IS_EVENT():
	if IS_FISTMAS():
		return "fistmas"
	elif IS_HOMOWEEN():
		return "homoween"
	elif IS_DKD():
		return "DKD"
	elif IS_BDAY():
		return "bday"

	return None

def IS_MUSICAL_EVENT():
	return IS_FISTMAS() or IS_HOMOWEEN() or IS_DKD()

fourth_begin = datetime.datetime.strptime(f'4/7/{t.year}', '%d/%m/%Y')
fourth_end = datetime.datetime.strptime(f'5/7/{t.year}', '%d/%m/%Y')
def IS_FOURTH():
	return SITE_NAME == 'rDrama' and fourth_begin < datetime.datetime.now() < fourth_end

fool_begin = datetime.datetime.strptime(f'1/4/{t.year}', '%d/%m/%Y')
fool_end = datetime.datetime.strptime(f'2/4/{t.year}', '%d/%m/%Y')
def IS_FOOL():
	return fool_begin < datetime.datetime.now() < fool_end

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
	"Kamala will win",
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

GIRL_NAMES = { #Lists on purpose
	'A': ['Aadhya', 'Aaliyah', 'Abagail', 'Abbey', 'Abbie', 'Abbigail', 'Abby', 'Abigail', 'Abigale', 'Abigayle', 'Abril', 'Ada', 'Adalee', 'Adaline', 'Adalyn', 'Adalynn', 'Addilyn', 'Addison', 'Adelaide', 'Adele', 'Adelina', 'Adeline', 'Adelyn', 'Adelynn', 'Adhara', 'Adley', 'Adriana', 'Adrianna', 'Adrienne', 'Aila', 'Ailani', 'Ailany', 'Aileen', 'Aimee', 'Ainara', 'Ainhoa', 'Ainsley', 'Aisha', 'Aitana', 'Aiyana', 'Aja', 'Alaia', 'Alaina', 'Alaiya', 'Alana', 'Alani', 'Alanna', 'Alaya', 'Alayah', 'Alayna', 'Aleah', 'Aleena', 'Alejandra', 'Alena', 'Alessandra', 'Alessia', 'Alex', 'Alexa', 'Alexandra', 'Alexandrea', 'Alexandria', 'Alexia', 'Alexis', 'Alexus', 'Alexys', 'Aleyna', 'Ali', 'Alia', 'Aliana', 'Alianna', 'Alice', 'Alicia', 'Alina', 'Alisa', 'Alisha', 'Alison', 'Alissa', 'Alisson', 'Alitzel', 'Alivia', 'Aliya', 'Aliyah', 'Aliza', 'Alize', 'Allie', 'Allison', 'Ally', 'Allyson', 'Allyssa', 'Alma', 'Alondra', 'Alora', 'Alycia', 'Alysa', 'Alysha', 'Alyson', 'Alyssa', 'Amaia', 'Amalia', 'Amanda', 'Amani', 'Amara', 'Amari', 'Amaris', 'Amaya', 'Amayah', 'Amber', 'Amelia', 'Amelie', 'America', 'Amina', 'Amira', 'Amirah', 'Amiri', 'Amiya', 'Amiyah', 'Amora', 'Amoura', 'Amy', 'Amya', 'Amyra', 'Ana', 'Anahi', 'Anais', 'Analia', 'Anastasia', 'Anaya', 'Andi', 'Andie', 'Andrea', 'Angel', 'Angela', 'Angelica', 'Angelina', 'Angelique', 'Angie', 'Anika', 'Anissa', 'Anita', 'Aniya', 'Aniyah', 'Anjali', 'Ann', 'Anna', 'Annabel', 'Annabelle', 'Annalise', 'Annamarie', 'Anne', 'Annette', 'Annie', 'Annika', 'Ansley', 'Antoinette', 'Antonella', 'Antonia', 'Anya', 'April', 'Arabella', 'Araceli', 'Aracely', 'Araya', 'Arely', 'Ari', 'Aria', 'Ariah', 'Ariana', 'Arianna', 'Ariel', 'Ariella', 'Arielle', 'Ariya', 'Ariyah', 'Arlene', 'Arlet', 'Arleth', 'Arlette', 'Armani', 'Artemis', 'Arya', 'Aryanna', 'Asha', 'Ashlee', 'Ashleigh', 'Ashley', 'Ashly', 'Ashlyn', 'Ashlynn', 'Ashton', 'Ashtyn', 'Asia', 'Aspen', 'Aspyn', 'Astrid', 'Athena', 'Aubree', 'Aubrey', 'Audrey', 'Augusta', 'Aura', 'Aurelia', 'Aurora', 'Autumn', 'Ava', 'Avani', 'Avayah', 'Averie', 'Averi', 'Aviana', 'Avianna', 'Aya', 'Ayah', 'Ayana', 'Ayanna', 'Ayla', 'Aylani', 'Ayleen', 'Aylin', 'Ayra', 'Azalea', 'Azari', 'Azaria', 'Azariah'],
	'B': ['Baby', 'Bailee', 'Bailey', 'Barbara', 'Baylee', 'Baylor', 'Beatrice', 'Beatriz', 'Belen', 'Bella', 'Bellamy', 'Berenice', 'Berkley', 'Bethany', 'Bianca', 'Billie', 'Birdie', 'Blaire', 'Blakely', 'Blanca', 'Blessing', 'Bonnie', 'Braelyn', 'Braelynn', 'Brandi', 'Brandy', 'Breana', 'Breanna', 'Breanne', 'Brenda', 'Brenna', 'Breonna', 'Bria', 'Briana', 'Brianna', 'Brianne', 'Briar', 'Bridget', 'Bridgette', 'Briella', 'Brielle', 'Brinley', 'Brionna', 'Brisa', 'Bristol', 'Britney', 'Brittany', 'Brittney', 'Brook', 'Brooke', 'Brooklyn', 'Brooklynn', 'Bryana', 'Bryanna', 'Brynlee', 'Brynleigh', 'Brynn'],
	'C': ['Cadence', 'Caitlin', 'Caitlyn', 'Caitlynn', 'Caleigh', 'Cali', 'Calista', 'Callie', 'Calliope', 'Cameron', 'Camila', 'Camilla', 'Camille', 'Camryn', 'Candace', 'Candice', 'Capri', 'Cara', 'Carina', 'Carissa', 'Carla', 'Carlee', 'Carley', 'Carli', 'Carlie', 'Carly', 'Carmen', 'Carol', 'Carolina', 'Caroline', 'Carolyn', 'Carrie', 'Carter', 'Casandra', 'Casey', 'Cassandra', 'Cassidy', 'Cassie', 'Cataleya', 'Catalina', 'Catherine', 'Cayla', 'Cecelia', 'Cecilia', 'Celeste', 'Celia', 'Celina', 'Celine', 'Chana', 'Chanel', 'Chantel', 'Charity', 'Charlee', 'Charleigh', 'Charli', 'Charlie', 'Charlotte', 'Chasity', 'Chaya', 'Chelsea', 'Chelsey', 'Cheyanne', 'Cheyenne', 'Chloe', 'Christa', 'Christian', 'Christiana', 'Christina', 'Christine', 'Christy', 'Chyna', 'Ciara', 'Cielo', 'Ciera', 'Cierra', 'Cindy', 'Citlalli', 'Claire', 'Clara', 'Clare', 'Clarissa', 'Claudia', 'Clementine', 'Cleo', 'Clover', 'Colette', 'Colleen', 'Collins', 'Cora', 'Coraline', 'Corinne', 'Cortney', 'Courtney', 'Cristal', 'Cristina', 'Crystal', 'Cydney', 'Cynthia'],
	'D': ['Dahlia', 'Daija', 'Daisha', 'Daisy', 'Dakota', 'Daleyza', 'Dalia', 'Dallas', 'Damaris', 'Dana', 'Dani', 'Dania', 'Daniela', 'Daniella', 'Danielle', 'Danna', 'Daphne', 'Darby', 'Darian', 'Dariana', 'Darlene', 'Dasia', 'Davina', 'Dawn', 'Dayana', 'Dayna', 'Deanna', 'Deasia', 'Deborah', 'Deja', 'Dejah', 'Delaney', 'Delia', 'Delilah', 'Della', 'Demi', 'Denise', 'Denver', 'Desirae', 'Desiree', 'Destani', 'Destinee', 'Destiney', 'Destini', 'Destiny', 'Devin', 'Devon', 'Devyn', 'Diamond', 'Diana', 'Diane', 'Dianna', 'Dior', 'Dominique', 'Donna', 'Dorothy', 'Dream', 'Drew', 'Dulce', 'Dylan'],
	'E': ['Ebony', 'Eden', 'Edith', 'Eileen', 'Elaina', 'Elaine', 'Eleanor', 'Eleanora', 'Elena', 'Elia', 'Eliana', 'Elianna', 'Elina', 'Elisa', 'Elisabeth', 'Elise', 'Elissa', 'Eliza', 'Elizabeth', 'Ella', 'Elle', 'Ellen', 'Elliana', 'Ellianna', 'Ellie', 'Elliot', 'Elliott', 'Ellis', 'Elodie', 'Eloise', 'Elora', 'Elouise', 'Elowyn', 'Elsa', 'Elsie', 'Elyse', 'Elyssa', 'Ember', 'Emberly', 'Emberlynn', 'Emelia', 'Emely', 'Emerald', 'Emerie', 'Emerson', 'Emersyn', 'Emery', 'Emilee', 'Emilia', 'Emiliana', 'Emilie', 'Emily', 'Emma', 'Emmalee', 'Emmeline', 'Emmie', 'Emmy', 'Emory', 'Emryn', 'Ensley', 'Erica', 'Ericka', 'Erika', 'Erin', 'Eryn', 'Esme', 'Esmeralda', 'Esperanza', 'Essence', 'Estefania', 'Estella', 'Estelle', 'Esther', 'Estrella', 'Etta', 'Eva', 'Evangeline', 'Eve', 'Evelyn', 'Evelynn', 'Everlee', 'Everleigh', 'Everly', 'Evie', 'Ezra'],
	'F': ['Fabiola', 'Faith', 'Fallon', 'Fatima', 'Faye', 'Felicia', 'Felicity', 'Fernanda', 'Finley', 'Fiona', 'Flora', 'Florence', 'Frances', 'Francesca', 'Freya', 'Freyja'],
	'G': ['Gabriela', 'Gabriella', 'Gabrielle', 'Galilea', 'Gemma', 'Genesis', 'Genevieve', 'Georgia', 'Georgina', 'Gia', 'Giana', 'Gianna', 'Gillian', 'Gina', 'Giovanna', 'Giselle', 'Gisselle', 'Giuliana', 'Gloria', 'Goldie', 'Grace', 'Gracelyn', 'Gracelynn', 'Gracie', 'Graciela', 'Greta', 'Gretchen', 'Guadalupe', 'Gwen', 'Gwendolyn'],
	'H': ['Hadassah', 'Hadlee', 'Hadley', 'Hailee', 'Hailey', 'Hailie', 'Haisley', 'Haleigh', 'Haley', 'Halie', 'Halle', 'Hallie', 'Halo', 'Hana', 'Hanna', 'Hannah', 'Harlee', 'Harley', 'Harlow', 'Harmonia', 'Harmonic', 'Harmony', 'Harper', 'Hattie', 'Haven', 'Hayden', 'Haylee', 'Hayley', 'Haylie', 'Hazel', 'Heather', 'Heaven', 'Heidi', 'Helen', 'Helena', 'Henley', 'Hillary', 'Holland', 'Holly', 'Hope'],
	'I': ['Ila', 'Iliana', 'Imani', 'Inaya', 'India', 'Indie', 'Indigo', 'Indy', 'Ingrid', 'Irene', 'Iris', 'Isabel', 'Isabela', 'Isabella', 'Isabelle', 'Isis', 'Isla', 'Itzel', 'Ivana', 'Ivanna', 'Ivey', 'Ivory', 'Ivy', 'Iyana', 'Iyla', 'Izabella'],
	'J': ['Jacey', 'Jackeline', 'Jacklyn', 'Jaclyn', 'Jacqueline', 'Jacquelyn', 'Jada', 'Jade', 'Jaden', 'Jadyn', 'Jaelyn', 'Jaida', 'Jaiden', 'Jailyn', 'Jaime', 'Jakayla', 'Jaliyah', 'Jalyn', 'Jamie', 'Jana', 'Janae', 'Jane', 'Janelle', 'Janessa', 'Janet', 'Janice', 'Janiya', 'Janiyah', 'Jaquelin', 'Jaqueline', 'Jasmin', 'Jasmine', 'Jasmyn', 'Jaycee', 'Jayda', 'Jayde', 'Jayden', 'Jayla', 'Jaylani', 'Jayleen', 'Jaylin', 'Jazlyn', 'Jazmin', 'Jazmine', 'Jazmyn', 'Jazmyne', 'Jeanette', 'Jemma', 'Jena', 'Jenesis', 'Jenifer', 'Jenna', 'Jennifer', 'Jenny', 'Jesse', 'Jessica', 'Jessie', 'Jewel', 'Jill', 'Jillian', 'Jimena', 'Joana', 'Joanna', 'Joanne', 'Jocelyn', 'Joelle', 'Johanna', 'Jolene', 'Jolie', 'Jordan', 'Jordyn', 'Joselyn', 'Josephine', 'Josie', 'Journee', 'Journey', 'Journi', 'Jovie', 'Joy', 'Joyce', 'Jream', 'Juanita', 'Judith', 'Julia', 'Juliana', 'Julianna', 'Julianne', 'Julie', 'Juliet', 'Julieta', 'Juliette', 'Julissa', 'June', 'Juniper', 'Justice', 'Justine'],
	'K': ['Kacey', 'Kaci', 'Kacie', 'Kaela', 'Kaeli', 'Kaelyn', 'Kahlani', 'Kai', 'Kaia', 'Kaila', 'Kailani', 'Kailee', 'Kailey', 'Kailyn', 'Kairi', 'Kaitlin', 'Kaitlyn', 'Kaitlynn', 'Kaiya', 'Kalani', 'Kaleigh', 'Kaley', 'Kali', 'Kaliyah', 'Kallie', 'Kalyn', 'Kamari', 'Kameron', 'Kamila', 'Kamiyah', 'Kamryn', 'Kara', 'Karen', 'Kari', 'Karina', 'Karissa', 'Karla', 'Karlee', 'Karley', 'Karli', 'Karlie', 'Karly', 'Karsyn', 'Karter', 'Kasandra', 'Kasey', 'Kassandra', 'Kassidy', 'Kataleya', 'Katalina', 'Katarina', 'Kate', 'Katelin', 'Katelyn', 'Katelynn', 'Katerina', 'Katharine', 'Katherine', 'Kathleen', 'Kathryn', 'Kathy', 'Katia', 'Katie', 'Katlyn', 'Katlynn', 'Katrina', 'Katy', 'Kaya', 'Kayla', 'Kaylah', 'Kaylan', 'Kaylani', 'Kaylee', 'Kayleigh', 'Kayley', 'Kayli', 'Kaylie', 'Kaylin', 'Kaylyn', 'Kaylynn', 'Keara', 'Keeley', 'Keely', 'Kehlani', 'Keilani', 'Keily', 'Keira', 'Kelli', 'Kellie', 'Kelly', 'Kelsey', 'Kelsi', 'Kelsie', 'Kendall', 'Kendra', 'Kenia', 'Kenna', 'Kennedi', 'Kennedy', 'Kensley', 'Kenya', 'Kenzie', 'Keyla', 'Khalani', 'Khaleesi', 'Khloe', 'Kiana', 'Kianna', 'Kiara', 'Kiarra', 'Kiera', 'Kierra', 'Kiersten', 'Kiley', 'Kimber', 'Kimberly', 'Kimora', 'Kinley', 'Kinsey', 'Kinslee', 'Kinsley', 'Kira', 'Kirsten', 'Kirstin', 'Kora', 'Kori', 'Kourtney', 'Krista', 'Kristen', 'Kristin', 'Kristina', 'Kristine', 'Kristy', 'Krystal', 'Kya', 'Kyla', 'Kylee', 'Kyleigh', 'Kylie', 'Kyra'],
	'L': ['Lacey', 'Laila', 'Lainey', 'Laisha', 'Lakelyn', 'Lakelynn', 'Lana', 'Laney', 'Lara', 'Larissa', 'Laura', 'Laurel', 'Lauren', 'Lauryn', 'Layla', 'Laylah', 'Laylani', 'Layne', 'Lea', 'Leah', 'Leann', 'Leanna', 'Legacy', 'Leia', 'Leighton', 'Leila', 'Leilani', 'Leilany', 'Lena', 'Lenora', 'Leona', 'Lesley', 'Leslie', 'Lesly', 'Leticia', 'Lexi', 'Lexie', 'Lexus', 'Leyla', 'Lia', 'Liana', 'Liberty', 'Lila', 'Lilah', 'Lilia', 'Lilian', 'Liliana', 'Lilianna', 'Lilith', 'Lillian', 'Lilliana', 'Lillie', 'Lilly', 'Lily', 'Lilyana', 'Lina', 'Linda', 'Lindsay', 'Lindsey', 'Lisa', 'Lisette', 'Litzy', 'Liv', 'Livia', 'Lizbeth', 'Lizeth', 'Lizette', 'Lola', 'London', 'Londyn', 'Lorelai', 'Lorelei', 'Loren', 'Lorena', 'Loretta', 'Lori', 'Lottie', 'Louisa', 'Louise', 'Lourdes', 'Love', 'Lucia', 'Luciana', 'Lucille', 'Lucy', 'Luella', 'Luisa', 'Luna', 'Luz', 'Lydia', 'Lyla', 'Lylah', 'Lyndsey', 'Lyra', 'Lyric'],
	'M': ['Mabel', 'Macey', 'Maci', 'Macie', 'Mackenzie', 'Macy', 'Madalyn', 'Maddie', 'Maddison', 'Madeleine', 'Madeline', 'Madelyn', 'Madelynn', 'Madilyn', 'Madilynn', 'Madisen', 'Madison', 'Madisyn', 'Madyson', 'Mae', 'Maegan', 'Maeve', 'Magdalena', 'Maggie', 'Magnolia', 'Maia', 'Maisie', 'Maisy', 'Maiya', 'Makayla', 'Makenna', 'Makenzie', 'Malani', 'Malaya', 'Malayah', 'Malaysia', 'Malia', 'Maliyah', 'Mallory', 'Mandy', 'Mara', 'Maranda', 'Marceline', 'Maren', 'Margaret', 'Margarita', 'Margo', 'Margot', 'Maria', 'Mariah', 'Mariam', 'Marian', 'Mariana', 'Marianna', 'Maribel', 'Marie', 'Mariela', 'Marigold', 'Marilee', 'Marilyn', 'Marina', 'Marisa', 'Marisol', 'Marissa', 'Maritza', 'Marleen', 'Marleigh', 'Marlen', 'Marlene', 'Marley', 'Martha', 'Martina', 'Mary', 'Maryam', 'Matilda', 'Mattie', 'Maura', 'Mavis', 'Maxine', 'Maya', 'Mayra', 'Mazie', 'Mckayla', 'Mckenna', 'McKenzie', 'Mckinley', 'Meadow', 'Meagan', 'Meaghan', 'Megan', 'Meghan', 'Meilani', 'Melanie', 'Melany', 'Melina', 'Melinda', 'Melisa', 'Melissa', 'Melody', 'Mercedes', 'Mercy', 'Meredith', 'Mia', 'Micaela', 'Micah', 'Michaela', 'Michele', 'Michelle', 'Mikaela', 'Mikayla', 'Mila', 'Milan', 'Milana', 'Milani', 'Milena', 'Miley', 'Millie', 'Mina', 'Mira', 'Miracle', 'Miranda', 'Mireya', 'Miriam', 'Misty', 'Mollie', 'Molly', 'Monica', 'Monique', 'Monserrat', 'Montana', 'Morgan', 'Moriah', 'Murphy', 'Mya', 'Myah', 'Myla', 'Mylah', 'Myra'],
	'N': ['Nadia', 'Nadine', 'Nala', 'Nalani', 'Nancy', 'Naomi', 'Natalia', 'Natalie', 'Nataly', 'Natasha', 'Nathalie', 'Navy', 'Naya', 'Nayeli', 'Neera', 'Neha', 'Nellie', 'Neriah', 'Nevaeh', 'Nia', 'Niah', 'Nichole', 'Nicole', 'Nicolette', 'Nikita', 'Nikki', 'Nina', 'Nira', 'Noa', 'Noah', 'Noelia', 'Noelle', 'Noemi', 'Nola', 'Noor', 'Nora', 'Norah', 'Nori', 'Norma', 'Novah', 'Novalee', 'Nya', 'Nyah', 'Nyasia', 'Nyla', 'Nylah', 'Nyomi', 'Nyra'],
	'O': ['Oaklee', 'Oakleigh', 'Oakley', 'Oaklyn', 'Oaklynn', 'Ocean', 'Octavia', 'Odalys', 'Olive', 'Olivia', 'Opal', 'Ophelia'],
	'P': ['Paige', 'Paislee', 'Paisley', 'Paloma', 'Pamela', 'Paola', 'Paris', 'Parker', 'Patience', 'Patricia', 'Paula', 'Paulina', 'Pearl', 'Penelope', 'Penny', 'Perla', 'Persephone', 'Phoebe', 'Phoenix', 'Piper', 'Poppy', 'Precious', 'Presley', 'Princess', 'Priscilla', 'Promise'],
	'Q': ['Qi', 'Qiana', 'Quelina', 'Quiana', 'Quinby', 'Quincy', 'Quinley', 'Quinlyn', 'Quinn', 'Quirina'],
	'R': ['Rachael', 'Rachel', 'Rachelle', 'Raegan', 'Raelyn', 'Raelynn', 'Raina', 'Ramona', 'Randi', 'Raquel', 'Raven', 'Raya', 'Rayna', 'Rayne', 'Reanna', 'Rebeca', 'Rebecca', 'Rebekah', 'Reese', 'Regan', 'Regina', 'Reign', 'Reilly', 'Reina', 'Remi', 'Renata', 'Renee', 'Reya', 'Reyna', 'Rhea', 'Rhianna', 'Rhiannon', 'Riley', 'Rita', 'River', 'Rivka', 'Robin', 'Robyn', 'Rocio', 'Romina', 'Rory', 'Rosa', 'Rosalia', 'Rosalie', 'Rosalina', 'Rosalinda', 'Rose', 'Roselyn', 'Rosemary', 'Rosie', 'Rowan', 'Roxanne', 'Royalty', 'Ruby', 'Ruth', 'Ruthie', 'Ryan', 'Ryann', 'Rylee', 'Ryleigh', 'Rylie'],
	'S': ['Saanvi', 'Sabrina', 'Sadie', 'Sage', 'Saige', 'Salem', 'Sally', 'Salma', 'Samantha', 'Samara', 'Samira', 'Sandra', 'Sandy', 'Saoirse', 'Sapphire', 'Sara', 'Sarah', 'Sarahi', 'Sarai', 'Sariah', 'Sarina', 'Sariyah', 'Sasha', 'Savana', 'Savanah', 'Savanna', 'Savannah', 'Saylor', 'Scarlet', 'Scarlett', 'Selah', 'Selena', 'Selene', 'Selina', 'Seraphina', 'Serena', 'Serenity', 'Sevyn', 'Shaina', 'Shakira', 'Shania', 'Shaniya', 'Shannon', 'Sharon', 'Shawna', 'Shay', 'Shayla', 'Shaylee', 'Shayna', 'Shea', 'Sheila', 'Shelby', 'Shiloh', 'Shirley', 'Shyann', 'Shyanne', 'Sidney', 'Siena', 'Sienna', 'Sierra', 'Silvia', 'Simone', 'Sky', 'Skye', 'Skyla', 'Skylar', 'Skyler', 'Sloan', 'Sloane', 'Sofia', 'Sol', 'Solana', 'Soleil', 'Sonia', 'Sonya', 'Sophia', 'Sophie', 'Stacey', 'Stacy', 'Stefanie', 'Stella', 'Stephanie', 'Stephany', 'Stevie', 'Stormi', 'Summer', 'Sunny', 'Susan', 'Susana', 'Sutton', 'Sydnee', 'Sydney', 'Sydni', 'Sydnie', 'Sylvia', 'Sylvie'],
	'T': ['Tabitha', 'Talia', 'Tallulah', 'Tamara', 'Tamia', 'Tania', 'Tanya', 'Tara', 'Taryn', 'Tatiana', 'Tatianna', 'Tatum', 'Tatyana', 'Taya', 'Tayler', 'Taylor', 'Taytum', 'Teagan', 'Teresa', 'Tess', 'Tessa', 'Thalia', 'Thea', 'Theodora', 'Theresa', 'Tia', 'Tiana', 'Tianna', 'Tiara', 'Tierra', 'Tiffany', 'Tina', 'Toni', 'Tori', 'Traci', 'Tracie', 'Tracy', 'Treasure', 'Trinity', 'Trisha', 'Tru', 'Tyler', 'Tyra'],
	'U': ['Udaya', 'Udita', 'Ula', 'Ulani', 'Ulyana', 'Uma', 'Umi', 'Unity', 'Unique', 'Uriyah', 'Uriyana', 'Ursula', 'Usha', 'Ushangi'],
	'V': ['Vada', 'Valentina', 'Valeria', 'Valerie', 'Valery', 'Vanessa', 'Veda', 'Vera', 'Veronica', 'Victoria', 'Vienna', 'Violet', 'Violeta', 'Violette', 'Virginia', 'Vivian', 'Viviana', 'Vivienne'],
	'W': ['Waverly', 'Wendy', 'Whitley', 'Whitney', 'Willa', 'Willow', 'Winifred', 'Winnie', 'Winona', 'Winter', 'Wren', 'Wrenlee', 'Wrenley', 'Wynter'],
	'X': ['Xamira', 'Xandra', 'Xanthe', 'Xanthia', 'Xanthippe', 'Xavia', 'Xaviera', 'Xeenia', 'Xena', 'Xia', 'Xiomara', 'Ximena', 'Xyla'],
	'Y': ['Yadira', 'Yamilet', 'Yamileth', 'Yara', 'Yareli', 'Yaretzi', 'Yasmeen', 'Yasmin', 'Yasmine', 'Yazmin', 'Yesenia', 'Yessenia', 'Yolanda', 'Yvette', 'Yvonne'],
	'Z': ['Zahra', 'Zahraa', 'Zainab', 'Zaniyah', 'Zara', 'Zaria', 'Zariah', 'Zariyah', 'Zayla', 'Zaylee', 'Zelda', 'Zendaya', 'Zhuri', 'Zoe', 'Zoey', 'Zoie', 'Zora', 'Zoya', 'Zuri']
}

GIRL_NAMES_TOTAL = set()
for l in GIRL_NAMES.values():
	GIRL_NAMES_TOTAL.update(l)

from sqlalchemy.engine.create import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(environ.get("DATABASE_URL").strip(), connect_args={"options": "-c statement_timeout=40000 -c idle_in_transaction_session_timeout=40000"})
db_session = scoped_session(sessionmaker(bind=engine, autoflush=False))

approved_embed_hosts_for_csp = ' '.join({x.split('/')[0] for x in approved_embed_hosts})
csp = f"default-src 'none'; frame-ancestors 'none'; form-action 'self'; manifest-src 'self'; worker-src 'self'; base-uri 'self'; font-src 'self' files.catbox.moe fonts.gstatic.com; style-src-elem 'self' rdrama.net watchpeopledie.tv; style-src-attr 'unsafe-inline'; style-src 'self' 'unsafe-inline'; script-src-elem 'self' challenges.cloudflare.com static.cloudflareinsights.com; script-src-attr 'none'; script-src 'self' challenges.cloudflare.com static.cloudflareinsights.com; frame-src www.teamblind.com www.tiktok.com www.instagram.com embed.reddit.com substack.com *.substack.com challenges.cloudflare.com cdpn.io platform.twitter.com rumble.com player.twitch.tv; connect-src 'self' submit.watchpeopledie.tv; img-src {approved_embed_hosts_for_csp} data:; media-src *.googlevideo.com archive.org *.archive.org litter.catbox.moe {approved_embed_hosts_for_csp};"
if not IS_LOCALHOST:
	csp += ' upgrade-insecure-requests;'

with open("includes/content-security-policy", "w") as f:
	f.write(f'add_header Content-Security-Policy "{csp}";')

def commas(number):
	return "{:,}".format(number)

AMERICAS_CODES = {'AI','AG','AR','AW','BS','BB','BZ','BM','BO','BQ','BV','BR','CA','KY','CL','CO','CR','CU','CW','DM','DO','EC','SV','FK','GF','GL','GD','GP','GT','GY','HT','HN','JM','MQ','MX','MS','NI','PA','PY','PE','PR','BL','KN','LC','MF','PM','VC','SX','GS','SR','TT','TC','US','UY','VE','VG','VI'}

import sys
if "load_chat" in sys.argv:
	sys.tracebacklimit = 0
	from flask_socketio import emit
	def stop(code, message=None):
		emit('error', message)
		raise Exception(message)
else:
	from flask import abort
	def stop(code, message=None):
		abort(code, message)
