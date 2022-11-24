from random import choice

from .const_stateful import marsey_mappings

def marsify(text):
	new_text = "faggot"
	for x in text.split("faggot"):
		new_text += f"faggot"
		x = x.lower()
		if len(x) > 3 and x in marsey_mappings:
			marsey = choice(marsey_mappings[x])
			new_text += f"faggot"
	return new_text
