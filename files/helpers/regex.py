import random
import re
from random import choice, choices

from .config.const import *

NOT_IN_CODE_OR_LINKS = '(?!([^<]*<\/(code|pre|a)>|[^`\n]*`|(.|\n)*```))'

valid_username_regex = re.compile("^[\w\-]{3,25}$", flags=re.A)
valid_username_patron_regex = re.compile("^[\w\-]{1,25}$", flags=re.A)

mention_regex = re.compile('(?<![:/\w])@([\w\-]{1,30})' + NOT_IN_CODE_OR_LINKS, flags=re.A)
group_mention_regex = re.compile('(?<![:/\w])!([\w\-]{3,25})' + NOT_IN_CODE_OR_LINKS, flags=re.A|re.I)

everyone_regex = re.compile('(^|\s|>)!(everyone)' + NOT_IN_CODE_OR_LINKS, flags=re.A)

valid_password_regex = re.compile("^.{8,100}$", flags=re.A)

marseyaward_body_regex = re.compile(">[^<\s+]|[^>\s+]<", flags=re.A)

marseyaward_title_regex = re.compile("( *<img[^>]+>)+", flags=re.A)


emoji_name_regex = re.compile("[a-z0-9]{1,30}", flags=re.A)
tags_regex = re.compile("[a-z0-9: ]{1,200}", flags=re.A)
hat_regex = re.compile("[\w\-() ,]{1,50}", flags=re.A)
description_regex = re.compile("[^<>&\n\t]{1,300}", flags=re.A)

badge_name_regex = re.compile(r"[^\/.]+", flags=re.A)

valid_sub_regex = re.compile("^[\w\-]{3,25}$", flags=re.A)

query_regex = re.compile("(\w+):(\S+)", flags=re.A)

poll_regex = re.compile("(^|\n|>)\$\$([^\$\n]+)\$\$\s*?" + NOT_IN_CODE_OR_LINKS, flags=re.A)
bet_regex = re.compile("(^|\n|>)##([^#\n]+)##\s*?" + NOT_IN_CODE_OR_LINKS, flags=re.A)
choice_regex = re.compile("(^|\n|>)&&([^&\n]+)&&\s*?" + NOT_IN_CODE_OR_LINKS, flags=re.A)

html_comment_regex = re.compile("<!--.*-->", flags=re.A)

title_regex = re.compile("[^\w ]", flags=re.A)

controversial_regex = re.compile('["> ](https:\/\/old\.reddit\.com/r/\w{2,20}\/comments\/[\w\-.#&/=\?@%+]{5,250})["< ]', flags=re.A)

spoiler_regex = re.compile('\|\|(.+?)\|\|' + NOT_IN_CODE_OR_LINKS, flags=re.A)
reddit_regex = re.compile('(?<![\w/])\/?(([ruRU])\/(\w|-){2,25})' + NOT_IN_CODE_OR_LINKS, flags=re.A)
sub_regex = re.compile('(?<![\w/])\/?([hH]\/(\w|-){3,25})' + NOT_IN_CODE_OR_LINKS, flags=re.A)

strikethrough_regex = re.compile('(^|\s|>|")~{1,2}([^~]+)~{1,2}' + NOT_IN_CODE_OR_LINKS, flags=re.A)

mute_regex = re.compile("\/mute @?([\w\-]{1,30}) ([0-9]+)", flags=re.A|re.I)

emoji_regex = re.compile(f"<p>\s*(:[!#@\w\-]{{1,72}}:\s*)+<\/p>", flags=re.A)
emoji_regex2 = re.compile(f'(?<!"):([!#@\w\-]{{1,72}}?):(?!([^<]*<\/(code|pre)>|[^`]*`))', flags=re.A)

snappy_url_regex = re.compile('<a href="(https?:\/\/.+?)".*?>(.+?)<\/a>', flags=re.A)
snappy_youtube_regex = re.compile('<lite-youtube videoid="(.+?)" params="autoplay=1', flags=re.A)

email_regex = re.compile('[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{2,63}\.[A-Za-z]{2,63}', flags=re.A)

slur_regex = re.compile(f"<[^>]*>|{slur_single_words}", flags=re.I|re.A)
slur_regex_upper = re.compile(f"<[^>]*>|{slur_single_words.upper()}", flags=re.A)
profanity_regex = re.compile(f"<[^>]*>|{profanity_single_words}", flags=re.I|re.A)
profanity_regex_upper = re.compile(f"<[^>]*>|{profanity_single_words.upper()}", flags=re.A)

torture_regex = re.compile('(^|\s)(i|me)($|\s)', flags=re.I|re.A)
torture_regex2 = re.compile("(^|\s)(i'm)($|\s)", flags=re.I|re.A)
torture_regex3 = re.compile("(^|\s)(my|mine)($|\s)", flags=re.I|re.A)

#matches ". ", does not match "..." or a.b
sentence_ending_regex = re.compile('(?<!\.)(\.)(?=$|\n|\s)', flags=re.I|re.A)
normal_punctuation_regex = re.compile('(\"|\')', flags=re.I|re.A)
more_than_one_comma_regex = re.compile('\,\,+', flags=re.I|re.A)
#matches the various superlatives, but only if it as the start or end of a string or if it surrounded by spaces or is at the end of a word.
superlative_regex = re.compile('(?<=^|(?<=\s))(everyone|everybody|nobody|all|none|every|any|no one|anything)(?=$|\n|\s|[.?!,])', flags=re.I|re.A)
#like above, except only when totally doesn't already prefix
totally_regex = re.compile('(?<=^|(?<=\s))(?<!totally )(into)(?=$|\n|\s|[.?!,])', flags=re.I|re.A)
greeting_regex = re.compile('(?<=^|(?<=\s))(hello|hi|hey|hecko)(?=$|\n|\s|[.?!,])', flags=re.I|re.A)
like_before_regex = re.compile('(?<=^|(?<=\s))(?<!like )(just|only)(?=$|\n|\s|[.?!,])', flags=re.I|re.A)
like_after_regex = re.compile('(?<=^|(?<=\s))(i mean)(?! like)(?=$|\n|\s|[.?!,])', flags=re.I|re.A)
#match ! or ? but only if it isn't touching another ! or ?, or is in front of a letter
single_repeatable_punctuation = re.compile('(?<!!|\?)(!|\?)(?!!|\?)(?=\s|$)', flags=re.I|re.A)
#match "redpilled", to turn into "goodpilled" (extremely jankpilled but its whatever). Group 2 contained "ed" if exists
redpilled_regex = re.compile('(?<=^|(?<=\s))(redpill(ed)*)(?=$|\n|\s|[.?!,])', flags=re.I|re.A)
#match "based and Xpilled". To be turned into "comfy X vibes". Note that "X" is in group 2. No conditional "ed", "ed" will always be present
based_and_x_pilled_regex = re.compile('(?<=^|(?<=\s))(based and ([a-zA-Z]*)pilled)(?=$|\n|\s|[.?!,])', flags=re.I|re.A)
#match "based" to "comfy"
based_regex = re.compile('(?<=^|(?<=\s))(based)(?=$|\n|\s|[.?!,])', flags=re.I|re.A)
#match "Xpilled". To be turned into "X vibes". Note that "X" is in group 2, "ed" in group 3
x_pilled_regex = re.compile('(?<=^|(?<=\s))(([a-zA-Z]+)pill(ed)?)(?=$|\n|\s|[.?!,])', flags=re.I|re.A)
#match "Xmaxxx". To be turned into "normalize good Xs". Note that "X" is in group 2, "s" (after X) in group 3
xmax_regex = re.compile('(?<=^|(?<=\s))(([a-zA-Z]+?)(s)?max+)(?=$|\n|\s|[.?!,])', flags=re.I|re.A)
#same as above, except "Xmaxxed" this time (b/c I have crippling OCD and "normalized" isn't "normalize" + "ed") :marseyrage:
xmaxed_regex = re.compile('(?<=^|(?<=\s))(([a-zA-Z]+?)(s)?max+ed)(?=$|\n|\s|[.?!,])', flags=re.I|re.A)
#same as above, except "Xmaxxing" this time
xmaxing_regex = re.compile('(?<=^|(?<=\s))(([a-zA-Z]+?)(s)?max+ing)(?=$|\n|\s|[.?!,])', flags=re.I|re.A)
initial_part_regex = re.compile('(?<=^)(>+)', flags=re.I|re.A)

#matches "the" or is, but only if it is not followed by "fucking". https://regex101.com/r/yxuYsQ/2
the_fucking_regex = re.compile('(?<=^|(?<=\s))((?:the|a)( (?:only))?|((that )?(?:is|are|was|were|will be|would be)( (?:your|her|his|their|no|a|not|to|too|so|this|the|our|what))?( (a|the))?)|is)(?=\s)(?! fucking)' + NOT_IN_CODE_OR_LINKS, flags=re.I|re.A)
#matches a single question mark but only if it isn't preceded by ", bitch"
bitch_question_mark_regex = re.compile('(?<!\?|\!)(?<!, bitch)(\?)(?!!|\?)(?=\s|$)' + NOT_IN_CODE_OR_LINKS, flags=re.I|re.A)
#matches a single exclamation point but only if it isn't preceded by ", motherfucker"
exclamation_point_regex = re.compile('(?<!!|\?)(?<!, motherfucker)(!)(?!!|\?)(?=\s|$)' + NOT_IN_CODE_OR_LINKS, flags=re.I|re.A)

image_check_regex = re.compile(f'!\[\]\(((?!(https:\/\/({hosts})\/|\/)).*?)\)', flags=re.A)

video_regex_extensions = '|'.join(VIDEO_FORMATS)
video_sub_regex = re.compile(f'(?<!")(https:\/\/({hosts})\/[\w:~,()\-.#&\/=?@%;+]*?\.({video_regex_extensions}))' + NOT_IN_CODE_OR_LINKS, flags=re.A)

audio_regex_extensions = '|'.join(AUDIO_FORMATS)
audio_sub_regex = re.compile(f'(?<!")(https:\/\/({hosts})\/[\w:~,()\-.#&\/=?@%;+]*?\.({audio_regex_extensions}))' + NOT_IN_CODE_OR_LINKS, flags=re.A)

image_regex_extensions = '|'.join(IMAGE_FORMATS)
image_sub_regex = re.compile(f'(?<!")(https:\/\/[\w\-.#&/=\?@%;+,:]{{5,250}}(\.|\?format=)({image_regex_extensions})((\?|&)[\w\-.#&/=\?@%;+,:]*)?)(?=$|\s)' + NOT_IN_CODE_OR_LINKS, flags=re.I|re.A)

image_regex_extensions_no_gif = image_regex_extensions.replace('|gif', '')
imgur_regex = re.compile(f'(https:\/\/i\.imgur\.com\/[a-z0-9]+)\.({image_regex_extensions_no_gif})', flags=re.I|re.A)

giphy_regex = re.compile('(https:\/\/media\.giphy\.com\/media\/[a-z0-9]+\/giphy)\.gif', flags=re.I|re.A)

youtube_regex = re.compile('<a href="(https:\/\/youtube\.com\/watch\?[\w\-.#&/=?@%+;]{7,}).*?<\/a>' + NOT_IN_CODE_OR_LINKS, flags=re.I|re.A)
yt_id_regex = re.compile('[\w\-]{5,20}', flags=re.A)

rumble_regex = re.compile('https://rumble\.com/embed/([a-zA-Z0-9]*)(/\?pub=([a-zA-Z0-9]*))?', flags=re.I|re.A)
bare_youtube_regex = re.compile('https:\/\/youtube\.com\/watch\?([\w\-.#&/=?@%+;]{7,})', flags=re.I|re.A)
twitch_regex = re.compile('(https:\/\/)?(www\.)?twitch.tv\/(.*)', flags=re.I|re.A)

link_fix_regex = re.compile("(\[.*?\]\()(?!http|\/)(.*?\))" + NOT_IN_CODE_OR_LINKS, flags=re.A)

css_url_regex = re.compile('url\(\s*[\'"]?(.*)[\'"]?', flags=re.I|re.A)

linefeeds_regex = re.compile("([^\n])\n([^\n])", flags=re.A)

greentext_regex = re.compile("(\n|^)>([^ >][^\n]*)", flags=re.A)

allowed_domain_regex = re.compile("[a-z0-9\-.]+", flags=re.I|re.A)

reddit_to_vreddit_regex = re.compile('(^|>|")https:\/\/old.reddit.com\/(r|u)\/', flags=re.A)
twitter_to_nitter_regex = re.compile('(^|>|")https:\/\/twitter.com\/(?!i\/)', flags=re.A)
reddit_domain_regex = re.compile("(^|\s|\()https?:\/\/(reddit\.com|(?:(?:[A-z]{2})(?:-[A-z]{2})" "?|beta|i|m|pay|ssl|www|new|alpha)\.reddit\.com|libredd\.it|reddit\.lol)\/(u|(r\/(\w|-){2,25}\/)?comments)\/", flags=re.A)

color_regex = re.compile("[a-f0-9]{6}", flags=re.A)

# lazy match on the .*?, only match if there is trailing stuff
# Specifically match Snappy's way of formatting, this might break some losers' comments.
showmore_regex = re.compile(r"^(.*?</p>(?:</li></ul>)?)(\s*<p>.*)", flags=re.A|re.DOTALL)

search_token_regex = re.compile('"([^"]*)"|(\S+)', flags=re.A)

git_regex = re.compile("ref: (refs/.+)", flags=re.A)

pronouns_regex = re.compile("([a-z]{1,7})\/[a-z]{1,7}(\/[a-z]{1,7})?", flags=re.A|re.I)

html_title_regex = re.compile("<title>(.{1,200})</title>", flags=re.I)

def sub_matcher(match, upper=False, replace_with=SLURS_FOR_REPLACING):
	group_num = 0
	match_str = match.group(group_num)
	if match_str.startswith('<'):
		return match_str
	else:
		repl = replace_with[match_str.lower()]
		if not upper or "<img" in repl:
			return repl
		else:
			return repl.upper()

def sub_matcher_upper(match, replace_with=SLURS_FOR_REPLACING):
	return sub_matcher(match, upper=True, replace_with=replace_with)


# TODO: make censoring a bit better
def sub_matcher_slurs(match, upper=False):
	return sub_matcher(match, upper, replace_with=SLURS_FOR_REPLACING)

def sub_matcher_slurs_upper(match):
	return sub_matcher_slurs(match, upper=True)

def sub_matcher_profanities(match, upper=False):
	return sub_matcher(match, upper, replace_with=PROFANITIES_FOR_REPLACING)

def sub_matcher_profanities_upper(match):
	return sub_matcher_profanities(match, upper=True)

def censor_slurs(body, logged_user):
	if not body: return ""

	if '<pre>' in body or '<code>' in body:
			return body

	def replace_re(body, regex, regex_upper, sub_func, sub_func_upper):
		body = regex_upper.sub(sub_func_upper, body)
		return regex.sub(sub_func, body)

	if not logged_user or logged_user == 'chat' or logged_user.slurreplacer:
		body = replace_re(body, slur_regex, slur_regex_upper, sub_matcher_slurs, sub_matcher_slurs_upper)
	if SITE_NAME == 'rDrama':
		if not logged_user or logged_user == 'chat' or logged_user.profanityreplacer:
			body = replace_re(body, profanity_regex, profanity_regex_upper, sub_matcher_profanities, sub_matcher_profanities_upper)

	return body

commands = {
	"fortune": FORTUNE_REPLIES,
	"factcheck": FACTCHECK_REPLIES,
	"8ball": EIGHTBALL_REPLIES,
	"roll": range(1, 10000),
	"coinflip": COINFLIP_HEADS_OR_TAILS,
}

command_regex = re.compile("(\s|^)#(fortune|factcheck|8ball|roll|coinflip)", flags=re.A|re.I)

def command_regex_matcher(match, upper=False):
	if match.group(2) == 'coinflip' and random.random() < 0.01:
		result = COINFLIP_EDGE
	else:
		result = str(choice(commands[match.group(2).lower()]))
		if match.group(2) == 'roll':
			color = tuple(choices(range(256), k=3))
			result = f'<b style="color:rgb{color}">Your roll: {result}</b>'
	return match.group(1) + result

reason_regex_post = re.compile('(/post/[0-9]+)', flags=re.A)
reason_regex_comment = re.compile('(/comment/[0-9]+)', flags=re.A)

numbered_list_regex = re.compile('((\s|^)[0-9]+)\. ', flags=re.A)

image_link_regex = re.compile(f"https:\/\/(i\.)?{SITE}\/(chat_)?images\/[0-9]{{11,17}}r?\.webp", flags=re.A)

video_link_regex = re.compile(f"https://(videos\.)?{SITE}\/(videos\/)?[0-9a-zA-Z._-]{{4,66}}\.({video_regex_extensions})", flags=re.A)

asset_image_link_regex = re.compile(f"https:\/\/(i\.)?{SITE}\/assets\/images\/[\w\/]+.webp(\?x=\d+)?", flags=re.A)
