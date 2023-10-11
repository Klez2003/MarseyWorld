from copy import deepcopy

from files.helpers.config.const import *

FISTMAS_AWARDS = ("fireplace", "snow", "gingerbread", "lights", "frostbite", "candycane")
HOMOWEEN_AWARDS = ("spiders", "fog", "bones", "pumpkin", "candy-corn", "ectoplasm", "stab", "flashlight", "haunt", "jumpscare", "bite", "vax")

#Personal awards are disabled on ghost posts and comments bc they can be used to figure out the identity of the author through https://rdrama.net/badges
AWARDS = {
	"fallback": {
		"kind": "fallback",
		"title": "Unknown",
		"description": "???",
		"icon": "fas fa-block-question",
		"color": "text-white",
		"price": 0,
		"deflectable": False,
		"cosmetic": False,
		"ghost": False,
		"enabled": False,
		"positive": True,
	},

	### Deprecated
	"king": {
		"kind": "king",
		"title": "King",
		"description": "Gives the recipient golden text for 24 hours.",
		"icon": "fas fa-crown",
		"color": "text-gold",
		"price": 1000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": False,
		"positive": True,
   },
	"ghost": {
		"kind": "ghost",
		"title": "Ghost",
		"description": "???",
		"icon": "fas fa-ghost",
		"color": "text-white",
		"price": 3000,
		"deflectable": False,
		"cosmetic": False,
		"ghost": False,
		"enabled": False,
		"positive": True,
	},
	"nword": {
		"kind": "nword",
		"title": "Nword Pass",
		"description": "???",
		"icon": "fas fa-edit",
		"color": "text-success",
		"price": 10000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": False,
		"positive": True,
	},
	"fish": {
		"kind": "fish",
		"title": "Fish",
		"description": "???",
		"icon": "fas fa-fish",
		"color": "text-gold",
		"price": 20000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": False,
		"positive": True,
	},


	### Fistmas and Homoween
	"lootbox": {
		"kind": "lootbox",
		"title": "Lootbox",
		"description": "???",
		"icon": "fas fa-box-open",
		"color": "text-blue",
		"price": 1000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": IS_FISTMAS() or IS_HOMOWEEN(),
		"positive": True,
	},

	### Fistmas
	"fireplace": {
		"kind": "fireplace",
		"title": "Fireplace",
		"description": "???",
		"icon": "fas fa-fireplace",
		"color": "text-orange",
		"price": 100,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": IS_FISTMAS(),
		"positive": True,
	},
	"snow": {
		"kind": "snow",
		"title": "Snow",
		"description": "???",
		"icon": "fas fa-snowflake",
		"color": "text-lightblue",
		"price": 300,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": IS_FISTMAS(),
		"positive": True,
	},
	"gingerbread": {
		"kind": "gingerbread",
		"title": "Gingerbread",
		"description": "???",
		"icon": "fas fa-gingerbread-man",
		"color": "text-brown",
		"price": 300,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": IS_FISTMAS(),
		"positive": True,
	},
	"lights": {
		"kind": "lights",
		"title": "Lights",
		"description": "???",
		"icon": "fas fa-lights-holiday",
		"color": "text-success",
		"price": 300,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": IS_FISTMAS(),
		"positive": True,
	},
	"frostbite": {
		"kind": "frostbite",
		"title": "Frostbite",
		"description": "???",
		"icon": "fas fa-temperature-snow",
		"color": "text-blue",
		"price": 300,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": IS_FISTMAS(),
		"positive": True,
	},
	"candycane": {
		"kind": "candycane",
		"title": "Candy Cane",
		"description": "???",
		"icon": "fas fa-candy-cane",
		"color": "text-danger",
		"price": 300,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": IS_FISTMAS(),
		"positive": True,
	},
	"grinch": {
		"kind": "grinch",
		"title": "Grinch",
		"description": "???",
		"icon": "fas fa-angry",
		"color": "text-green-500",
		"price": 1000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": IS_FISTMAS() and SITE_NAME != "WPD",
		"positive": True,
	},

	### Homoween
	"spiders": {
		"kind": "spiders",
		"title": "Spiders",
		"description": "???",
		"icon": "fas fa-spider",
		"color": "text-black",
		"price": 200,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": IS_HOMOWEEN(),
		"positive": True,
	},
	"fog": {
		"kind": "fog",
		"title": "Fog",
		"description": "???",
		"icon": "fas fa-smoke",
		"color": "text-gray",
		"price": 200,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": IS_HOMOWEEN(),
		"positive": True,
	},
	"bones": {
		"kind": "bones",
		"title": "Bones",
		"description": "???",
		"icon": "fas fa-bone",
		"color": "text-white",
		"price": 200,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": IS_HOMOWEEN(),
		"positive": True,
	},
	"pumpkin": {
		"kind": "pumpkin",
		"title": "Pumpkin",
		"description": "???",
		"icon": "fas fa-jack-o-lantern",
		"color": "text-orange",
		"price": 200,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": IS_HOMOWEEN(),
		"positive": True,
	},
	"stalker": {
		"kind": "stalker",
		"title": "Stalker",
		"description": "???",
		"icon": "fas fa-scarecrow",
		"color": "text-primary",
		"price": 250,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": IS_HOMOWEEN(),
		"positive": True,
	},
	"candy-corn": {
		"kind": "candy-corn",
		"title": "Candy Corn",
		"description": "???",
		"icon": "fas fa-candy-corn",
		"color": "text-orange",
		"price": 400,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": IS_HOMOWEEN(),
		"positive": True,
	},
	"ectoplasm": {
		"kind": "ectoplasm",
		"title": "Ectoplasm",
		"description": "???",
		"icon": "fas fa-ghost",
		"color": "text-success",
		"price": 400,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": IS_HOMOWEEN(),
		"positive": True,
	},
	"stab": {
		"kind": "stab",
		"title": "Stab",
		"description": "???",
		"icon": "fas fa-knife-kitchen",
		"color": "text-danger",
		"price": 400,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": IS_HOMOWEEN(),
		"positive": True,
	},
	"upsidedown": {
		"kind": "upsidedown",
		"title": "Upside Down",
		"description": "???",
		"icon": "fas fa-trees",
		"color": "",
		"price": 400,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": IS_HOMOWEEN() and SITE == 'devrama.net',
		"positive": True,
	},
	"flashlight": {
		"kind": "flashlight",
		"title": "Flashlight",
		"description": "???",
		"icon": "fas fa-flashlight",
		"color": "text-black",
		"price": 400,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": IS_HOMOWEEN(),
		"positive": True,
	},
	"haunt": {
		"kind": "haunt",
		"title": "Haunt",
		"description": "???",
		"icon": "fas fa-book-dead",
		"color": "text-warning",
		"price": 400,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": IS_HOMOWEEN(),
		"positive": True,
	},

	"jumpscare": {
		"kind": "jumpscare",
		"title": "Jumpscare",
		"description": "???",
		"icon": "fas fa-coffin-cross",
		"color": "text-purple",
		"price": 500,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": IS_HOMOWEEN(),
		"positive": True,
	},
	"vax": {
		"kind": "vax",
		"title": "Vaxxmaxx",
		"description": "???",
		"icon": "fas fa-syringe",
		"color": "text-blue",
		"price": 200,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": IS_HOMOWEEN(),
		"positive": True,
	},
	"bite": {
		"kind": "bite",
		"title": "Zombie Bite",
		"description": "???",
		"icon": "fas fa-biohazard",
		"color": "text-danger",
		"price": 500,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": IS_HOMOWEEN(),
		"positive": True,
	},
	"hallowgrinch": {
		"kind": "hallowgrinch",
		"title": "Hallowgrinch",
		"description": "???",
		"icon": "fas fa-angry",
		"color": "text-orange",
		"price": 1000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": IS_HOMOWEEN() and SITE_NAME != "WPD",
		"positive": True,
	},

	### Birthgay/Birthdead
	"confetti": {
		"kind": "confetti",
		"title": "Confetti",
		"description": "Summons confetti to fall on the post.",
		"icon": "fas fa-party-horn",
		"color": "text-yellow",
		"price": 200,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": IS_BIRTHGAY() or IS_BIRTHDEAD(),
		"positive": True,
	},

	### Standard
	"beano": {
		"kind": "beano",
		"title": "Beano",
		"description": "Makes the recipient not hear fart noises on the site.",
		"icon": "fas fa-gas-pump-slash",
		"color": "text-green",
		"price": 100,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": True,
	},
	"marsify": {
		"kind": "marsify",
		"title": "Marsify",
		"description": "Marsifies the recipient's posts and comments for 24 hours.",
		"icon": "fas fa-cat",
		"color": "text-white",
		"price": 100,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": False,
	},
	"emoji": {
		"kind": "emoji",
		"title": "Emoji",
		"description": "Summons a moving emoji on the post.",
		"icon": "fas fa-smile-beam",
		"color": "text-yellow",
		"price": 100,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": True,
		"positive": True,
	},
	"emoji-hz": {
		"kind": "emoji-hz",
		"title": "Emoji",
		"description": "Summons a moving emoji on the post.",
		"icon": "fas fa-smile-beam",
		"color": "text-yellow",
		"price": 200,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": False,
		"positive": True,
	},
	"rainbow": {
		"kind": "rainbow",
		"title": "Rainbow",
		"description": "Makes the recipient's posts and comments in rainbow text for 24 hours.",
		"icon": "fas fa-cloud-rainbow",
		"color": "text-pink",
		"price": 200,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": not FEATURES['HOUSES'],
		"positive": False,
	},
	"sharpen": {
		"kind": "sharpen",
		"title": "Sharpen",
		"description": "Adds a badass edge to all the recipient's posts and comments for 24 hours.",
		"icon": "fas fa-fire",
		"color": "text-danger",
		"price": 200,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": not FEATURES['HOUSES'],
		"positive": False,
	},
	"shit": {
		"kind": "shit",
		"title": "Shit",
		"description": "Makes flies swarm the post.",
		"icon": "fas fa-poop",
		"color": "text-black-50",
		"price": 300,
		"deflectable": True,
		"cosmetic": True,
		"ghost": True,
		"enabled": True,
		"positive": True,
	},
	"fireflies": {
		"kind": "fireflies",
		"title": "Fireflies",
		"description": "Makes fireflies swarm the post.",
		"icon": "fas fa-sparkles",
		"color": "text-warning",
		"price": 300,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": True,
		"positive": True,
	},
	"firework": {
		"kind": "firework",
		"title": "Fireworks",
		"description": "Summons fireworks on the post.",
		"icon": "fas fa-bahai",
		"color": "text-danger",
		"price": 300,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": True,
		"positive": True,
	},
	"ricardo": {
		"kind": "ricardo",
		"title": "Stripper Cake",
		"description": "Summons Ricardo to dance on the post.",
		"icon": "fas fa-pinata",
		"color": "text-pink",
		"price": 300,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": True,
		"positive": True,
	},
	"tilt": {
		"kind": "tilt",
		"title": "Tilt",
		"description": "Tilts the post or comment",
		"icon": "fas fa-car-tilt",
		"color": "text-blue",
		"price": 300,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": True,
		"positive": False,
	},
	"glowie": {
		"kind": "glowie",
		"title": "Glowie",
		"description": "Indicates that the recipient can be seen when driving. Just run them over.",
		"icon": "fas fa-user-secret",
		"color": "text-green",
		"price": 500,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": True,
		"positive": False,
	},
	"gold": {
		"kind": "gold",
		"title": "Gold",
		"description": "Gold is a virtual good you can use on Reddit to reward, recognize, and celebrate content from redditors you love. If you like a post or comment and want to show your appreciation for it, you can give it gold. This will help the post or comment stand out on Reddit.",
		"icon": "fas fa-coin",
		"color": "text-gold",
		"price": 500,
		"deflectable": False,
		"cosmetic": True,
		"ghost": True,
		"enabled": True,
		"positive": True,
   },
	"spider": {
		"kind": "spider",
		"title": "Spider!",
		"description": "Summons a spider to terrorize the recipient for 24 hours.",
		"icon": "fas fa-spider",
		"color": "text-brown",
		"price": 500,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": False,
	},
	"owoify": {
		"kind": "owoify",
		"title": "OwOify",
		"description": "OwOifies the recipient's posts and comments for 6 hours.",
		"icon": "fas fa-paw-simple",
		"color": "text-purple",
		"price": 500,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": not FEATURES['HOUSES'],
		"positive": False,
	},
	"flairlock": {
		"kind": "flairlock",
		"title": "1-Day Flairlock",
		"description": "Sets a flair for the recipient and locks it for 24 hours.",
		"icon": "fas fa-lock",
		"color": "text-black",
		"price": 500,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": False,
	},
	"rehab": {
		"kind": "rehab",
		"title": "Rehab",
		"description": "Prevents the user from gambling for 24 hours in a last-ditch effort to save them from themself.",
		"icon": "fas fa-dice-six",
		"color": "text-black",
		"price": 777,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": False,
	},
	"namelock": {
		"kind": "namelock",
		"title": "1-Day Namelock",
		"description": "Changes the recipient's username to something of your choosing for 24 hours.",
		"icon": "fas fa-at",
		"color": "text-pink",
		"price": 1000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": False,
	},
	"queen": {
		"kind": "queen",
		"title": "Queen",
		"description": "Gets the recipient in touch with their feminine side for 24 hours.",
		"icon": "fas fa-phone",
		"color": "text-pink",
		"price": 1000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": False,
	},
	"offsitementions": {
		"kind": "offsitementions",
		"title": "Y'all Seein' Eye",
		"description": "Gives the recipient access to notifications when people off-site talk about us.",
		"icon": "fas fa-eyes",
		"color": "text-orange",
		"price": 1000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": True,
	},
	"unpin": {
		"kind": "unpin",
		"title": "Unpin",
		"description": "Removes 1 hour from the pin duration of a post or 6 hours from the pin duration of a comment.",
		"icon": "fas fa-thumbtack fa-rotate--45",
		"color": "text-black",
		"price": 1000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": True,
		"enabled": True,
		"positive": False,
	},
	"chud": {
		"kind": "chud",
		"title": "Chud",
		"description": "Chuds the recipient for 24 hours.",
		"icon": "fas fa-snooze",
		"color": "text-purple",
		"price": 1000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": False,
	},
	"pin": {
		"kind": "pin",
		"title": "Pin",
		"description": "Pins a post for 1 hour or a comment for 6 hours.",
		"icon": "fas fa-thumbtack fa-rotate--45",
		"color": "text-warning",
		"price": 1500,
		"deflectable": False,
		"cosmetic": False,
		"ghost": True,
		"enabled": True,
		"positive": True,
	},
	"progressivestack": {
		"kind": "progressivestack",
		"title": "Progressive Stack",
		"description": "Makes votes on the recipient's posts and comments weigh double in the ranking algorithm for 6 hours.",
		"icon": "fas fa-bullhorn",
		"color": "text-danger",
		"price": 1500,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": True,
	},
	"pizzashill": {
		"kind": "pizzashill",
		"title": "Pizzashill",
		"description": "Forces the recipient to make all posts/comments > 280 characters for 24 hours.",
		"icon": "fas fa-pizza-slice",
		"color": "text-orange",
		"price": 1500,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": False,
	},
	"bird": {
		"kind": "bird",
		"title": "Bird Site",
		"description": "Forces the recipient to make all posts/comments < 140 characters for 24 hours.",
		"icon": "fab fa-twitter",
		"color": "text-blue",
		"price": 1500,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": False,
	},
	"marsey": {
		"kind": "marsey",
		"title": "Hieroglyphs",
		"description": "Makes the recipient unable to post/comment anything but emojis for 24 hours.",
		"icon": "fas fa-ankh",
		"color": "text-gold",
		"price": 2000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": False,
	},
	"ban": {
		"kind": "ban",
		"title": "1-Day Ban",
		"description": "Bans the recipient for a day.",
		"icon": "fas fa-gavel",
		"color": "text-danger",
		"price": 2000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": False,
	},
	"unban": {
		"kind": "unban",
		"title": "1-Day Unban",
		"description": "Removes 1 day from the ban duration of the recipient.",
		"icon": "fas fa-gavel",
		"color": "text-success",
		"price": 2500,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": True,
	},
	"deflector": {
		"kind": "deflector",
		"title": "Deflector",
		"description": "Causes most awards received for the next 10 hours to be deflected back at their giver.",
		"icon": "fas fa-shield",
		"color": "text-pink",
		"price": 2500,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": True,
	},
	"benefactor": {
		"kind": "benefactor",
		"title": "Benefactor",
		"description": f"Grants one month of {patron} status and 2000 marseybux to the recipient. Cannot be used on yourself.",
		"icon": "fas fa-gift",
		"color": "text-blue",
		"price": 4000,
		"deflectable": False,
		"cosmetic": False,
		"ghost": False,
		"enabled": FEATURES['MARSEYBUX'],
		"positive": True,
	},
	"eye": {
		"kind": "eye",
		"title": "All-Seeing Eye",
		"description": "Gives the recipient the ability to view private profiles.",
		"icon": "fas fa-eye",
		"color": "text-silver",
		"price": 5000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": True,
	},
	"grass": {
		"kind": "grass",
		"title": "Grass",
		"description": "Ban the recipient for 30 days (if they provide a timestamped picture of them touching grass/snow/sand/ass to the admins, they will get unbanned immediately)",
		"icon": "fas fa-seedling",
		"color": "text-success",
		"price": 10000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": False,
	},
	"unblockable": {
		"kind": "unblockable",
		"title": "Unblockable",
		"description": "Makes the recipient unblockable and removes all blocks on them.",
		"icon": "fas fa-laugh-squint",
		"color": "text-lightgreen",
		"price": 20000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": True,
	},
	"pause": {
		"kind": "pause",
		"title": "Pause",
		"description": "Gives the recipient the ability to pause profile anthems.",
		"icon": "fas fa-volume-mute",
		"color": "text-danger",
		"price": 20000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": True,
	},
	"unpausable": {
		"kind": "unpausable",
		"title": "Unpausable",
		"description": "Makes the profile anthem of the recipient unpausable.",
		"icon": "fas fa-volume",
		"color": "text-success",
		"price": 40000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": True,
	},
	"alt": {
		"kind": "alt",
		"title": "Alt-Seeing Eye",
		"description": "Gives the recipient the ability to view alts.",
		"icon": "fas fa-eye",
		"color": "text-gold",
		"price": 50000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": True,
	},
	"checkmark": {
		"kind": "checkmark",
		"title": "Checkmark",
		"description": "Gives the recipient a checkmark.",
		"icon": "fas fa-badge-check",
		"color": "checkmark",
		"price": 50000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": True,
	},
	"pride": {
		"kind": "pride",
		"title": "Pride",
		"description": "Permanently glams up the recipient's name, showing lifelong support for the LGBTQIA+ community.",
		"icon": "fas fa-heart",
		"color": "text-purple",
		"price": 200000,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"enabled": True,
		"positive": True,
	},
}

AWARDS_ENABLED = {}
for k, val in AWARDS.items():
	if val["enabled"]:
		AWARDS_ENABLED[k] = val

LOOTBOX_ITEM_COUNT = 5

HOUSE_AWARDS = {
	"Furry": {
		"kind": "Furry",
		"title": "OwOify",
		"description": "OwOifies the recipient's posts and comments for 6 hours.",
		"icon": "fas fa-paw-simple",
		"color": "text-purple",
		"price": 500,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"positive": False,
	},
	"Femboy": {
		"kind": "Femboy",
		"title": "Rainbow",
		"description": "Makes the recipient's posts and comments in rainbow text for 24 hours.",
		"icon": "fas fa-cloud-rainbow",
		"color": "text-pink",
		"price": 200,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"positive": False,
	},
	"Vampire": {
		"kind": "Vampire",
		"title": "Bite",
		"description": "Turns the recipient into a vampire for 2 days.",
		"icon": "fas fa-bat",
		"color": "text-gray",
		"price": 500,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"positive": False,
	},
	"Racist": {
		"kind": "Racist",
		"title": "Early Life",
		"description": "Checks the recipient's Early Life section on Wikipedia. Notices.",
		"icon": "fas fa-star-of-david",
		"color": "text-yellow",
		"price": 100,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"positive": False,
	},
	"Edgy": {
		"kind": "Edgy",
		"title": "Sharpen",
		"description": "Adds a badass edge to all the recipient's posts and comments for 24 hours.",
		"icon": "fas fa-fire",
		"color": "text-danger",
		"price": 200,
		"deflectable": True,
		"cosmetic": False,
		"ghost": False,
		"positive": False,
	},
}

temp = deepcopy(HOUSE_AWARDS).items()
for k, val in temp:
	HOUSE_AWARDS[f'{k} Founder'] = val
	HOUSE_AWARDS[f'{k} Founder']['kind'] += ' Founder'
	HOUSE_AWARDS[f'{k} Founder']['price'] = int(HOUSE_AWARDS[f'{k} Founder']['price'] * 0.75)
