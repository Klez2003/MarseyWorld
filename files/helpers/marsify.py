import random

from .const_stateful import MARSEY_MAPPINGS


def marsify(text, chud_phrase, seed):
	if '`' in text or '<pre>' in text or '<code>' in text:
		return text

	chud_words = chud_phrase.split() if chud_phrase else []

	new_text = ''
	for x in text.split(' '):
		new_text += f'{x} '
		x = x.lower()
		if x in chud_words: continue
		if len(x) >= 5 and x in MARSEY_MAPPINGS:
			random.seed(seed)
			marsey = random.choice(MARSEY_MAPPINGS[x])
			random.seed()
			new_text += f':{marsey}: '
	return new_text
