import random
from files.helpers.regex import *

def dyslexia(string, chud_phrase):
	if "`" in string or "```" in string or "<code>" in string or "<pre>" in string:
		return string

	new_lines = []
	for line in string.splitlines():
		if chud_phrase and chud_phrase in line:
			new_lines.append(line)
			continue

		new_words = []
		for word in line.split(" "):
			if not dyslexia_word_regex.fullmatch(word):
				new_words.append(word)
				continue

			if len(word) > 3:
				idx = random.randint(1, len(word) - 3)
				word = word[:idx] + word[idx + 1] + word[idx] + word[idx + 2:]
			new_words.append(word)

		new_lines.append(" ".join(new_words))

	return "\n".join(new_lines)