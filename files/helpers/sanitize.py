import functools
import random
import re
import signal
from functools import partial
from os import path, listdir
from urllib.parse import parse_qs, urlparse, unquote, ParseResult, urlencode, urlunparse
import time
import requests

from sqlalchemy.sql import func

import bleach
from bleach.css_sanitizer import CSSSanitizer
from bleach.linkifier import LinkifyFilter
from bs4 import BeautifulSoup
from mistletoe import markdown

from files.classes.domains import BannedDomain
from files.classes.mod_logs import ModAction
from files.classes.notifications import Notification
from files.classes.group import Group
from files.classes.follows import Follow

from files.helpers.config.const import *
from files.helpers.const_stateful import *
from files.helpers.regex import *
from files.helpers.get import *
from files.helpers.marsify import *
from files.helpers.owoify import *
from files.helpers.sharpen import *
from files.helpers.queenify import *


allowed_tags = ('a','audio','b','big','blink','blockquote','br','center','code','del','details','em','g','h1','h2','h3','h4','h5','h6','hr','i','img','li','lite-youtube','marquee','ol','p','pre','rp','rt','ruby','small','span','spoiler','strike','strong','sub','summary','sup','table','tbody','td','th','thead','tr','u','ul','video')

allowed_styles = ['background-color', 'color', 'filter', 'font-weight', 'text-align', 'transform']

def allowed_attributes(tag, name, value):

	if name == 'style':
		return True

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
		if name in {'g','b','glow','party'} and not value: return True
		if name in {'alt','title'}: return True
		if name == 'class' and value == 'img': return True
		if name == 'data-user-submitted' and not value: return True

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
		if name == 'class' and value in {'mb-0','resizable','yt','text-center'}: return True

	if tag == 'span':
		if name == 'data-bs-toggle' and value == 'tooltip': return True
		if name == 'title': return True
		if name == 'alt': return True
		if name == 'cide' and not value: return True
		if name == 'bounce' and not value: return True

	if tag == 'table':
		if name == 'class' and value == 'table': return True

	return False

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
		_note=f'reason: "Blackjack: {kind}"'
	)
	g.db.add(ma)

	v.ban_reason = f"Blackjack: {kind}"
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

def find_all_emoji_endings(emoji):
	endings = []

	is_non_ending_found = False
	while not is_non_ending_found:
		if emoji.endswith('pat'):
			if 'pat' in endings:
				is_non_ending_found = True
				continue
			endings.append('pat')
			emoji = emoji[:-3]
			continue

		if emoji.endswith('talking'):
			if 'talking' in endings:
				is_non_ending_found = True
				continue
			endings.append('talking')
			emoji = emoji[:-7]
			continue

		if emoji.endswith('genocide'):
			if 'genocide' in endings:
				is_non_ending_found = True
				continue
			endings.append('genocide')
			emoji = emoji[:-8]
			continue

		if emoji.endswith('love'):
			if 'love' in endings:
				is_non_ending_found = True
				continue
			endings.append('love')
			emoji = emoji[:-4]
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


def render_emoji(html, regexp, golden, emojis_used, b=False, is_title=False):
	emojis = list(regexp.finditer(html))
	captured = set()

	for i in emojis:
		if i.group(0) in captured: continue
		captured.add(i.group(0))

		emoji = i.group(1).lower()
		attrs = ''
		if b: attrs += ' b'
		if is_title: emoji = emoji.replace('#','')
		if golden and len(emojis) <= 20 and ('marsey' in emoji or emoji in MARSEYS_CONST2):
			if random.random() < 0.005:
				attrs += ' ' + random.choice(('g', 'glow', 'party'))

		old = emoji
		emoji = emoji.replace('!','').replace('#','')

		emoji_partial_pat = '<img alt=":{0}:" loading="lazy" src="{1}"{2}>'
		emoji_partial = '<img alt=":{0}:" data-bs-toggle="tooltip" loading="lazy" src="{1}" title=":{0}:"{2}>'
		emoji_html = None

		ending_modifiers, emoji = find_all_emoji_endings(emoji)

		is_talking = 'talking' in ending_modifiers
		is_patted = 'pat' in ending_modifiers
		is_talking_first = ending_modifiers.index('pat') > ending_modifiers.index('talking') if is_talking and is_patted else False
		is_loved = 'love' in ending_modifiers
		is_genocided = 'genocide' in ending_modifiers
		is_user = emoji.startswith('@')

		end_modifier_length = 3 if is_patted else 0
		end_modifier_length = end_modifier_length + 7 if is_talking else end_modifier_length

		hand_html = f'<img loading="lazy" src="{SITE_FULL_IMAGES}/i/hand.webp">' if is_patted and emoji != 'marseyunpettable' else ''
		talking_html = f'<img loading="lazy" src="{SITE_FULL_IMAGES}/i/talking.webp">' if is_talking else ''
		loved_html = f'<img loading="lazy" src="{SITE_FULL_IMAGES}/i/love-foreground.webp" alt=":{old}:" {attrs}><img loading="lazy" alt=":{old}:" src="{SITE_FULL_IMAGES}/i/love-background.webp" {attrs}>'
		genocide_attr = ' cide' if is_genocided else ''

		modifier_html = ''
		if (is_talking and is_patted):
			modifier_html = f'{talking_html}{hand_html}' if is_talking_first else f'{hand_html}{talking_html}'
		elif (is_patted):
			modifier_html = hand_html
		elif (is_talking):
			modifier_html = talking_html

		if(is_loved):
			modifier_html = f'{modifier_html}{loved_html}'

		if (is_patted and emoji != 'marseyunpettable') or is_talking or is_genocided or is_loved:
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


def with_sigalrm_timeout(timeout):
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

def remove_cuniform(sanitized):
	if not sanitized: return ""
	sanitized = sanitized.replace('\u200e','').replace('\u200b','').replace('\u202e','').replace("\ufeff", "").replace("\u033f","").replace("\u0589", ":")
	sanitized = sanitized.replace("𒐪","").replace("𒐫","").replace("﷽","")
	sanitized = sanitized.replace("\r\n", "\n")
	sanitized = sanitized.replace("’", "'")
	return sanitized.strip()

def get_youtube_id_and_t(url):
	params = parse_qs(urlparse(url).query, keep_blank_values=True)

	id = params.get('v')

	if not id: return (None, None)

	id = id[0]

	t = None
	split = id.split('?t=')
	if len(split) == 2:
		id = split[0]
		t = split[1]

	id = id.split('?')[0]

	return (id, t)

def handle_youtube_links(url):
	url = url.replace('&amp;','&')
	params = parse_qs(urlparse(url).query, keep_blank_values=True)
	html = None
	id, t = get_youtube_id_and_t(url)
	if not id: return None
	if yt_id_regex.fullmatch(id):
		if not t:
			t = params.get('t', params.get('start', [0]))[0]
		if isinstance(t, str):
			t = t.replace('s','').replace('S','')
			split = t.split('m')
			if len(split) == 2:
				minutes = int(split[0])
				if split[1]: seconds = int(split[1])
				else: seconds = 0
				t = minutes*60 + seconds
		html = f'<lite-youtube videoid="{id}" params="autoplay=1&modestbranding=1'
		if t:
			html += f'&start={int(t)}'
		html += '"></lite-youtube>'
	return html

@with_sigalrm_timeout(10)
def sanitize(sanitized, golden=True, limit_pings=0, showmore=False, count_emojis=False, snappy=False, chat=False, blackjack=None, commenters_ping_post_id=None, obj=None, author=None):
	def error(error):
		if chat:
			return error, 403
		else:
			abort(403, error)

	sanitized = html_comment_regex.sub('', sanitized)
	sanitized = remove_cuniform(sanitized)

	if not sanitized: return ''

	v = getattr(g, 'v', None)

	if blackjack and execute_blackjack(v, None, sanitized, blackjack):
		return '<p>g</p>'

	if obj and not obj.is_effortpost:
		if author.owoify:
			sanitized = owoify(sanitized, author.chud_phrase)
		if author.marsify:
			sanitized = marsify(sanitized, author.chud_phrase)

	if obj and obj.sharpened:
		sanitized = sharpen(sanitized, author.chud_phrase)

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

	sanitized = sanitized.replace('_', '▔')
	sanitized = markdown(sanitized)
	sanitized = sanitized.replace('▔', '_').replace('%E2%96%94', '_')

	if obj and obj.queened:
		sanitized = queenify_html(sanitized)

	sanitized = sanitized.replace('<a href="/%21', '<a href="/!')

	sanitized = reddit_mention_regex.sub(r'<a href="https://old.reddit.com/\1" rel="nofollow noopener" target="_blank">/\1</a>', sanitized)
	sanitized = hole_mention_regex.sub(r'<a href="/\1">/\1</a>', sanitized)

	names = set(m.group(1) for m in mention_regex.finditer(sanitized))

	if limit_pings and len(names) > limit_pings and v.admin_level < PERMS['POST_COMMENT_INFINITE_PINGS']:
		error("Max ping limit is 5 for comments and 50 for posts!")

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
		if not u or (v and u.id in v.all_twoway_blocks) or (v and u.has_muted(v)):
			return m.group(0)
		return f'<a href="/id/{u.id}"><img loading="lazy" src="/pp/{u.id}">@{u.username}</a>'

	sanitized = mention_regex.sub(replacer, sanitized)

	if FEATURES['PING_GROUPS']:
		def group_replacer(m):
			name = m.group(1)

			if name == 'everyone':
				return f'<a href="/users">!{name}</a>'
			elif name == 'jannies':
				return f'<a href="/admins">!{name}</a>'
			elif name == 'holejannies' and get_obj_hole(obj):
				return f'<a href="/h/{obj.hole}/mods">!{name}</a>'
			elif name == 'commenters' and commenters_ping_post_id:
				return f'<a href="/!commenters/{commenters_ping_post_id}/{int(time.time())}">!{name}</a>'
			elif name == 'followers':
				return f'<a href="/id/{v.id}/followers">!{name}</a>'
			elif g.db.get(Group, name.lower()):
				return f'<a href="/!{name.lower()}">!{name}</a>'
			else:
				return m.group(0)

		sanitized = group_mention_regex.sub(group_replacer, sanitized)


	soup = BeautifulSoup(sanitized, 'lxml')

	for tag in soup.find_all("img"):
		if tag.get("src") and not tag["src"].startswith('/pp/') and not (snappy and tag["src"].startswith(f'{SITE_FULL_IMAGES}/e/')):
			if not is_safe_url(tag["src"]):
				a = soup.new_tag("a", href=tag["src"], rel="nofollow noopener", target="_blank")
				a.string = tag["src"]
				tag.replace_with(a)
				continue

			del tag["g"]
			del tag["glow"]
			del tag["party"]

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
		tag["data-user-submitted"] = ""

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

	sanitized = video_sub_regex.sub(r'<p class="resizable"><video controls preload="none" src="\1"></video></p>', sanitized)
	sanitized = audio_sub_regex.sub(r'<audio controls preload="none" src="\1"></audio>', sanitized)

	if count_emojis:
		for emoji in g.db.query(Emoji).filter(Emoji.submitter_id==None, Emoji.name.in_(emojis_used)):
			emoji.count += 1
			g.db.add(emoji)

	if obj:
		for emoji in emojis_used:
			if emoji in OVER_18_EMOJIS:
				obj.nsfw = True
				break

	sanitized = sanitized.replace('<p></p>', '')

	allowed_css_properties = allowed_styles.copy()
	if v and v.chud:
		allowed_css_properties.remove('filter')

	css_sanitizer = CSSSanitizer(allowed_css_properties=allowed_css_properties)
	sanitized = bleach.Cleaner(tags=allowed_tags,
								attributes=allowed_attributes,
								protocols=['http', 'https'],
								css_sanitizer=css_sanitizer,
								filters=[partial(LinkifyFilter, skip_tags=["pre"],
									parse_email=False, url_re=sanitize_url_regex)]
								).clean(sanitized)

	#doing this here cuz of the linkifyfilter right above it (therefore unifying all link processing logic)
	soup = BeautifulSoup(sanitized, 'lxml')

	has_transform = bool(soup.select('[style*=transform i]'))

	links = soup.find_all("a")

	if v and v.admin_level >= PERMS["IGNORE_DOMAIN_BAN"]:
		banned_domains = []
	else:
		banned_domains = [x.domain for x in g.db.query(BannedDomain.domain)]

	for link in links:
		#remove empty links
		if not link.contents or not str(link.contents[0]).strip():
			link.extract()
			continue

		href = link.get("href")
		if not href: continue

		link["href"] = normalize_url(href)
		if link.string == href:
			link.string = link["href"]
		href = link["href"]

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

		if has_transform:
			del link["href"]

	sanitized = str(soup).replace('<html><body>','').replace('</body></html>','').replace('/>','>')

	captured = []
	for i in youtube_regex.finditer(sanitized):
		if i.group(0) in captured: continue
		captured.append(i.group(0))

		html = handle_youtube_links(i.group(1))
		if html:
			if not chat:
				html = f'<p class="resizable yt">{html}</p>'
			sanitized = sanitized.replace(i.group(0), html)

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

	if "style" in sanitized and "filter" in sanitized:
		if sanitized.count("blur(") + sanitized.count("drop-shadow(") > 5:
			error("Max 5 usages of 'blur' and 'drop-shadow'!")

	return sanitized.strip()

def allowed_attributes_emojis(tag, name, value):
	if tag == 'img':
		if name == 'src':
			if '\\' in value: return False
			if value.startswith('/') : return True
			if value.startswith(f'{SITE_FULL_IMAGES}/') : return True
		if name == 'loading' and value == 'lazy': return True
		if name == 'data-bs-toggle' and value == 'tooltip': return True
		if name in {'g','glow','party'} and not value: return True
		if name in {'alt','title'}: return True

	if tag == 'span':
		if name == 'data-bs-toggle' and value == 'tooltip': return True
		if name == 'title': return True
		if name == 'alt': return True
		if name == 'cide' and not value: return True
	return False


@with_sigalrm_timeout(2)
def filter_emojis_only(title, golden=True, count_emojis=False, obj=None, author=None):

	title = title.replace("\n", "").replace("\r", "").replace("\t", "").replace('<','&lt;').replace('>','&gt;')

	title = remove_cuniform(title)

	if obj and not obj.is_effortpost:
		if author.owoify:
			title = owoify(title, author.chud_phrase)
		if author.marsify:
			title = marsify(title, author.chud_phrase)

	if obj and obj.sharpened:
		title = sharpen(title, author.chud_phrase)

	emojis_used = set()

	title = render_emoji(title, emoji_regex2, golden, emojis_used, is_title=True)

	if count_emojis:
		for emoji in g.db.query(Emoji).filter(Emoji.submitter_id==None, Emoji.name.in_(emojis_used)):
			emoji.count += 1
			g.db.add(emoji)

	if obj:
		for emoji in emojis_used:
			if emoji in OVER_18_EMOJIS:
				obj.nsfw = True
				break

	title = strikethrough_regex.sub(r'\1<del>\2</del>', title)

	title = bleach.clean(title, tags=['img','del','span'], attributes=allowed_attributes_emojis, protocols=['http','https']).replace('\n','')

	if len(title) > POST_TITLE_HTML_LENGTH_LIMIT:
		abort(400, "Rendered title is too big!")

	title = title.strip()

	return title

def is_whitelisted(domain, k):
	if domain.endswith('pullpush.io'):
		return True
	if 'sort' in k.lower() or 'query' in k.lower():
		return True
	if k in {'_x_tr_hl','_x_tr_pto','_x_tr_sl','_x_tr_tl','abstract_id','after','article','bill_id','c','clip','commentID','comments','context','count','f','fbid','format','forum_id','i','ID','id','lb','list','oldid','p','page','post_id','postid','q','run','scrollToComments','search','sl','sp','story_fbid','tab','term','text','thread_id','threadid','ticket_form_id','time_continue','title','title_no','tl','token','topic','type','tz1','tz2','u','udca','url','v','vid','viewkey'}:
		return True
	if k == 't' and domain != 'twitter.com':
		return True
	if k == 'oid' and domain != 'quora.com':
		return True
	return False


def normalize_url(url):
	url = unquote(url)

	url = url.replace("reddit.com/user/", "reddit.com/u/")

	url = reddit_domain_regex.sub(r'\1https://old.reddit.com/\5', url)

	url = url.replace("https://music.youtube.com/watch?v=", "https://youtube.com/watch?v=") \
			 .replace("https://www.youtube.com", "https://youtube.com") \
			 .replace("https://m.youtube.com", "https://youtube.com") \
			 .replace("https://youtube.com/shorts/", "https://youtube.com/watch?v=") \
			 .replace("https://youtube.com/live/", "https://youtube.com/watch?v=") \
			 .replace("https://youtube.com/v/", "https://youtube.com/watch?v=") \
			 .replace("https://mobile.twitter.com", "https://twitter.com") \
			 .replace("https://x.com", "https://twitter.com") \
			 .replace("https://www.twitter.com", "https://twitter.com") \
			 .replace("https://nitter.net/", "https://twitter.com/") \
			 .replace("https://nitter.42l.fr/", "https://twitter.com/") \
			 .replace("https://nitter.net/", "https://twitter.com/") \
			 .replace("https://m.facebook.com", "https://facebook.com") \
			 .replace("https://en.m.wikipedia.org", "https://en.wikipedia.org") \
			 .replace("https://www.instagram.com", "https://instagram.com") \
			 .replace("https://www.tiktok.com", "https://tiktok.com") \
			 .replace("https://imgur.com/", "https://i.imgur.com/") \
			 .replace("/giphy.gif", "/giphy.webp") \
			 .replace('https://www.google.com/amp/s/', 'https://') \
			 .replace('https://amp.', 'https://') \
			 .replace('https://cnn.com/cnn/', 'https://edition.cnn.com/') \
			 .replace('/amp/', '/') \
			 .replace('https://letmegooglethat.com/?q=', 'https://google.com/search?q=') \
			 .replace('https://lmgtfy.app/?q=', 'https://google.com/search?q=') \
			 .replace(DONATE_LINK, f'{SITE_FULL}/donate') \

	if url.endswith('.amp'):
		url = url.split('.amp')[0]

	url = giphy_regex.sub(r'\1.webp', url)

	if not url.startswith('/') and not url.startswith('https://rdrama.net') and not url.startswith('https://watchpeopledie.tv'):
		try: parsed_url = urlparse(url)
		except:
			print(url, flush=True)
			abort(500)

		netloc = parsed_url.netloc
		path = parsed_url.path.rstrip('/')
		qd = parse_qs(parsed_url.query, keep_blank_values=True)

		filtered = {}

		if netloc == 'youtu.be':
			filtered['v'] = path.lstrip('/')
			netloc = 'youtube.com'
			path = '/watch'

		filtered |= {k: val for k, val in qd.items() if not val[0] or is_whitelisted(netloc, k)}

		if netloc == 'old.reddit.com' and reddit_comment_link_regex.fullmatch(url):
			filtered['context'] = 8

		new_url = ParseResult(scheme="https",
							netloc=netloc,
							path=path,
							params=parsed_url.params,
							query=urlencode(filtered, doseq=True),
							fragment=parsed_url.fragment)
		url = urlunparse(new_url)

	url = url.rstrip('/')

	url = imgur_regex.sub(r'\1_d.webp?maxwidth=9999&fidelity=grand', url)

	return url

def normalize_url_gevent(url):
	url = requests.get(url, headers=HEADERS, timeout=2).url
	return normalize_url(url)

def validate_css(css):
	if '@import' in css:
		return False, "CSS @import statements are not allowed!"

	if '/*' in css:
		return False, "CSS comments are not allowed!"

	for i in css_url_regex.finditer(css):
		url = i.group(1)
		if not is_safe_url(url):
			domain = tldextract.extract(url).registered_domain
			return False, f"The domain '{domain}' is not allowed here!"

	return True, ""

def torture_chud(string, username):
	if not string: return string
	for k, l in CHUD_REPLACEMENTS.items():
		string = string.replace(k, l)
	string = torture_regex.sub(rf'\1@{username}\3', string)
	string = torture_regex2.sub(rf'\1@{username} is\3', string)
	string = torture_regex3.sub(rf"\1@{username}'s\3", string)
	return string

def complies_with_chud(obj):
	#check for cases where u should leave
	if not obj.chudded: return True
	if obj.author.hieroglyphs: return True

	if isinstance(obj, Post):
		if obj.id in ADMIGGER_THREADS: return True
		if obj.hole == "chudrama": return True
	elif obj.parent_post:
		if obj.parent_post in ADMIGGER_THREADS: return True
		if obj.post.hole == "chudrama": return True

	#perserve old body_html to be used in checking for chud phrase
	old_body_html = obj.body_html

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
		if not obj.author.chud or obj.author.chud_phrase in obj.title.lower():
			return True

	#check for chud_phrase in body_html
	if old_body_html:
		excluded_tags = {'del','sub','sup','marquee','spoiler','lite-youtube','video','audio'}
		soup = BeautifulSoup(old_body_html, 'lxml')
		tags = soup.html.body.find_all(lambda tag: tag.name not in excluded_tags and not tag.attrs, recursive=False)
		for tag in tags:
			for text in tag.find_all(text=True, recursive=False):
				if not obj.author.chud or obj.author.chud_phrase in text.lower():
					return True

	return False
