import re
from .config.const import *

tranny = f'<img loading="lazy" data-bs-toggle="tooltip" alt=":marseytrain:" title=":marseytrain:" src="{SITE_FULL_IMAGES}/e/marseytrain.webp">'
trannie = f'<img loading="lazy" data-bs-toggle="tooltip" alt=":!marseytrain:" title=":!marseytrain:" src="{SITE_FULL_IMAGES}/e/marseytrain.webp">'
troon = f'<img loading="lazy" data-bs-toggle="tooltip" alt=":marseytrain2:" title=":marseytrain2:" src="{SITE_FULL_IMAGES}/e/marseytrain2.webp">'

SLURS = {
	"tranny": tranny,
	"trannie": trannie,
	"troon": troon,
	"(?<!\\bs)nigger": "BIPOC",
	"negroid": "BIPOC",
	"nignog": "BIPOC",
	"nig nog": "BIPOC",
	"niglet": 'BIPOClet',
	"negress": "BIPOCette",
	"faggot": "cute twink",
	"fag": "strag",
	"(?<!\w)spic(?!\w)": "hard-working American",
	"(?<!\w)spics(?!\w)": "hard-working Americans",
	"kike": "jewish chad",
	"(?<!\w)heeb": "jewish chad",
	"daisy's destruction": "Cars 2",
	"daisys destruction": "Cars 2",
	"daisy destruction": "Cars 2",
	"pajeet": "sexy Indian dude",
	"hunter2": "*******",
	"dyke(?!\w)": "cute butch",
	"dykes": "cute butches",
}

if SITE_NAME == 'rDrama':
	SLURS |= {
		"retarded": "r-slurred",
		"a retard": "an r-slur",
		"retard": "r-slur",
		"pedophile": "p-dophile",
		"kill youself": "keep yourself safe",
		"kill yourself": "keep yourself safe",
		"kill yourselves": "keep yourselves safe",
		"latinos": "latinx",
		"latino": "latinx",
		"latinas": "latinx",
		"latina": "latinx",
		"hispanics": "latinx",
		"hispanic": "latinx",
		"autistic": "neurodivergent",
		"gamer": "g*mer",
		"journalist": "journ*list",
		"journalism": "journ*lism",
		"fake and gay": "fake and straight",
		"(?<!\w)rapist": "male feminist",
		"(?<!\w)pedo(?!\w)": "p-do",
		"(?<!\w)kys(?!\w)": "keep yourself safe",
		"republicans": 'rethuglicans',
		"republican party": 'rethuglican party',
		"america": 'ameriKKKa',
		"it's almost as if": "I'm an r-slur but",
		"it's almost like": "I'm an r-slur but",
		"its almost as if": "I'm an r-slur but",
		"its almost like": "I'm an r-slur but",
		"my brother in christ": "my brother in Allah (ﷻ)",
		"(?<!\w)cool (?!(it|down|off))": "fetch ",
		"(?<!\w)cool(?![\w ])": "fetch",
		"krayon(?! \()": "krayon (sister toucher)",
		"discord": "groomercord",
		"(?<!\w)allah(?! \()": "Allah (ﷻ)",
		"my wife(?! \()": "my wife (male)",
		"(?<!cow)tools(?!\w)": "cowtools",
		"explain": "mansplain",
		'nigga': 'neighbor',
		'(?<![\w.])cat(?!\w)': 'marsey',
		'(?<!\w)cats(?!\w)': 'marseys',
		'hello': 'hecko',
		'ryan gosling': 'literally me',
		'howdy': 'meowdy',
		'corgi': 'klenny',
		"right now": "right meow",
		"(?<!\/)linux": "GNU/Linux",
		'(?<!-)based': 'keyed',
		'(?<!\w)needful': 'sneedful',
		'think tank': 'twink tank',
	}

PROFANITIES = {
	'motherfucker': 'motherlover',
	'fuck': 'frick',
	'(?<!\w)ass(?!\w)': 'butt',
	'shitting': 'pooping',
	'damn': 'darn',
	'bitch(?!\w)': 'b-word',
	'toilet': 'potty',
	'(?<!\w)asshole': 'butthole',
	'(?<!\w)rape': 'r*pe',
	'(?<!\w)hell(?!\w)': 'heck',
	'(?<!\w)sex(?!\w)': 's*x',
	'(?<!\w)cum(?!\w)': 'c*m',
	'(?<!\w)dick': 'peepee',
	'cock(?!\w)': 'peepee',
	'cocks': 'peepees',
	'penis': 'peepee',
	'pussy': 'kitty',
	'pussies': 'kitties',
	'cunt': 'c*nt',
}



slur_single_words = "|".join([slur.lower() for slur in SLURS.keys()])
profanity_single_words = "|".join([profanity.lower() for profanity in PROFANITIES.keys()])
slur_regex = re.compile(f"<[^>]*>|{slur_single_words}", flags=re.I|re.A)
profanity_regex = re.compile(f"<[^>]*>|{profanity_single_words}", flags=re.I|re.A)

SLURS_FOR_REPLACING = {}
for k, val in SLURS.items():
	newkey = k.split('(?!')[0]
	if ')' in newkey:
		newkey = newkey.split(')')[1]
	SLURS_FOR_REPLACING[newkey] = val

PROFANITIES_FOR_REPLACING = {}
for k, val in PROFANITIES.items():
	newkey = k.split('(?!')[0]
	if ')' in newkey:
		newkey = newkey.split(')')[1]
	PROFANITIES_FOR_REPLACING[newkey] = val



def sub_matcher(match, X_FOR_REPLACING):
	group_num = 0
	match_str = match.group(group_num)
	if match_str.startswith('<'):
		return match_str
	else:
		repl = X_FOR_REPLACING[match_str.lower()]
		if "<img" not in repl:
			if match_str.isupper():
				return repl.upper()
			if match_str[0].isupper():
				return repl[0].upper() + repl[1:]
		return repl

def sub_matcher_slurs(match):
	return sub_matcher(match, SLURS_FOR_REPLACING)

def sub_matcher_profanities(match):
	return sub_matcher(match, PROFANITIES_FOR_REPLACING)



def censor_slurs_profanities(body, logged_user, is_plain=False):
	if not body: return ""

	if '<pre>' in body or '<code>' in body:
			return body

	if not logged_user or logged_user == 'chat' or logged_user.slurreplacer:
		body = slur_regex.sub(sub_matcher_slurs, body)

	if SITE_NAME == 'rDrama':
		if not logged_user or logged_user == 'chat' or logged_user.profanityreplacer:
			body = profanity_regex.sub(sub_matcher_profanities, body)

	if is_plain:
		body = body.replace(tranny, ':marseytrain:')
		body = body.replace(trannie, ':!marseytrain:')
		body = body.replace(troon, ':marseytrain2:')

	return body
