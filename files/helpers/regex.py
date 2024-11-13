import random
import re
import regex
from flask import g

from files.classes.media import *
from .config.const import *

NOT_IN_CODE_OR_LINKS = '(?!([^<]*<\/(code|pre|a)>|[^`\n]*`))'
NOT_IN_CODE_OR_LINKS_OR_SPOILER = '(?!([^<]*<\/(code|pre|a|spoiler)>|[^`\n]*`))'

valid_username_regex = re.compile("^[\w-]{3,25}$", flags=re.A)
valid_username_patron_regex = re.compile("^[\w-]{1,25}$", flags=re.A)

mention_regex = re.compile('(?<![:/\w])@([\w-]{1,30})' + NOT_IN_CODE_OR_LINKS, flags=re.A)
group_mention_regex = re.compile('(?<![:/\w])!([\w-]{3,25})' + NOT_IN_CODE_OR_LINKS, flags=re.A|re.I)

chat_adding_regex = re.compile('\+@([\w-]{1,30})' + NOT_IN_CODE_OR_LINKS, flags=re.A)
chat_kicking_regex = re.compile('\-@([\w-]{1,30})' + NOT_IN_CODE_OR_LINKS, flags=re.A)
chat_jannying_regex = re.compile('\*@([\w-]{1,30})' + NOT_IN_CODE_OR_LINKS, flags=re.A)
chat_dejannying_regex = re.compile(r'(^|\s)/@([\w-]{1,30})' + NOT_IN_CODE_OR_LINKS, flags=re.A)

everyone_regex = re.compile('(^|\s|>)!(everyone)' + NOT_IN_CODE_OR_LINKS, flags=re.A)

valid_password_regex = re.compile("^.{8,100}$", flags=re.A)

marseyaward_body_regex = re.compile(">[^<\s+]|[^>\s+]<", flags=re.A)

marseyaward_title_regex = re.compile("( *<img[^>]+>)+", flags=re.A)


emoji_name_regex = re.compile("[a-z0-9]{1,30}", flags=re.A)
tags_regex = re.compile("[a-z0-9: ]{1,200}", flags=re.A)
hat_name_regex = re.compile("[\w\-() ,]{1,50}", flags=re.A)
description_regex = re.compile("[^<>&\n\t]{1,300}", flags=re.A)

badge_name_regex = re.compile(r"[^\/.]+", flags=re.A)

hole_group_name_regex = re.compile("^[\w-]{3,25}$", flags=re.A)

query_regex = re.compile("(\w+):(\S+)", flags=re.A)

poll_regex = re.compile("(^|\n|>)\$\$([^\n]+?)\$\$\s*?" + NOT_IN_CODE_OR_LINKS, flags=re.A)
bet_regex = re.compile("(^|\n|>)##([^\n]+?)##\s*?" + NOT_IN_CODE_OR_LINKS, flags=re.A)
choice_regex = re.compile("(^|\n|>)&&([^\n]+?)&&\s*?" + NOT_IN_CODE_OR_LINKS, flags=re.A)

html_comment_regex = re.compile("<!--.*-->", flags=re.A)

title_regex = re.compile("[^\w ]", flags=re.A)

controversial_regex = re.compile('https:\/\/old\.reddit\.com\/r\/\w{2,20}\/comments\/[\w\-.#&/=\?@%+]{5,250}', flags=re.A)

spoiler_regex = re.compile('\|\|(.+?)\|\|' + NOT_IN_CODE_OR_LINKS, flags=re.A)
hole_mention_regex = re.compile('(?<![\w/"])\/?([hH]\/[\w-]{3,25})' + NOT_IN_CODE_OR_LINKS, flags=re.A)

strikethrough_regex = re.compile(r'(?<!\\)~{1,2}([^~]+)~{1,2}' + NOT_IN_CODE_OR_LINKS, flags=re.A)

mute_regex = re.compile("\/mute @?([\w-]{1,30}) ([0-9]+)" + NOT_IN_CODE_OR_LINKS, flags=re.A|re.I)
unmute_regex = re.compile("\/unmute @?([\w-]{1,30})" + NOT_IN_CODE_OR_LINKS, flags=re.A|re.I)

emoji_regex = re.compile(f"<p>\s*(:[!#@\w\-]{{1,72}}:\s*)+<\/p>", flags=re.A)
emoji_regex2 = re.compile(f'(?<!"):([!#@\w\-]{{1,72}}?):(?![^<]*<\/(code|pre)>)', flags=re.A)

snappy_url_regex = re.compile('<a href="(https?:\/\/.+?)".*?>(.+?)<\/a>', flags=re.A)

email_regex = re.compile('[A-Za-z0-9._%+-]{1,64}@[A-Za-z0-9.-]{2,63}\.[A-Za-z]{2,63}', flags=re.A)

torture_regex = re.compile('(^|\s)(i|me)($|\s)', flags=re.I|re.A)
torture_regex2 = re.compile("(^|\s)(i'?m)($|\s)", flags=re.I|re.A)
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
the_fucking_regex = regex.compile('(?<!>.*)(^|\s)((?:the|a)( (?:only))?|((that )?(?:is|are|was|were|will be|would be)( (?:your|her|his|their|no|a|not|to|too|so|this|the|our|what))?( (a|the))?)|is)(?=\s)(?! fucking)' + NOT_IN_CODE_OR_LINKS, flags=re.I|re.A)
#matches a single question mark but only if it isn't preceded by ", bitch"
bitch_question_mark_regex = regex.compile('(?<!\?|\!|>.*)(?<!, bitch)(\?)(?!!|\?)(?=\s|$)' + NOT_IN_CODE_OR_LINKS, flags=re.I|re.A)
#matches a single exclamation point but only if it isn't preceded by ", motherfucker"
exclamation_point_regex = regex.compile('(?<!!|\?|>.*)(?<!, motherfucker)(!)(?!!|\?)(?=\s|$)' + NOT_IN_CODE_OR_LINKS, flags=re.I|re.A)

image_check_regex = re.compile(f'!\[\]\(((?!(https:\/\/({hosts})\/|\/)).*?)\)', flags=re.A)

video_regex_extensions = '|'.join(VIDEO_FORMATS)
video_sub_regex = re.compile(f'(?<!")(https:\/\/({hosts})\/[\w:~,()\-.#&\/=?@%;+]*?\.({video_regex_extensions}))' + NOT_IN_CODE_OR_LINKS_OR_SPOILER, flags=re.A|re.I)

def video_sub_regex_matcher(match, obj):
	url = match.group(1)
	if url.startswith(SITE_FULL_VIDEOS):
		filename = '/videos/' + url.split(f'{SITE_FULL_VIDEOS}/')[1]
		g.db.flush()
		media = g.db.get(Media, filename)
		if media:
			if obj:
				if not obj.id: raise Exception("The thing that never happens happened again")
				if str(obj.__class__) == "<class 'files.classes.post.Post'>":
					existing = g.db.query(MediaUsage.id).filter_by(filename=filename, post_id=obj.id).one_or_none()
					if not existing:
						media_usage = MediaUsage(filename=filename)
						media_usage.post_id = obj.id
						g.db.add(media_usage)
				else:			
					existing = g.db.query(MediaUsage.id).filter_by(filename=filename, comment_id=obj.id).one_or_none()
					if not existing:
						media_usage = MediaUsage(filename=filename)
						media_usage.comment_id = obj.id
						g.db.add(media_usage)

			if media.posterurl:
				return 	f'<p class="resizable"><video poster="{media.posterurl}" controls preload="none" src="{url}"></video></p>'
	return f'<p class="resizable"><video controls preload="none" src="{url}"></video></p>'

audio_regex_extensions = '|'.join(AUDIO_FORMATS)
audio_sub_regex = re.compile(f'(?<!")(https:\/\/({hosts})\/[\w:~,()\-.#&\/=?@%;+]*?\.({audio_regex_extensions}))' + NOT_IN_CODE_OR_LINKS, flags=re.A)

image_regex_extensions = '|'.join(IMAGE_FORMATS)
image_sub_regex = re.compile(f'(?<!")(https:\/\/[\w\-.#&/=\?@%;+,:]{{5,250}}(\.|@|\?format=)({image_regex_extensions})((\?|&)[\w\-.#&/=\?@%;+,:]*)?)(?=$|\s|<)' + NOT_IN_CODE_OR_LINKS, flags=re.I|re.A)

image_regex_extensions_no_gif = image_regex_extensions.replace('|gif', '')
imgur_regex = re.compile(f'^(https:\/\/i\.imgur\.com\/[a-z0-9]+)\.({image_regex_extensions_no_gif})', flags=re.I|re.A)

rumble_regex = re.compile('https://rumble\.com/embed/([a-zA-Z0-9]*)(/\?pub=([a-zA-Z0-9]*))?', flags=re.I|re.A)

twitch_regex = re.compile('(https:\/\/)?(www\.)?twitch.tv\/(\w*)', flags=re.I|re.A)

link_fix_regex = re.compile("(\[.*?\]\()(?!http|\/)(.*?\))" + NOT_IN_CODE_OR_LINKS, flags=re.A)

css_url_regex = re.compile('url\([\'"]?((.|\n)*?)[",);}$]', flags=re.I|re.A) # AEVANN, DO NOT TOUCH THIS, IT WENT THROUGH A MILLION ITERATIONS, IT'S PERFECT NOW

linefeeds_regex = re.compile("([^\n])\n([^\n])", flags=re.A)

greentext_regex = re.compile("(\n|^)>([^ >][^\n]*)", flags=re.A)

allowed_domain_regex = re.compile("[a-z0-9\-.]+", flags=re.I|re.A)

twitter_domain_regex = re.compile('(^|>|")https:\/\/(x|twitter).com\/(?!i\/)', flags=re.A)

instagram_to_imgsed_regex = re.compile('(^|>|")https:\/\/instagram.com\/(?!reel\/)', flags=re.A)

color_regex = re.compile("[a-f0-9]{6}", flags=re.A)

# lazy match on the .*?, only match if there is trailing stuff
# Specifically match Snappy's way of formatting, this might break some losers' comments.
showmore_regex = re.compile(r"^(.*?</p>(?:</li></ul>)?)(\s*<p>.*)", flags=re.A|re.DOTALL)

search_token_regex = re.compile('("[^"]*")|(\S+)', flags=re.A)

git_regex = re.compile("ref: (refs/.+)", flags=re.A)

pronouns_regex = re.compile("(\w{1,7})\/\w{1,7}(\/\w{1,7})?", flags=re.A)

html_title_regex = re.compile("<title>(.{1,200})</title>", flags=re.I)

excessive_css_scale_regex = re.compile("scale\([^)]*?(\d{2})", flags=re.A)

word_alert_regex = re.compile(r'\b(764|o9a|9 angles|hurtcore|pthc|oldcom|cvlt|hn|harm ?nation|cut ?sign|lore ?book|million ?pity)\b', flags=re.A|re.I)

commands = {
	"fortune": FORTUNE_REPLIES,
	"factcheck": FACTCHECK_REPLIES,
	"8ball": EIGHTBALL_REPLIES,
	"coinflip": COINFLIP_HEADS_OR_TAILS,
}

command_regex = re.compile("(\s|^)#(fortune|factcheck|8ball|roll([1-9][0-9]*)|coinflip)", flags=re.A|re.I)

def command_regex_matcher(match):
	if match.group(2) == 'coinflip' and random.random() < 0.01:
		result = COINFLIP_EDGE
	else:
		if match.group(2).startswith('roll'):
			max_num = int(match.group(3))
			result = random.randint(1, max_num)
			color = tuple(random.choices(range(256), k=3))
			result = f'<b style="color:rgb{color}">Your roll (1-{max_num}): {result}</b>'
		else:
			result = str(random.choice(commands[match.group(2).lower()]))
	return match.group(1) + result

reason_regex_post = re.compile('(/post/[0-9]+)', flags=re.A)
reason_regex_comment = re.compile('(/comment/[0-9]+)', flags=re.A)

numbered_list_regex = re.compile('((\n|^)[> ]*[0-9]+)[\.)] ', flags=re.A)
unnumbered_list_regex = re.compile('((\n|^)[> ]*)\+ ', flags=re.A)

image_link_regex = re.compile(f"https:\/\/(i\.)?{SITE}\/(chat_)?images\/[0-9]{{11,17}}r?\.webp", flags=re.A)

video_link_regex = re.compile(f"https://(videos2?\.)?{SITE}\/(videos\/)?[0-9a-zA-Z._-]{{4,66}}\.({video_regex_extensions})", flags=re.A)

asset_image_link_regex = re.compile(f"https:\/\/(i\.)?{SITE}\/assets\/images\/[\w\/]+.webp(\?x=\d+)?", flags=re.A)

search_regex_1 = re.compile(r'[\0():|&*!<>]', flags=re.A)
search_regex_2 = re.compile(r"'", flags=re.A)
search_regex_3 = re.compile(r'\s+', flags=re.A)

###OWOIFY

owo_word_regex = re.compile(r'[^\s]+', flags=re.A)
owo_space_regex = re.compile(r'\s+', flags=re.A)
owo_ignore_links_images_regex = re.compile(r'\]\(', flags=re.A)
owo_ignore_emojis_regex = re.compile(r':[!#@a-z0-9_\-]+:', flags=re.I|re.A)
owo_ignore_the_Regex = re.compile(r'\bthe\b', flags=re.I|re.A)


###LinkifyFilter

tlds = ( # Original gTLDs and ccTLDs
	'ac','ad','ae','aero','af','ag','ai','al','am','an','ao','aq','ar','arpa','as','asia','at',
	'au','aw','ax','az','ba','bb','bd','be','bf','bg','bh','bi','biz','bj','bm','bn','bo','br',
	'bs','bt','bv','bw','by','bz','ca','cafe','cat','cc','cd','cf','cg','ch','ci','ck','cl',
	'cm','cn','co','com','coop','cr','cu','cv','cx','cy','cz','de','dj','dk','dm','do','dz','ec',
	'edu','ee','eg','er','es','et','eu','fi','fj','fk','fm','fo','fr','ga','gb','gd','ge','gf',
	'gg','gh','gi','gl','gm','gn','gov','gp','gq','gr','gs','gt','gu','gw','gy','hk','hm','hn',
	'hr','ht','hu','id','ie','il','im','in','info','int','io','iq','ir','is','it','je','jm','jo',
	'jobs','jp','ke','kg','kh','ki','km','kn','kp','kr','kw','ky','kz','la','lb','lc','li','lk',
	'lr','ls','lt','lu','lv','ly','ma','mc','md','me','mg','mh','mil','mk','ml','mm','mn','mo',
	'mobi','mp','mq','mr','ms','mt','mu','museum','mv','mw','mx','my','mz','na','name',
	'nc','ne','net','nf','ng','ni','nl','no','np','nr','nu','nz','om','org','pa','pe','pf','pg',
	'ph','pk','pl','pm','pn','post','pr','pro','ps','pt','pw','qa','re','ro','rs','ru','rw',
	'sa','sb','sc','sd','se','sg','sh','si','sj','sk','sl','sm','sn','so','social','sr','ss','st',
	'su','sv','sx','sy','sz','tc','td','tel','tf','tg','th','tj','tk','tl','tm','tn','to','tp',
	'tr','travel','tt','tv','tw','tz','ua','ug','uk','us','uy','uz','va','vc','ve','vg','vi','vn',
	'vu','wf','ws','xn','xxx','ye','yt','yu','za','zm','zw',
	# New gTLDs
	'app','cleaning','club','dev','farm','florist','fun','gay','lgbt','life','lol',
	'moe','mom','monster','new','news','one','online','pics','press','pub','site','blog',
	'vip','win','world','wtf','xyz','video','host','art','media','wiki','tech',
	'cooking','network','party','goog','markets','today','beauty','camp','top',
	'red','city','quest','works','soy','zone','gl',
	)

protocols = ('http', 'https')

sanitize_url_regex = re.compile(
		r"""\(*# Match any opening parentheses.
		\b(?<![@.])(?:(?:{0}):/{{0,3}}(?:(?:\w+:)?\w+@)?)?# http://
		([\w-]+\.)+(?:{1})(?:\:[0-9]+)?(?!\.\w)\b# xx.yy.tld(:##)?
		(?:[/?][^#\s\{{\}}\|\\\^\[\]`<>"]*)?
			# /path/zz (excluding "unsafe" chars from RFC 1738,
			# except for ~, which happens in practice)
		(?:\#[^#\s\|\\\^\[\]`<>"]*)?
			# #hash (excluding "unsafe" chars from RFC 1738,
			# except for ~, which happens in practice)
		""".format(
			"|".join(sorted(protocols)), "|".join(sorted(tlds))
		),
		re.X | re.U,
	)

###REDDIT

#sanitizing
reddit_mention_regex = re.compile('(^|[>\s])\/?(r|u)(\/[\w-]{2,25})' + NOT_IN_CODE_OR_LINKS, flags=re.I|re.A)
reddit_domain_regex = re.compile("(^|\s|\()https?:\/\/(redd.it\/|((www\.|new\.)?reddit\.com|redd\.it)\/(u\/(?![\w-]{2,25}\/s\/)|user\/|(r\/\w{2,25}\/)?comments\/|r\/\w{2,25}\/?$))", flags=re.A)
reddit_comment_link_regex = re.compile("https:\/\/old.reddit.com\/r\/\w{2,25}\/comments(\/\w+){3}\/?.*", flags=re.A)

#gevent
reddit_s_url_regex = re.compile("https:\/\/(www\.)?reddit.com\/(r|u|user)\/[\w-]{2,25}\/s\/\w{10}\/?", flags=re.A)
tiktok_t_url_regex = re.compile("https:\/\/(www\.|vm\.)?tiktok.com(\/t)?\/\w{9}\/?", flags=re.A)

#run-time
reddit_to_vreddit_regex = re.compile('(^|>|")https:\/\/old.reddit.com\/(r|u|user)\/', flags=re.A)

#post search
subreddit_name_regex = re.compile('\w{2,25}', flags=re.A)


###YOUTUBE

#sanitize
youtube_regex = re.compile('<a href="(https:\/\/youtube\.com\/watch\?v=[\w-]{11}[\w&;=-]*)" rel="nofollow noopener" target="_blank">(https:\/\/)?youtube\.com\/watch\?v=[\w-]{11}[\w&;=-]*<\/a>' + NOT_IN_CODE_OR_LINKS, flags=re.I|re.A)

#sanitize and song
yt_id_regex = re.compile('[\w-]{11}', flags=re.A)

#orgy
bare_youtube_regex = re.compile('https:\/\/youtube\.com\/watch\?v=[\w-]{11}[\w&;=]*', flags=re.I|re.A)
