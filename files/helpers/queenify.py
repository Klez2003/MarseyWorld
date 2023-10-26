from bs4 import BeautifulSoup

from files.helpers.regex import *

def queenify_tag_string(string):
	if not string: return string

	result = initial_part_regex.search(string)
	initial = result.group(1) if result else ""
	string = string.lower()
	string = initial_part_regex.sub("", string)
	string = sentence_ending_regex.sub(", and", string)
	string = superlative_regex.sub(r"literally \g<1>", string)
	string = totally_regex.sub(r"totally \g<1>", string)
	string = single_repeatable_punctuation.sub(r"\g<1>\g<1>\g<1>", string)
	string = greeting_regex.sub(r"hiiiiiiiiii", string)
	string = like_after_regex.sub(r"\g<1> like", string)
	string = like_before_regex.sub(r"like \g<1>", string)
	string = redpilled_regex.sub(r"goodpill\g<2>", string)
	string = based_and_x_pilled_regex.sub(r"comfy \g<2> vibes", string)
	string = based_regex.sub(r"comfy", string)
	string = x_pilled_regex.sub(r"\g<2> vibes", string)
	string = xmax_regex.sub(r"normalize good \g<2>s", string)
	string = xmaxing_regex.sub(r"normalizing good \g<2>s", string)
	string = xmaxed_regex.sub(r"normalized good \g<2>s", string)

	string = normal_punctuation_regex.sub("", string)
	string = more_than_one_comma_regex.sub(",", string)
	if string[-5:] == ', and':
		string = string[:-5]

	if random.random() < 0.5:
		girl_phrase = random.choice(GIRL_PHRASES)
		string = girl_phrase.replace("$", string)
	
	return initial + string

def queenify_html(html):
	if '<p>&amp;&amp;' in html or '<p>$$' in html or '<p>##' in html:
		return html

	soup = BeautifulSoup(html, 'lxml')
	tags = soup.html.body.find_all(lambda tag: tag.name not in {'blockquote','codeblock','pre'} and tag.string, recursive=False)
	for tag in tags:
		tag.string.replace_with(queenify_tag_string(tag.string))
	
	return str(soup).replace('<html><body>','').replace('</body></html>','')
