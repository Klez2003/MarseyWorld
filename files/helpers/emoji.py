from os import path, listdir
from enum import Enum

from sqlalchemy.sql import func

from files.classes.emoji import Emoji

from files.helpers.config.const import *
from files.helpers.const_stateful import *
from files.helpers.regex import *
from files.helpers.get import *

class EmojiEnding(Enum):
	PAT = 'pat'
	TALKING = 'talking'
	GENOCIDE = 'genocide'
	LOVE = 'love'
	TYPING = 'typing'

SPECIAL_EMOJIS = {
	'capylove': ['love'],
	'marseycornlove': ['love'],
	'marseyunpettable': ['pat'],
}

def isTerminated(emoji, ending, endings):
	if(emoji.endswith(ending) and ending in endings):
		return True
	
def isEnding(emoji, ending):
	if emoji.endswith(ending):
		if(SPECIAL_EMOJIS.get(emoji) and ending in SPECIAL_EMOJIS[emoji]):
			return False
		return True

def find_all_emoji_endings(emoji):
	endings = []

	is_non_ending_found = False
	while not is_non_ending_found:
		for ending in [e.value for e in EmojiEnding]:
			if isEnding(emoji, ending):
				if(isTerminated(emoji, ending, endings)):
					is_non_ending_found = True
					break
				endings.append(ending)
				emoji = emoji[:-len(ending)]
				continue
		is_non_ending_found = True

	if emoji.endswith('random'):
		kind = emoji.split('random')[0].title()
		if kind == 'Donkeykong': kind = 'Donkey Kong'
		elif kind == 'Marseyflag': kind = 'Marsey Flags'
		elif kind == 'Marseyalphabet': kind = 'Marsey Alphabet'

		if kind in EMOJI_KINDS:
			emoji = g.db.query(Emoji.name).filter_by(kind=kind, nsfw=False).order_by(func.random()).first()[0]

	return endings, emoji

def render_emoji(html, regexp, golden, emojis_used, b=False, is_title=False, obj=None):
	emojis = list(regexp.finditer(html))
	captured = set()

	for i in emojis:
		if i.group(0) in captured: continue
		captured.add(i.group(0))

		emoji = i.group(1).lower()
		attrs = ''

		if is_title and '#' in emoji:
			if obj:
				obj.title = obj.title.replace(emoji, emoji.replace('#',''))
			emoji = emoji.replace('#','')

		if golden and len(emojis) <= 20 and ('marsey' in emoji or emoji in MARSEYS_CONST2) and random.random() < 0.005:
			attrs += ' ' + random.choice(('g', 'glow', 'party'))

		old = emoji
		emoji = emoji.replace('!','').replace('#','')
		
		if emoji in ALPHABET_MARSEYS:
			attrs += ' alpha'
		elif b:
			attrs += ' b'

		emoji_partial_pat = '<img alt=":{0}:" loading="lazy" src="{1}"{2}>'
		emoji_partial = '<img alt=":{0}:" data-bs-toggle="tooltip" loading="lazy" src="{1}" title=":{0}:"{2}>'
		emoji_html = None

		ending_modifiers, emoji = find_all_emoji_endings(emoji)

		is_talking = 'talking' in ending_modifiers
		is_patted = 'pat' in ending_modifiers
		is_talking_first = ending_modifiers.index('pat') > ending_modifiers.index('talking') if is_talking and is_patted else False
		is_loved = 'love' in ending_modifiers
		is_genocided = 'genocide' in ending_modifiers
		is_typing = 'typing' in ending_modifiers
		is_user = emoji.startswith('@')

		end_modifier_length = 3 if is_patted else 0
		end_modifier_length = end_modifier_length + 7 if is_talking else end_modifier_length

		hand_html = f'<img loading="lazy" src="{SITE_FULL_IMAGES}/i/hand.webp">' if is_patted and emoji != 'marseyunpettable' else ''
		talking_html = f'<img loading="lazy" src="{SITE_FULL_IMAGES}/i/talking.webp">' if is_talking else ''
		typing_html = f'<img loading="lazy" src="{SITE_FULL_IMAGES}/i/typing-hands.webp">' if is_typing else ''
		loved_html = f'<img loading="lazy" src="{SITE_FULL_IMAGES}/i/love-foreground.webp" alt=":{old}:" {attrs}><img loading="lazy" alt=":{old}:" src="{SITE_FULL_IMAGES}/i/love-background.webp" {attrs}>'
		genocide_attr = ' cide' if is_genocided else ''

		modifier_html = ''
		if is_talking and is_patted:
			modifier_html = f'{talking_html}{hand_html}' if is_talking_first else f'{hand_html}{talking_html}'
		elif is_patted:
			modifier_html = hand_html
		elif is_talking:
			modifier_html = talking_html

		if is_loved:
			modifier_html = f'{modifier_html}{loved_html}'

		if is_typing:
			modifier_html = f'{modifier_html}{typing_html}'

		if is_patted or is_talking or is_genocided or is_loved or is_typing:
			if path.isfile(f"files/assets/images/emojis/{emoji}.webp"):
				emoji_html = f'<span alt=":{old}:" data-bs-toggle="tooltip" title=":{old}:"{genocide_attr}>{modifier_html}{emoji_partial_pat.format(old, f"{SITE_FULL_IMAGES}/e/{emoji}.webp", attrs)}</span>'
			elif is_user:
				if u := get_user(emoji[1:], graceful=True):
					emoji_html = f'<span alt=":{old}:" data-bs-toggle="tooltip" title=":{old}:"{genocide_attr}>{modifier_html}{emoji_partial_pat.format(old, f"/pp/{u.id}", attrs)}</span>'
		elif path.isfile(f'files/assets/images/emojis/{emoji}.webp'):
			emoji_html = emoji_partial.format(old, f'{SITE_FULL_IMAGES}/e/{emoji}.webp', attrs)


		if emoji_html:
			emojis_used.add(emoji)
			html = re.sub(f'(?<!"){i.group(0)}(?![^<]*<\/(code|pre)>)', emoji_html, html)
	return html
