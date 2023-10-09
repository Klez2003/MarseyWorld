from random import choice

from .const_stateful import MARSEY_MAPPINGS

def marsify(text):
	if '`' in text or '<pre>' in text or '<code>' in text:
		return text

	new_text = ''
	for x in text.split(' '):
		new_text += f'{x} '
		x = x.lower()
		if len(x) >= 5 and x in MARSEY_MAPPINGS:
			marsey = choice(MARSEY_MAPPINGS[x])
			new_text += f':{marsey}: '
	return new_text
