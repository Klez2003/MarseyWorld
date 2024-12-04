import string

from owoify.structures.word import Word
from owoify.utility.interleave_arrays import interleave_arrays
from owoify.utility.presets import *

from files.helpers.regex import *

# Includes, excerpts, and modifies some functions from:
# https://github.com/deadshot465/owoify-py @ owoify/owoify.py


OWO_EXCLUDE_PATTERNS = [
	owo_ignore_links_images_regex, # links []() and images ![]()
		# NB: May not be effective when URL part contains literal spaces vs %20
		# Also relies on owoify replacements currently not affecting symbols.
	owo_ignore_emojis_regex, #emojis
	owo_ignore_the_Regex, # exclude: 'the' ↦ 'teh'
	sanitize_url_regex, # bare links
	user_mention_regex, # mentions
	group_mention_regex, #ping group mentions
	reddit_mention_regex, #/u/ and /r/
	command_regex, # markup commands
]

def owoify(source, chud_phrase):
	if '`' in source or '<pre>' in source or '<code>' in source:
		return source

	word_matches = owo_word_regex.findall(source)
	space_matches = owo_space_regex.findall(source)

	words = [Word(s) for s in word_matches]
	spaces = [Word(s) for s in space_matches]

	ignored_words = chud_phrase.lower().split() if chud_phrase else []

	for pattern in (poll_regex, choice_regex, bet_regex):
		matches = [x.group(0) for x in pattern.finditer(source.lower())]
		for match in matches:
			ignored_words += match.split()

	words = list(map(lambda w: owoify_map_token_custom(w, ignored_words), words))

	result = interleave_arrays(words, spaces)
	result_strings = list(map(lambda w: str(w), result))
	return ''.join(result_strings)

def owoify_map_token_custom(token, ignored_words):
	word_without_punc = token.word.lower().translate(str.maketrans('', '', string.punctuation))

	if word_without_punc in ignored_words:
		return token

	for pattern in OWO_EXCLUDE_PATTERNS:
		# if pattern appears anywhere in token, do not owoify.
		if pattern.search(token.word):
			return token

	# Original Owoification Logic (sans cases for higher owo levels)
	for func in SPECIFIC_WORD_MAPPING_LIST:
		token = func(token)

	for func in OWO_MAPPING_LIST:
		token = func(token)
	# End Original Owoification Logic

	return token
