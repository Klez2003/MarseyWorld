import functools
import random
import re
import signal
from functools import partial
from os import path, listdir
from typing import Any
from urllib.parse import parse_qs, urlparse, unquote

import bleach
from bleach.css_sanitizer import CSSSanitizer
from bleach.linkifier import LinkifyFilter
from bs4 import BeautifulSoup
from mistletoe import markdown

from files.classes.domains import BannedDomain
from files.classes.mod_logs import ModAction
from files.classes.notifications import Notification
from files.classes.group import Group

from files.helpers.config.const import *
from files.helpers.const_stateful import *
from files.helpers.regex import *
from files.helpers.get import *

TLDS = ( # Original gTLDs and ccTLDs
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
	'ph','pk','pl','pm','pn','post','pr','pro','ps','pt','pw','py','qa','re','ro','rs','ru','rw',
	'sa','sb','sc','sd','se','sg','sh','si','sj','sk','sl','sm','sn','so','social','sr','ss','st',
	'su','sv','sx','sy','sz','tc','td','tel','tf','tg','th','tj','tk','tl','tm','tn','to','tp',
	'tr','travel','tt','tv','tw','tz','ua','ug','uk','us','uy','uz','va','vc','ve','vg','vi','vn',
	'vu','wf','ws','xn','xxx','ye','yt','yu','za','zm','zw',
	# New gTLDs
	'app','cleaning','club','dev','farm','florist','fun','gay','lgbt','life','lol',
	'moe','mom','monster','new','news','online','pics','press','pub','site','blog',
	'vip','win','world','wtf','xyz','video','host','art','media','wiki','tech',
	'cooking','network','party','goog','markets',
	)

allowed_tags = ('b','blockquote','br','code','del','em','h1','h2','h3','h4','h5','h6','hr','i',
	'li','ol','p','pre','strong','sub','sup','table','tbody','th','thead','td','tr','ul',
	'marquee','a','span','ruby','rp','rt','spoiler','img','lite-youtube','video','audio','g','u','small')

allowed_styles = ['color', 'background-color', 'font-weight', 'text-align']

def allowed_attributes(tag, name, value):

	if name == 'style': return True

	if tag == 'marquee':
		if name in {'direction', 'behavior', 'scrollamount'}: return True
		if name in {'height', 'width'}:
			try: value = int(value.replace('px', ''))
			except: return False
			if 0 < value <= 250: return True

	if tag == 'a':
		if name == 'href' and '\\' not in value and 'xn--' not in value:
			return True
		if name == 'rel' and value == 'nofollow noopener': return True
		if name == 'target' and value == '_blank': return True

	if tag == 'img':
		if name in {'src','data-src'}: return is_safe_url(value)
		if name == 'loading' and value == 'lazy': return True
		if name == 'data-bs-toggle' and value == 'tooltip': return True
		if name in {'g','b','glow'} and not value: return True
		if name in {'alt','title'}: return True
		if name == 'class' and value == 'img': return True

	if tag == 'lite-youtube':
		if name == 'params' and value.startswith('autoplay=1&modestbranding=1'): return True
		if name == 'videoid': return True

	if tag == 'video':
		if name == 'controls' and value == '': return True
		if name == 'preload' and value == 'none': return True
		if name == 'src': return is_safe_url(value)

	if tag == 'audio':
		if name == 'src': return is_safe_url(value)
		if name == 'controls' and value == '': return True
		if name == 'preload' and value == 'none': return True

	if tag == 'p':
		if name == 'class' and value in {'mb-0','resizable','text-center'}: return True

	if tag == 'span':
		if name == 'data-bs-toggle' and value == 'tooltip': return True
		if name == 'title': return True
		if name == 'alt': return True

	if tag == 'table':
		if name == 'class' and value == 'table': return True

	return False

def build_url_re(tlds, protocols):
	"""Builds the url regex used by linkifier

	If you want a different set of tlds or allowed protocols, pass those in
	and stomp on the existing ``url_re``::

		from bleach import linkifier

		my_url_re = linkifier.build_url_re(my_tlds_list, my_protocols)

		linker = LinkifyFilter(url_re=my_url_re)

	"""
	return re.compile(
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
		re.VERBOSE | re.UNICODE,
	)

url_re = build_url_re(tlds=TLDS, protocols=['http', 'https'])

def create_comment_duplicated(text_html):
	new_comment = Comment(author_id=AUTOJANNY_ID,
							parent_post=None,
							body_html=text_html,
							distinguish_level=6,
							is_bot=True)
	g.db.add(new_comment)
	g.db.flush()

	new_comment.top_comment_id = new_comment.id

	return new_comment.id

def send_repeatable_notification_duplicated(uid, text):

	if uid in BOT_IDs: return

	text_html = sanitize(text)

	existing_comments = g.db.query(Comment.id).filter_by(author_id=AUTOJANNY_ID, parent_post=None, body_html=text_html, is_bot=True).order_by(Comment.id).all()

	for c in existing_comments:
		existing_notif = g.db.query(Notification.user_id).filter_by(user_id=uid, comment_id=c.id).one_or_none()
		if not existing_notif:
			notif = Notification(comment_id=c.id, user_id=uid)
			g.db.add(notif)
			return

	cid = create_comment_duplicated(text_html)
	notif = Notification(comment_id=cid, user_id=uid)
	g.db.add(notif)


def execute_blackjack(v, target, body, kind):
	if not blackjack or not body: return False

	execute = False
	for x in blackjack.split(','):
		if all(i in body.lower() for i in x.split()):
			execute = True

	if not execute: return False

	v.shadowbanned = AUTOJANNY_ID

	ma = ModAction(
		kind="shadowban",
		user_id=AUTOJANNY_ID,
		target_user_id=v.id,
		_note='reason: "Blackjack"'
	)
	g.db.add(ma)

	v.ban_reason = "Blackjack"
	g.db.add(v)

	notified_ids = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS['BLACKJACK_NOTIFICATIONS'])]
	extra_info = kind

	if target:
		if kind == 'post':
			extra_info = target.permalink
		elif kind == 'report':
			extra_info = f"reports on {target.permalink}"
		elif kind in {'comment', 'message'}:
			for id in notified_ids:
				n = Notification(comment_id=target.id, user_id=id)
				g.db.add(n)

			extra_info = None

	if extra_info:
		for id in notified_ids:
			send_repeatable_notification_duplicated(id, f"Blackjack by @{v.username}: {extra_info}")
	return True

def render_emoji(html, regexp, golden, emojis_used, b=False):
	emojis = list(regexp.finditer(html))
	captured = set()

	for i in emojis:
		if i.group(0) in captured: continue
		captured.add(i.group(0))

		emoji = i.group(1).lower()
		attrs = ''
		if b: attrs += ' b'
		if golden and len(emojis) <= 20 and ('marsey' in emoji or emoji in marseys_const2):
			if random.random() < 0.0025: attrs += ' g'
			elif random.random() < 0.00125: attrs += ' glow'

		old = emoji
		emoji = emoji.replace('!','').replace('#','')
		if emoji == 'marseyrandom': emoji = random.choice(marseys_const2)

		emoji_partial_pat = '<img alt=":{0}:" loading="lazy" src="{1}"{2}>'
		emoji_partial = '<img alt=":{0}:" data-bs-toggle="tooltip" loading="lazy" src="{1}" title=":{0}:"{2}>'
		emoji_html = None

		if emoji.endswith('pat') and emoji != 'marseyunpettablepat':
			if path.isfile(f"files/assets/images/emojis/{emoji.replace('pat','')}.webp"):
				emoji_html = f'<span data-bs-toggle="tooltip" title=":{old}:"><img loading="lazy" src="/i/hand.webp">{emoji_partial_pat.format(old, f"/e/{emoji[:-3]}.webp", attrs)}</span>'
			elif emoji.startswith('@'):
				if u := get_user(emoji[1:-3], graceful=True):
					emoji_html = f'<span data-bs-toggle="tooltip" title=":{old}:"><img loading="lazy" src="/i/hand.webp">{emoji_partial_pat.format(old, f"/pp/{u.id}", attrs)}</span>'
		elif path.isfile(f'files/assets/images/emojis/{emoji}.webp'):
			emoji_html = emoji_partial.format(old, f'/e/{emoji}.webp', attrs)


		if emoji_html:
			emojis_used.add(emoji)
			html = re.sub(f'(?<!"){i.group(0)}(?![^<]*<\/(code|pre|a)>)', emoji_html, html)
	return html


def with_sigalrm_timeout(timeout: int):
	'Use SIGALRM to raise an exception if the function executes for longer than timeout seconds'

	# while trying to test this using time.sleep I discovered that gunicorn does in fact do some
	# async so if we timeout on that (or on a db op) then the process is crashed without returning
	# a proper 500 error. Oh well.
	def sig_handler(signum, frame):
		print("Timeout!", flush=True)
		raise Exception("Timeout")

	def inner(func):
		@functools.wraps(func)
		def wrapped(*args, **kwargs):
			signal.signal(signal.SIGALRM, sig_handler)
			signal.alarm(timeout)
			try:
				return func(*args, **kwargs)
			finally:
				signal.alarm(0)
		return wrapped
	return inner

def remove_cuniform(sanitized:Optional[str]) -> str:
	if not sanitized: return ""
	sanitized = sanitized.replace('\u200e','').replace('\u200b','').replace('\u202e','').replace("\ufeff", "")
	sanitized = sanitized.replace("𒐪","").replace("𒐫","").replace("﷽","")
	sanitized = sanitized.replace("\r\n", "\n")
	sanitized = sanitized.strip()
	return sanitized

def sanitize_raw_title(sanitized:Optional[str]) -> str:
	if not sanitized: return ""
	sanitized = sanitized.replace("\r","").replace("\n", "")
	sanitized = remove_cuniform(sanitized)
	return sanitized[:POST_TITLE_LENGTH_LIMIT]

def sanitize_raw_body(sanitized:Optional[str], is_post:bool) -> str:
	if not sanitized: return ""
	sanitized = html_comment_regex.sub('', sanitized)
	sanitized = remove_cuniform(sanitized)
	return sanitized[:POST_BODY_LENGTH_LIMIT(g.v) if is_post else COMMENT_BODY_LENGTH_LIMIT]


def sanitize_settings_text(sanitized:Optional[str], max_length:Optional[int]=None) -> str:
	if not sanitized: return ""
	sanitized = sanitized.replace('\u200e','').replace('\u200b','').replace("\ufeff", "").replace("\r", "").replace("\n","")
	sanitized = sanitized.strip()
	if max_length: sanitized = sanitized[:max_length]
	return sanitized


def handle_youtube_links(url):
	html = None
	params = parse_qs(urlparse(url).query, keep_blank_values=True)

	id = params.get('v')

	if not id: return None

	id = id[0]

	t = None
	split = id.split('?t=')
	if len(split) == 2:
		id = split[0]
		t = split[1]

	id = id.split('?')[0]

	if yt_id_regex.fullmatch(id):
		if not t:
			t = params.get('t', params.get('start', [0]))[0]
		if isinstance(t, str):
			t = t.replace('s','').replace('S','')
			split = t.split('m')
			if len(split) == 2:
				minutes = int(split[0])
				seconds = int(split[1])
				t = minutes*60 + seconds
		html = f'<lite-youtube videoid="{id}" params="autoplay=1&modestbranding=1'
		if t:
			html += f'&start={int(t)}'
		html += '"></lite-youtube>'
	return html

@with_sigalrm_timeout(10)
def sanitize(sanitized, golden=True, limit_pings=0, showmore=False, count_emojis=False, snappy=False, chat=False, blackjack=None):
	sanitized = sanitized.strip()
	if not sanitized: return ''

	if "style" in sanitized and "filter" in sanitized:
		if sanitized.count("blur(") + sanitized.count("drop-shadow(") > 5:
			abort(400, "Too many filters!")

	if blackjack and execute_blackjack(g.v, None, sanitized, blackjack):
		sanitized = 'g'

	sanitized = utm_regex.sub('', sanitized)
	sanitized = utm_regex2.sub('', sanitized)

	sanitized = normalize_url(sanitized)

	if '```' not in sanitized and '<pre>' not in sanitized:
		sanitized = linefeeds_regex.sub(r'\1\n\n\2', sanitized)

	sanitized = greentext_regex.sub(r'\1<g>\>\2</g>', sanitized)
	sanitized = image_sub_regex.sub(r'![](\1)', sanitized)
	sanitized = image_check_regex.sub(r'\1', sanitized)
	sanitized = link_fix_regex.sub(r'\1https://\2', sanitized)

	if FEATURES['MARKUP_COMMANDS']:
		sanitized = command_regex.sub(command_regex_matcher, sanitized)

	sanitized = numbered_list_regex.sub(r'\1\. ', sanitized)

	sanitized = strikethrough_regex.sub(r'\1<del>\2</del>', sanitized)

	sanitized = markdown(sanitized)

	# replacing zero width characters, overlines, fake colons
	sanitized = sanitized.replace('\u200e','').replace('\u200b','').replace("\ufeff", "").replace("\u033f","").replace("\u0589", ":")

	sanitized = reddit_regex.sub(r'\1<a href="https://old.reddit.com/\2" rel="nofollow noopener" target="_blank">/\2</a>', sanitized)
	sanitized = sub_regex.sub(r'\1<a href="/\2">/\2</a>', sanitized)

	v = getattr(g, 'v', None)

	names = set(m.group(1) for m in mention_regex.finditer(sanitized))
	if limit_pings and len(names) > limit_pings and not v.admin_level >= PERMS['POST_COMMENT_INFINITE_PINGS']: abort(406)
	users_list = get_users(names, graceful=True)
	users_dict = {}
	for u in users_list:
		users_dict[u.username.lower()] = u
		if u.original_username:
			users_dict[u.original_username.lower()] = u
		if u.prelock_username:
			users_dict[u.prelock_username.lower()] = u

	def replacer(m):
		u = users_dict.get(m.group(1).lower())
		if not u or (v and u.id in v.all_twoway_blocks):
			return m.group(0)
		return f'<a href="/id/{u.id}"><img loading="lazy" src="/pp/{u.id}">@{u.username}</a>'

	sanitized = mention_regex.sub(replacer, sanitized)

	if FEATURES['PING_GROUPS']:
		def group_replacer(m):
			name = m.group(1).lower()

			if name == 'everyone':
				return f'<a href="/users">!{name}</a>'
			elif g.db.get(Group, name):
				return f'<a href="/!{name}">!{name}</a>'
			else:
				return m.group(0)

		sanitized = group_mention_regex.sub(group_replacer, sanitized)


	soup = BeautifulSoup(sanitized, 'lxml')

	for tag in soup.find_all("img"):
		if tag.get("src") and not tag["src"].startswith('/pp/'):
			if not is_safe_url(tag["src"]):
				a = soup.new_tag("a", href=tag["src"], rel="nofollow noopener", target="_blank")
				a.string = tag["src"]
				tag.replace_with(a)
				continue

			tag["loading"] = "lazy"
			tag["data-src"] = tag["src"]
			tag["src"] = f"{SITE_FULL_IMAGES}/i/l.webp"
			tag['alt'] = tag["data-src"]
			tag['class'] = "img"

			if tag.parent.name != 'a':
				a = soup.new_tag("a", href=tag["data-src"])
				if not is_site_url(a["href"]):
					a["rel"] = "nofollow noopener"
					a["target"] = "_blank"
				tag = tag.replace_with(a)
				a.append(tag)

			tag["data-src"] = tag["data-src"]

	sanitized = str(soup).replace('<html><body>','').replace('</body></html>','').replace('/>','>')

	sanitized = spoiler_regex.sub(r'<spoiler>\1</spoiler>', sanitized)

	emojis_used = set()

	emojis = list(emoji_regex.finditer(sanitized))
	if len(emojis) > 20: golden = False

	captured = []
	for i in emojis:
		if i.group(0) in captured: continue
		captured.append(i.group(0))

		old = i.group(0)
		if 'marseylong1' in old or 'marseylong2' in old or 'marseylongcockandballs' in old or 'marseyllama1' in old or 'marseyllama2' in old:
			new = old.lower().replace(">", " class='mb-0'>")
		else: new = old.lower()

		new = render_emoji(new, emoji_regex2, golden, emojis_used, True)

		sanitized = sanitized.replace(old, new)

	emojis = list(emoji_regex2.finditer(sanitized))
	if len(emojis) > 20: golden = False

	sanitized = render_emoji(sanitized, emoji_regex2, golden, emojis_used)

	sanitized = sanitized.replace('&amp;','&')

	captured = []
	for i in youtube_regex.finditer(sanitized):
		if i.group(0) in captured: continue
		captured.append(i.group(0))

		html = handle_youtube_links(i.group(2))
		if html:
			sanitized = sanitized.replace(i.group(0), i.group(1) + html)

	sanitized = video_sub_regex.sub(r'<p class="resizable"><video controls preload="none" src="\1"></video></p>', sanitized)
	sanitized = audio_sub_regex.sub(r'<audio controls preload="none" src="\1"></audio>', sanitized)

	if count_emojis:
		for emoji in g.db.query(Emoji).filter(Emoji.submitter_id==None, Emoji.name.in_(emojis_used)).all():
			emoji.count += 1
			g.db.add(emoji)

	sanitized = sanitized.replace('<p></p>', '')

	if g.v and g.v.chud:
		allowed_css_properties = allowed_styles
	else:
		allowed_css_properties = allowed_styles + ["filter"]

	css_sanitizer = CSSSanitizer(allowed_css_properties=allowed_css_properties)
	sanitized = bleach.Cleaner(tags=allowed_tags,
								attributes=allowed_attributes,
								protocols=['http', 'https'],
								css_sanitizer=css_sanitizer,
								filters=[partial(LinkifyFilter, skip_tags=["pre"],
									parse_email=False, url_re=url_re)]
								).clean(sanitized)

	#doing this here cuz of the linkifyfilter right above it (therefore unifying all link processing logic)
	soup = BeautifulSoup(sanitized, 'lxml')

	links = soup.find_all("a")

	def error(error):
		if chat:
			return error, 403
		else:
			abort(403, error)

	if g.v and g.v.admin_level >= PERMS["IGNORE_DOMAIN_BAN"]:
		banned_domains = []
	else:
		if discord_username_regex.match(sanitized):
			return error("Stop grooming!")
		banned_domains = [x.domain for x in g.db.query(BannedDomain.domain).all()]

	for link in links:
		#remove empty links
		if not link.contents or not str(link.contents[0]).strip():
			link.extract()
			continue

		href = link.get("href")
		if not href: continue

		def unlinkfy():
			link.string = href
			del link["href"]

		#\ in href right after / makes most browsers ditch site hostname and allows for a host injection bypassing the check, see <a href="/\google.com">cool</a>
		if "\\" in href:
			unlinkfy()
			continue

		#don't allow something like this https://rdrama.net/post/78376/reminder-of-the-fact-that-our/2150032#context
		domain = tldextract.extract(href).registered_domain
		if domain and not allowed_domain_regex.fullmatch(domain):
			unlinkfy()
			continue

		#check for banned domain
		combined = (domain + urlparse(href).path).lower()
		if any((combined.startswith(x) for x in banned_domains)):
			unlinkfy()
			continue

		#don't allow something like this [@Aevann2](https://iplogger.org/1fRKk7)
		if str(link.string).startswith('@') and not href.startswith('/'):
			unlinkfy()
			continue

		#don't allow something like this [!jannies](https://iplogger.org/1fRKk7)
		if str(link.string).startswith('!') and not href.startswith('/'):
			unlinkfy()
			continue

		#don't allow something like this [https://rԁrama.net/leaderboard](https://iplogger.org/1fRKk7)
		if not snappy:
			string_domain = tldextract.extract(str(link.string)).registered_domain
			if string_domain and string_domain != tldextract.extract(href).registered_domain:
				link.string = href

		#insert target="_blank" and ref="nofollower noopener" for external link
		if not href.startswith('/') and not href.startswith(f'{SITE_FULL}/'):
			link["target"] = "_blank"
			link["rel"] = "nofollow noopener"


	sanitized = str(soup).replace('<html><body>','').replace('</body></html>','').replace('/>','>')

	if '<pre>' not in sanitized and blackjack != "rules":
		sanitized = sanitized.replace('\n','')

	if showmore:
		# Insert a show more button if the text is too long or has too many paragraphs
		CHARLIMIT = 3000
		pos = 0
		for _ in range(20):
			pos = sanitized.find('</p>', pos + 4)
			if pos < 0:
				break
		if (pos < 0 and len(sanitized) > CHARLIMIT) or pos > CHARLIMIT:
			pos = CHARLIMIT - 500
		if pos >= 0:
			sanitized = (sanitized[:pos] + showmore_regex.sub(r'\1<p><button class="showmore">SHOW MORE</button></p><d class="d-none">\2</d>', sanitized[pos:], count=1))

	return sanitized.strip()

def allowed_attributes_emojis(tag, name, value):
	if tag == 'img':
		if name == 'src' and value.startswith('/') and '\\' not in value: return True
		if name == 'loading' and value == 'lazy': return True
		if name == 'data-bs-toggle' and value == 'tooltip': return True
		if name in {'g','glow'} and not value: return True
		if name in {'alt','title'}: return True

	if tag == 'span':
		if name == 'data-bs-toggle' and value == 'tooltip': return True
		if name == 'title': return True
		if name == 'alt': return True
	return False


@with_sigalrm_timeout(1)
def filter_emojis_only(title, golden=True, count_emojis=False, graceful=False, strip=True):

	title = title.replace("\n", "").replace("\r", "").replace("\t", "").replace('<','&lt;').replace('>','&gt;')

	title = remove_cuniform(title)

	emojis_used = set()

	title = render_emoji(title, emoji_regex3, golden, emojis_used)

	if count_emojis:
		for emoji in g.db.query(Emoji).filter(Emoji.submitter_id==None, Emoji.name.in_(emojis_used)).all():
			emoji.count += 1
			g.db.add(emoji)

	title = strikethrough_regex.sub(r'\1<del>\2</del>', title)

	title = bleach.clean(title, tags=['img','del','span'], attributes=allowed_attributes_emojis, protocols=['http','https']).replace('\n','')

	if strip:
		title = title.strip()

	if len(title) > POST_TITLE_HTML_LENGTH_LIMIT and not graceful: abort(400)
	else: return title

def normalize_url(url):
	url = reddit_domain_regex.sub(r'\1https://old.reddit.com/\3/', url)

	url = url.replace("https://youtu.be/", "https://youtube.com/watch?v=") \
			 .replace("https://music.youtube.com/watch?v=", "https://youtube.com/watch?v=") \
			 .replace("https://www.youtube.com", "https://youtube.com") \
			 .replace("https://m.youtube.com", "https://youtube.com") \
			 .replace("https://youtube.com/shorts/", "https://youtube.com/watch?v=") \
			 .replace("https://youtube.com/v/", "https://youtube.com/watch?v=") \
			 .replace("https://mobile.twitter.com", "https://twitter.com") \
			 .replace("https://m.facebook.com", "https://facebook.com") \
			 .replace("https://m.wikipedia.org", "https://wikipedia.org") \
			 .replace("https://www.twitter.com", "https://twitter.com") \
			 .replace("https://www.instagram.com", "https://instagram.com") \
			 .replace("https://www.tiktok.com", "https://tiktok.com") \
			 .replace("https://www.streamable.com", "https://streamable.com") \
			 .replace("https://streamable.com/", "https://streamable.com/e/") \
			 .replace("https://streamable.com/e/e/", "https://streamable.com/e/") \
			 .replace("https://search.marsey.cat/#", "https://camas.unddit.com/#") \
			 .replace("https://imgur.com/", "https://i.imgur.com/") \
			 .replace("https://nitter.net/", "https://twitter.com/") \
			 .replace("https://nitter.42l.fr/", "https://twitter.com/") \
			 .replace("https://nitter.lacontrevoie.fr/", "https://twitter.com/") \
			 .replace("/giphy.gif", "/giphy.webp") \

	url = imgur_regex.sub(r'\1_d.webp?maxwidth=9999&fidelity=grand', url)
	url = giphy_regex.sub(r'\1.webp', url)
	url = unquote(url)

	return url

def validate_css(css):
	if '@import' in css:
		return False, "CSS @import statements are not allowed!"

	if '/*' in css:
		return False, "CSS comments are not allowed!"

	for i in css_url_regex.finditer(css):
		url = i.group(1)
		if not is_safe_url(url):
			domain = tldextract.extract(url).registered_domain
			return False, f"The domain '{domain}' is not allowed, please use one of these domains\n\n{approved_embed_hosts}."

	return True, ""

def torture_chud(string, username):
	if not string: return string
	for k, l in CHUD_REPLACEMENTS.items():
		string = string.replace(k, l)
	string = torture_regex.sub(rf'\1@{username}\3', string)
	string = torture_regex2.sub(rf'\1@{username} is\3', string)
	string = torture_regex3.sub(rf"\1@{username}'s\3", string)
	return string

def torture_queen(string, key):
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
	string = normal_punctuation_regex.sub("", string)
	string = more_than_one_comma_regex.sub(",", string)
	if string[-5:] == ', and':
		string = string[:-5]
    
	random.seed(key)
	if random.random() < PHRASE_CHANCE:
		girl_phrase = random.choice(GIRL_PHRASES)
		string = girl_phrase.replace("$", string)
	string = initial + string
	return string

def torture_object(obj, torture_method):
	#torture body_html
	if obj.body_html and '<p>&amp;&amp;' not in obj.body_html and '<p>$$' not in obj.body_html and '<p>##' not in obj.body_html:
		soup = BeautifulSoup(obj.body_html, 'lxml')
		tags = soup.html.body.find_all(lambda tag: tag.name not in {'blockquote','codeblock','pre'} and tag.string, recursive=False)
		i = 0
		for tag in tags:
			i+=1
			key = obj.id+i
			tag.string.replace_with(torture_method(tag.string, key))
		obj.body_html = str(soup).replace('<html><body>','').replace('</body></html>','')

	#torture title_html and check for chud_phrase in plain title and leave if it's there
	if isinstance(obj, Post):
		obj.title_html = obj.title_html

def complies_with_chud(obj):
	#check for cases where u should leave
	if not (obj.author.chud or obj.author.queen): return True
	if obj.author.marseyawarded: return True
	if isinstance(obj, Post):
		if obj.id in ADMIGGER_THREADS: return True
		if obj.sub == "chudrama": return True
	elif obj.parent_post:
		if obj.parent_post in ADMIGGER_THREADS: return True
		if obj.post.sub == "chudrama": return True

	if obj.author.chud:
		if not obj.chudded: return True

		#perserve old body_html to be used in checking for chud phrase
		old_body_html = obj.body_html

		# TODO: Replace this code to make it more generic
		#torture body_html
		if obj.body_html and '<p>&amp;&amp;' not in obj.body_html and '<p>$$' not in obj.body_html and '<p>##' not in obj.body_html:
			soup = BeautifulSoup(obj.body_html, 'lxml')
			tags = soup.html.body.find_all(lambda tag: tag.name not in {'blockquote','codeblock','pre'} and tag.string, recursive=False)
			for tag in tags:
				tag.string.replace_with(torture_chud(tag.string, obj.author.username))
			obj.body_html = str(soup).replace('<html><body>','').replace('</body></html>','')

		#torture title_html and check for chud_phrase in plain title and leave if it's there
		if isinstance(obj, Post):
			obj.title_html = torture_chud(obj.title_html, obj.author.username)
			if obj.author.chud_phrase in obj.title.lower():
				return True

		#check for chud_phrase in body_html
		if old_body_html:
			excluded_tags = {'del','sub','sup','marquee','spoiler','lite-youtube','video','audio'}
			soup = BeautifulSoup(old_body_html, 'lxml')
			tags = soup.html.body.find_all(lambda tag: tag.name not in excluded_tags and not tag.attrs, recursive=False)
			for tag in tags:
				for text in tag.find_all(text=True, recursive=False):
					if obj.author.chud_phrase in text.lower():
						return True

		return False
	elif obj.author.queen:
		torture_object(obj, torture_queen)
		return True
