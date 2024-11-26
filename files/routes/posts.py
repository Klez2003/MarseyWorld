import os
import time
import html
from io import BytesIO
from os import path
from shutil import copyfile
from sys import stdout
from urllib.parse import urlparse
import random

import gevent
import requests
from PIL import Image

from files.__main__ import app, cache, limiter
from files.classes import *
from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.regex import *
from files.helpers.sanitize import *
from files.helpers.settings import get_setting
from files.helpers.slots import *
from files.helpers.sorting_and_time import *
from files.helpers.can_see import *
from files.routes.routehelpers import execute_shadowban_viewers_and_voters
from files.routes.wrappers import *

from .front import frontlist
from .users import userpagelisting

from files.__main__ import app, limiter

def _make_post_url():
	url = request.values.get("url", "").replace('\x00', '').strip()
	if url == '': return None
	if '\\' in url:
		stop(400)
	if len(url) > 2048:
		stop(400, "There's a 2048 character limit for URLs!")
	return normalize_url(url)

def _check_domain_ban_and_make_post_embed(url, v):
	if not url:
		return None

	embed = None
	domain = tldextract.extract(url).registered_domain

	if v.admin_level < PERMS["IGNORE_DOMAIN_BAN"]:
		combined = (domain + urlparse(url).path).lower()
		for x in g.db.query(BannedDomain):
			if combined.startswith(x.domain):
				stop(400, f'Remove the banned link "{x.domain}" and try again!\nReason for link ban: "{x.reason}"')

	if domain == "x.com" and '/status/' in url:
		try:
			embed = requests.get("https://publish.x.com/oembed", params={"url":url, "omit_script":"t", "dnt":"t"}, headers=HEADERS, timeout=5).json()["html"]
			embed = embed.replace('<a href', '<a rel="nofollow noopener" href')
		except: pass
	elif url.startswith("https://bsky.app/profile/") and '/post/' in url:
		try:
			embed = requests.get("https://embed.bsky.app/oembed", params={"url":url}, headers=HEADERS, timeout=5, proxies=proxies).json()["html"]
			embed = embed.replace('<a href', '<a rel="nofollow noopener" href')
			embed = embed.split('<script async src="https://embed.bsky.app/static/embed.js" charset="utf-8"></script>')[0]
		except: pass
	elif url.startswith('https://youtube.com/watch?'):
		embed = handle_youtube_links(url)
	elif SITE in domain and "/post/" in url and "context" not in url and url.count('/') < 6:
		id = url.split("/post/")[1]
		if "/" in id: id = id.split("/")[0]
		embed = str(int(id))

	if embed and len(embed) > 1500: embed = None
	if embed: embed = embed.strip()
	return embed

def _process_post_attachement(p, v):
	file = request.files['file-url']

	if file.content_type.startswith('image/'):
		name = f'/images/{time.time()}'.replace('.','') + '.webp'
		file.save(name)
		p.url = process_image(name, v)

		name2 = name.replace('.webp', 'r.webp')
		copyfile(name, name2)
		p.thumburl = process_image(name2, v, resize=199)
	elif file.content_type.startswith('video/'):
		p.url, p.posterurl, name = process_video(file, v, post=p)
		if p.posterurl:
			name2 = name.replace('.webp', 'r.webp')
			copyfile(name, name2)
			p.thumburl = process_image(name2, v, resize=199)
	elif file.content_type.startswith('audio/'):
		p.url = process_audio(file, v)
	else:
		stop(415)

def _register_duplicate_media_usage_and_get_poster(p):
	filename = '/videos' + p.url.split(SITE_FULL_VIDEOS)[1]
	media = g.db.get(Media, filename)
	if media:
		existing = g.db.query(MediaUsage).filter_by(filename=filename, post_id=p.id).one_or_none()
		if not existing:
			media_usage = MediaUsage(
				filename=filename,
				post_id=p.id,
			)
			g.db.add(media_usage)

		if existing and existing.deleted_utc and not p.deleted_utc:
			existing.deleted_utc = None

		if media.posterurl:
			p.posterurl = media.posterurl

def _add_post_view(pid):
	db = db_session()

	p = db.query(Post).filter_by(id=pid).options(load_only(Post.views)).one()
	p.views += 1
	db.add(p)

	try: db.commit()
	except: db.rollback()
	db.close()
	stdout.flush()

@app.post("/publish/<int:pid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def publish(pid, v):
	p = get_post(pid)

	if not p.draft:
		return {"message": "Post published!"}

	if p.author_id != v.id and v.admin_level < PERMS['PUBLISH_OTHERS_POSTS']:
		stop(403)

	if p.author.is_suspended and p.hole != 'chudrama':
		if SITE_NAME == 'rDrama':
			stop(403, "While temp-banned, you can only post in h/chudrama")
		stop(403, "You can't perform this action while banned!")

	p.draft = False
	p.created_utc = int(time.time())
	g.db.add(p)

	p.chudded = p.author.chud and p.hole != 'chudrama' and not (p.is_longpost and not p.author.chudded_by) and not p.distinguished
	p.queened = p.author.queen and not p.is_longpost and not p.distinguished
	p.sharpened = p.author.sharpen and not p.is_longpost and not p.distinguished
	p.rainbowed = p.author.rainbow and not p.is_longpost and not p.distinguished

	p.title_html = filter_emojis_only(p.title, golden=False, obj=p, author=p.author)
	p.body_html = sanitize(p.body, golden=False, limit_pings=POST_PING_LIMIT, obj=p, author=p.author)

	if p.draft or not complies_with_chud(p):
		stop(403, f'You have to include "{p.author.chud_phrase}" in your post!')

	notify_users = NOTIFY_USERS(f'{p.title} {p.body}', v, ghost=p.ghost, obj=p, followers_ping=False)

	if notify_users:
		cid, text = notif_comment_mention(p)
		if notify_users == 'everyone':
			alert_everyone(cid)
		else:
			for x in notify_users:
				add_notif(cid, x, text, pushnotif_url=p.permalink)

	if p.author.id in PINNED_POSTS_IDS and not p.ghost and not (p.hole and p.hole_obj.stealth):
		p.pinned_utc = time.time() + PINNED_POSTS_IDS[p.author.id] * 3600
		p.pinned = "AutoJanny"

	cache.delete_memoized(frontlist)
	cache.delete_memoized(userpagelisting)

	execute_snappy(p, v)

	if p.effortpost and not (SITE_NAME == 'WPD' and p.author.truescore < 500) and p.can_be_effortpost:
		body = f"@{p.author.username} has requested that {p.textlink} be marked as an effortpost!"
		alert_admins(body)
	
	p.effortpost = False

	return {"message": "Post has been published successfully!"}

@app.get("/submit")
@app.get("/h/<hole>/submit")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def submit_get(v, hole=None):
	hole = get_hole(hole, graceful=True)

	if request.path.startswith('/h/') and not hole: stop(404)

	hole_objs = g.db.query(Hole) if SITE_NAME == 'WPD' else None

	return render_template("submit.html", v=v, hole=hole, hole_objs=hole_objs)

@app.get("/post/<int:pid>")
@app.get("/post/<int:pid>/<anything>")
@app.get("/h/<hole>/post/<int:pid>")
@app.get("/h/<hole>/post/<int:pid>/<anything>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_desired_with_logingate
def post_id(pid, v, anything=None, hole=None):
	p = get_post(pid, v=v)
	if not can_see(v, p): stop(403)

	if not g.is_api_or_xhr and p.nsfw  and not g.show_nsfw:
		return render_template("errors/nsfw.html", v=v)

	gevent.spawn(_add_post_view, pid)

	if p.new: defaultsortingcomments = 'new'
	elif v: defaultsortingcomments = v.defaultsortingcomments
	else: defaultsortingcomments = "hot"
	sort = request.values.get("sort", defaultsortingcomments)

	if sort == 'saves':
		sort = defaultsortingcomments

	if not v:
		result = cache.get(f'post_{p.id}_{sort}')
		if result:
			calc_users()
			return result

	if v:
		execute_shadowban_viewers_and_voters(v, p)
		# output is needed: see comments.py
		comments, output = get_comments_v_properties(v, None, Comment.parent_post == p.id, Comment.level < 10)

		if sort == "hot" or sort == defaultsortingcomments:
			pinned = [c[0] for c in comments.filter(Comment.pinned != None).order_by(Comment.created_utc.desc())]
			comments = comments.filter(Comment.pinned == None)

		comments = comments.filter(Comment.level == 1)
		comments = sort_objects(sort, comments, Comment)
		comments = [c[0] for c in comments]
	else:
		comments = g.db.query(Comment).filter(Comment.parent_post == p.id)

		if sort == "hot" or sort == defaultsortingcomments:
			pinned = comments.filter(Comment.pinned != None).order_by(Comment.created_utc.desc()).all()
			comments = comments.filter(Comment.pinned == None)

		comments = comments.filter(Comment.level == 1)
		comments = sort_objects(sort, comments, Comment)
		comments = comments.all()

	offset = 0
	ids = set()

	threshold = 100

	if p.comment_count > threshold+25 and not (v and v.client):
		comments2 = []
		count = 0
		if p.created_utc > 1638672040:
			for comment in comments:
				comments2.append(comment)
				ids.add(comment.id)
				count += g.db.query(Comment).filter_by(parent_post=p.id, top_comment_id=comment.id).count() + 1
				if count > threshold: break
		else:
			for comment in comments:
				comments2.append(comment)
				ids.add(comment.id)
				count += g.db.query(Comment).filter_by(parent_post=p.id, parent_comment_id=comment.id).count() + 1
				if count > 20: break

		if len(comments) == len(comments2): offset = 0
		else: offset = 1
		comments = comments2

	p.replies = comments

	if sort == "hot" or sort == defaultsortingcomments:
		pinned2 = {}
		for pin in pinned:
			if pin.level > 1:
				pinned2[pin.top_comment] = ''
				ids.add(pin.top_comment.id)
				if pin.top_comment in comments:
					comments.remove(pin.top_comment)
			else:
				pinned2[pin] = ''
				ids.add(pin.id)

		p.replies = list(pinned2.keys()) + p.replies

	if v and v.client:
		return p.json

	template = "post.html"
	if p.is_banned and not (v and (v.admin_level >= PERMS['POST_COMMENT_MODERATION'] or p.author_id == v.id)):
		template = "post_banned.html"

	result = render_template(template, v=v, p=p, ids=list(ids),
		sort=sort, render_replies=True, offset=offset, hole=p.hole_obj,
		fart=get_setting('fart_mode'))

	if not v:
		cache.set(f'post_{p.id}_{sort}', result, timeout=3600)

	return result

@app.get("/view_more/<int:pid>/<sort>/<int:offset>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_desired_with_logingate
def view_more(v, pid, sort, offset):
	p = get_post(pid, v=v)

	try: ids = set(int(x) for x in request.values.get("ids").split(','))
	except: stop(400)

	if v:
		# output is needed: see comments.py
		comments, output = get_comments_v_properties(v, None, Comment.parent_post == pid, Comment.id.notin_(ids), Comment.level < 10)

		if sort == "hot":
			comments = comments.filter(Comment.pinned == None, Comment.num_of_pinned_children == 0)

		comments = comments.filter(Comment.level == 1)
		comments = sort_objects(sort, comments, Comment)

		comments = [c[0] for c in comments]
	else:
		comments = g.db.query(Comment).filter(
				Comment.parent_post == pid,
				Comment.level == 1,
				Comment.id.notin_(ids)
			)

		if sort == "hot":
			comments = comments.filter(Comment.pinned == None, Comment.num_of_pinned_children == 0)

		comments = sort_objects(sort, comments, Comment)

		comments = comments.offset(offset).all()

	comments2 = []
	count = 0
	if p.created_utc > 1638672040:
		for comment in comments:
			comments2.append(comment)
			ids.add(comment.id)
			count += g.db.query(Comment).filter_by(parent_post=p.id, top_comment_id=comment.id).count() + 1
			if count > 100: break
	else:
		for comment in comments:
			comments2.append(comment)
			ids.add(comment.id)
			count += g.db.query(Comment).filter_by(parent_post=p.id, parent_comment_id=comment.id).count() + 1
			if count > 20: break

	if len(comments) == len(comments2): offset = 0
	else: offset += 1
	comments = comments2

	return render_template("comments.html", v=v, comments=comments, p=p, ids=list(ids), render_replies=True, pid=pid, sort=sort, offset=offset)


@app.get("/more_comments/<int:cid>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@auth_desired_with_logingate
def more_comments(v, cid):
	tcid = g.db.query(Comment.top_comment_id).filter_by(id=cid).one_or_none()[0]

	if v:
		# output is needed: see comments.py
		comments, output = get_comments_v_properties(v, None, Comment.top_comment_id == tcid, Comment.level > 9)
		comments = comments.filter(Comment.parent_comment_id == cid)
		comments = [c[0] for c in comments]
	else:
		c = get_comment(cid)
		comments = c.replies(sort=request.values.get('sort'))

	if comments: p = comments[0].post
	else: p = None

	return render_template("comments.html", v=v, comments=comments, p=p, render_replies=True)

def expand_url(post_url, fragment_url):
	if fragment_url.startswith("https://"):
		return fragment_url
	elif fragment_url.startswith('//'):
		return f"https:{fragment_url}"
	elif fragment_url.startswith('/') and '\\' not in fragment_url:
		parsed_url = urlparse(post_url)
		return f"https://{parsed_url.netloc}{fragment_url}"
	else:
		return f"{post_url}/{fragment_url}"


def postprocess_post(post_url, post_body, post_body_html, pid, generate_thumb, edit):
	with app.app_context():
		if post_url and (reddit_s_url_regex.fullmatch(post_url) or tiktok_t_url_regex.fullmatch(post_url)):
			post_url = normalize_url_gevent(post_url)

		if post_body:
			li = list(reddit_s_url_regex.finditer(post_body)) + list(tiktok_t_url_regex.finditer(post_body))
			for i in li:
				old = i.group(0)
				new = normalize_url_gevent(old)
				post_body = post_body.replace(old, new)
				post_body_html = post_body_html.replace(old, new)

		g.db = db_session()

		p = g.db.query(Post).filter_by(id=pid).options(load_only(Post.id)).one_or_none()
		p.url = post_url
		p.body = post_body
		p.body_html = post_body_html
		g.db.add(p)

		if not p.draft and not edit:
			execute_snappy(p, p.author)

		g.db.commit()
		g.db.close()

		stdout.flush()


		#thumbnail
		if not generate_thumb or not post_url:
			return

		if post_url.startswith('https://youtube.com/watch?v='):
			id, _ = get_youtube_id_and_t(post_url)
			url = f'https://i.ytimg.com/vi/{id}/hqdefault.jpg'
			image_req = requests.get(url, headers=HEADERS, timeout=5, proxies=proxies)
		else:
			if post_url.startswith('/') and '\\' not in post_url:
				post_url = f"{SITE_FULL}{post_url}"

			try:
				x = requests.get(post_url, headers=HEADERS, timeout=5, proxies=proxies)
			except:
				return

			if x.status_code != 200:
				return

			if x.headers.get("Content-Type","").startswith("text/html"):
				soup = BeautifulSoup(x.content, 'lxml')

				thumb_candidate_urls = []

				for tag_name in ("twitter:image", "og:image", "thumbnail"):
					tag = soup.find('meta', attrs={"name": tag_name, "content": True})
					if not tag:
						tag = soup.find('meta', attrs={"property": tag_name, "content": True})
					if tag:
						thumb_candidate_urls.append(expand_url(post_url, tag['content']))

				for tag in soup.find_all("img", attrs={'src': True}):
					thumb_candidate_urls.append(expand_url(post_url, tag['src']))

				for url in thumb_candidate_urls:
					try:
						image_req = requests.get(url, headers=HEADERS, timeout=5, proxies=proxies)
					except:
						continue

					if image_req.status_code >= 400:
						continue

					if not image_req.headers.get("Content-Type","").startswith("image/"):
						continue

					if image_req.headers.get("Content-Type","").startswith("image/svg"):
						continue

					with Image.open(BytesIO(image_req.content)) as i:
						if i.width < 30 or i.height < 30:
							continue
					break
				else:
					return
			elif x.headers.get("Content-Type","").startswith("image/"):
				image_req = x
				with Image.open(BytesIO(x.content)) as i:
					size = len(i.fp.read())
					if size > 8 * 1024 * 1024:
						return
			else:
				return

		name = f'/images/{time.time()}'.replace('.','') + '.webp'

		with open(name, "wb") as file:
			for chunk in image_req.iter_content(1024):
				file.write(chunk)

		g.db = db_session()

		p = g.db.query(Post).filter_by(id=pid).options(load_only(Post.author_id)).one_or_none()

		thumburl = process_image(name, None, resize=199, uploader_id=p.author_id)

		if thumburl:
			p.thumburl = thumburl
			g.db.add(p)

		g.db.commit()
		g.db.close()

	stdout.flush()


@app.post("/is_repost")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def is_repost(v):
	not_a_repost = {'permalink': ''}
	if not FEATURES['REPOST_DETECTION']:
		return not_a_repost

	url = request.values.get('url').rstrip('/')
	if not url or len(url) < MIN_REPOST_CHECK_URL_LENGTH or not url.startswith('http'):
		stop(400)

	if reddit_s_url_regex.fullmatch(url) or tiktok_t_url_regex.fullmatch(url):
		try: url = normalize_url_gevent(url)
		except: stop(400)

	url = normalize_url(url)

	url = escape_for_search(url)

	repost = g.db.query(Post).filter(
		or_(
			Post.url.ilike(url),
			Post.url.ilike(f'{url}/'),
		),
		Post.deleted_utc == 0,
		Post.is_banned == False
	).first()

	if repost: return {'permalink': repost.permalink}
	else: return not_a_repost

@app.post("/submit")
@app.post("/h/<hole>/submit")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit('20/day', deduct_when=lambda response: response.status_code < 400)
@limiter.limit('20/day', deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def submit_post(v, hole=None):
	flag_draft = request.values.get("draft", False, bool)

	url = _make_post_url()

	title = request.values.get("title", "").replace('\x00', '').replace('\n', ' ').strip()
	if len(title) > POST_TITLE_LENGTH_LIMIT:
		stop(400, f'Post title is too long (max {POST_TITLE_LENGTH_LIMIT} characters)')

	body = request.values.get("body", "").replace('\x00', '').strip()
	if len(body) > POST_BODY_LENGTH_LIMIT(g.v):
		stop(400, f'Post body is too long (max {POST_BODY_LENGTH_LIMIT(g.v)} characters)')

	body = body.replace('@jannies', '!jannies')

	if not title:
		stop(400, "Please enter a better title!")

	hole = request.values.get("hole", "").lower().replace('/h/','').replace('\x00', '').strip()

	if SITE == 'rdrama.net' and v.chud == 1:
		hole = 'chudrama'

	if SITE == 'rdrama.net' and v.id in {4358, 18286}:
		hole = 'slavshit'

	if SITE == 'rdrama.net' and v.id == 10947:
		hole = 'mnn'

	if v.is_suspended and hole != 'chudrama' and not flag_draft:
		if SITE_NAME == 'rDrama':
			stop(403, "While temp-banned, you can only post in h/chudrama")
		stop(403, "You can't perform this action while banned!")

	if hole == 'changelog':
		stop(400, "/h/changelog is archived")

	if hole == 'announcements' and v.admin_level < PERMS["POST_IN_H_ANNOUNCEMENTS"]:
		stop(400, "Your admin-level is not sufficient enough for this action!")

	if hole in {'furry','vampire','racist','femboy','edgy'} and not v.client and not v.house.lower().startswith(hole):
		stop(400, f"You need to be a member of House {hole.capitalize()} to post in /h/{hole}")

	if hole and hole != 'none':
		hole_name = hole.strip().lower()
		hole = g.db.query(Hole).options(load_only(Hole.name)).filter_by(name=hole_name).one_or_none()

		if not hole:
			stop(400, f"/h/{hole_name} not found!")

		if hole.dead_utc:
			stop(400, f'/h/{hole_name} is dead. You can resurrect it at a cost if you wish.')

		if not can_see(v, hole):
			if hole.name == 'highrollerclub':
				stop(403, f"Only {patron}s can post in /h/{hole}")
			stop(403, f"You're not allowed to post in /h/{hole}")

		hole = hole.name
		if v.exiler_username(hole): stop(400, f"You're exiled from /h/{hole}")
	else: hole = None

	if not hole and HOLE_REQUIRED:
		stop(400, f"You must choose a hole for your post!")

	flag_distinguished = request.values.get("distinguished", False, bool) and v.admin_level >= PERMS['POST_COMMENT_DISTINGUISH']

	if not flag_distinguished:
		if v.longpost and (len(body) < 280 or ' [](' in body or body.startswith('[](')):
			stop(400, "You have to type more than 280 characters!")
		elif v.bird and len(body) > 140:
			stop(400, "You have to type less than 140 characters!")


	embed = _check_domain_ban_and_make_post_embed(url, v)

	if not url and not body and not request.files.get("file") and not request.files.get("file-url"):
		stop(400, "Please enter a url or some text!")

	if not IS_LOCALHOST:
		dup = g.db.query(Post).filter(
			Post.author_id == v.id,
			Post.deleted_utc == 0,
			Post.title == title,
			Post.url == url,
			Post.body == body
		).first()
		if dup:
			return {"post_id": dup.id, "success": False}

	if not execute_antispam_post_check(title, v, url):
		stop(403, "You have been banned for 1 day for spamming!")

	body = process_files(request.files, v, body).strip()
	if len(body) > POST_BODY_LENGTH_LIMIT(g.v):
		stop(400, f'Post body is too long (max {POST_BODY_LENGTH_LIMIT(g.v)} characters)')

	flag_notify = (request.values.get("notify", "on") == "on")
	flag_new = request.values.get("new", False, bool) or 'megathread' in title.lower()
	flag_nsfw = FEATURES['NSFW_MARKING'] and request.values.get("nsfw", False, bool)
	flag_effortpost = request.values.get("effortpost", False, bool)
	flag_ghost = request.values.get("ghost", False, bool) and v.can_post_in_ghost_threads

	if flag_ghost: hole = None

	p = Post(
		draft=flag_draft,
		notify=flag_notify,
		author_id=v.id,
		nsfw=flag_nsfw,
		new=flag_new,
		app_id=v.client.application.id if v.client else None,
		is_bot=(v.client is not None),
		url=url,
		body=body,
		embed=embed,
		title=title,
		hole=hole,
		ghost=flag_ghost,
		distinguished=flag_distinguished,
	)

	if SITE_NAME == 'WPD':
		p.cw = request.values.get("cw", False, bool)

	if not p.draft:
		p.chudded = v.chud and hole != 'chudrama' and not (p.is_longpost and not v.chudded_by) and not p.distinguished
		p.queened = v.queen and not p.is_longpost and not p.distinguished
		p.sharpened = v.sharpen and not p.is_longpost and not p.distinguished
		p.rainbowed = v.rainbow and not p.is_longpost and not p.distinguished

	title_html = filter_emojis_only(title, count_emojis=True, obj=p, author=v)

	if v.hieroglyphs and not p.distinguished and not marseyaward_title_regex.fullmatch(title_html):
		stop(400, "You can only type emojis!")

	p.title_html = title_html

	g.db.add(p)
	body_html = sanitize(body, count_emojis=True, limit_pings=POST_PING_LIMIT, obj=p, author=v)

	if v.hieroglyphs and not p.distinguished and marseyaward_body_regex.search(body_html):
		stop(400, "You can only type emojis!")

	if len(body_html) > POST_BODY_HTML_LENGTH_LIMIT:
		stop(400, "Rendered post body is too long!")

	p.body_html = body_html

	g.db.add(p)
	g.db.flush()

	if SITE == 'watchpeopledie.tv' and p.cw and p.hole == 'selfharm':
		text = f"ALERT: @{v.username} has added a child warning to {p.textlink} despite the post being in /h/selfharm"
		alert_admins(text)

	execute_under_siege(v, p, 'post')

	process_options(v, p)

	for text in {p.body, p.title, p.url}:
		if execute_blackjack(v, p, text, 'post'): break

	vote = Vote(user_id=v.id,
				vote_type=1,
				post_id=p.id,
				coins=0
				)
	g.db.add(vote)

	if request.files.get('file-url') and not g.is_tor:
		_process_post_attachement(p, v)
	elif p.url and p.url.startswith(SITE_FULL_VIDEOS):
		_register_duplicate_media_usage_and_get_poster(p)

	if not p.draft and not complies_with_chud(p):
		p.is_banned = True

		for media_usage in p.media_usages:
			media_usage.removed_utc = time.time()
			g.db.add(media_usage)

		p.ban_reason = "AutoJanny for lack of chud phrase"

		body = random.choice(CHUD_MSGS).format(username=v.username, type='post', CHUD_PHRASE=v.chud_phrase)
		body_jannied_html = sanitize(body)


		c_jannied = Comment(author_id=AUTOJANNY_ID,
			parent_post=p.id,
			level=1,
			nsfw=False,
			is_bot=True,
			app_id=None,
			distinguished=True,
			body=body,
			body_html=body_jannied_html,
			ghost=p.ghost
		)

		g.db.add(c_jannied)
		g.db.flush()

		p.comment_count += 1
		g.db.add(p)

		c_jannied.top_comment_id = c_jannied.id

		n = Notification(comment_id=c_jannied.id, user_id=v.id)
		g.db.add(n)

		autojanny = g.db.get(User, AUTOJANNY_ID)
		autojanny.comment_count += 1
		g.db.add(autojanny)

	if not p.draft:
		notify_users = NOTIFY_USERS(f'{title} {body}', v, ghost=p.ghost, obj=p, followers_ping=False)

		if notify_users:
			cid, text = notif_comment_mention(p)
			if notify_users == 'everyone':
				alert_everyone(cid)
			else:
				for x in notify_users:
					add_notif(cid, x, text, pushnotif_url=p.permalink)

	v.post_count += 1
	g.db.add(v)

	if v.id in PINNED_POSTS_IDS and not p.ghost and not p.draft and not (p.hole and p.hole_obj.stealth):
		p.pinned_utc = time.time() + PINNED_POSTS_IDS[v.id] * 3600
		p.pinned = "AutoJanny"

	if p.distinguished:
		ma = ModAction(
			kind='distinguish_post',
			user_id=v.id,
			target_post_id=p.id
		)
		g.db.add(ma)


	if not p.draft and flag_effortpost and not (SITE_NAME == 'WPD' and v.truescore < 500) and p.can_be_effortpost:
		body = f"@{v.username} has requested that {p.textlink} be marked as an effortpost!"
		alert_admins(body)

	if p.draft and flag_effortpost and not (SITE_NAME == 'WPD' and v.truescore < 500):
		p.effortpost = True

	if any(i in p.title.lower() for i in ENCOURAGED) or any(i in str(p.url).lower() for i in ENCOURAGED2):
		send_notification(AEVANN_ID, p.permalink)

	g.db.commit()
	generate_thumb = (not p.thumburl and p.url and p.domain != SITE)
	gevent.spawn(postprocess_post, p.url, p.body, p.body_html, p.id, generate_thumb, False)

	cache.delete_memoized(frontlist)
	cache.delete_memoized(userpagelisting)

	if v.client: return p.json
	else:
		p.voted = 1
		return {"post_id": p.id, "success": True}

@app.post("/delete/post/<int:pid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DELETE_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DELETE_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def delete_post_pid(pid, v):
	p = get_post(pid)
	if p.author_id != v.id: stop(403)

	if not p.deleted_utc:
		p.deleted_utc = int(time.time())
		p.profile_pinned = False
		p.pinned = None
		p.pinned_utc = None

		g.db.add(p)

		p.author.truescore -= p.upvotes + p.downvotes - 1
		g.db.add(p.author)

		cache.delete_memoized(frontlist)
		cache.delete_memoized(userpagelisting)

		v.post_count -= 1
		g.db.add(v)

		for media_usage in p.media_usages:
			media_usage.deleted_utc = p.deleted_utc
			g.db.add(media_usage)

		for sort in COMMENT_SORTS.keys():
			cache.delete(f'post_{p.id}_{sort}')

	return {"message": "Post deleted!"}

@app.post("/undelete_post/<int:pid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def undelete_post_pid(pid, v):
	p = get_post(pid)
	if p.author_id != v.id: stop(403)

	if p.deleted_utc:
		p.deleted_utc = 0
		g.db.add(p)

		p.author.truescore += p.upvotes + p.downvotes - 1
		g.db.add(p.author)

		cache.delete_memoized(frontlist)
		cache.delete_memoized(userpagelisting)

		v.post_count += 1
		g.db.add(v)

		for media_usage in p.media_usages:
			media_usage.deleted_utc = None
			g.db.add(media_usage)

		for sort in COMMENT_SORTS.keys():
			cache.delete(f'post_{p.id}_{sort}')

	return {"message": "Post undeleted!"}


@app.post("/mark_post_nsfw/<int:pid>")
@feature_required('NSFW_MARKING')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def mark_post_nsfw(pid, v):
	p = get_post(pid)

	if p.author_id != v.id and v.admin_level < PERMS['POST_COMMENT_MODERATION'] and not v.mods_hole(p.hole):
		stop(403)

	p.nsfw = True
	g.db.add(p)

	if p.author_id != v.id:
		if v.admin_level >= PERMS['POST_COMMENT_MODERATION']:
			ma = ModAction(
					kind = "set_nsfw",
					user_id = v.id,
					target_post_id = p.id,
				)
			g.db.add(ma)
			position = 'a site admin'
		else:
			ma = HoleAction(
					hole = p.hole,
					kind = "set_nsfw",
					user_id = v.id,
					target_post_id = p.id,
				)
			g.db.add(ma)
			position = f'a /h/{p.hole} mod'

		send_repeatable_notification(p.author_id, f"@{v.username} ({position}) has marked {p.textlink} as NSFW")

	return {"message": "Post has been marked as NSFW!"}

@app.post("/unmark_post_nsfw/<int:pid>")
@feature_required('NSFW_MARKING')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def unmark_post_nsfw(pid, v):
	p = get_post(pid)

	if p.author_id != v.id and v.admin_level < PERMS['POST_COMMENT_MODERATION'] and not v.mods_hole(p.hole):
		stop(403)

	if p.nsfw and v.is_permabanned:
		stop(403)

	p.nsfw = False
	g.db.add(p)

	if p.author_id != v.id:
		if v.admin_level >= PERMS['POST_COMMENT_MODERATION']:
			ma = ModAction(
					kind = "unset_nsfw",
					user_id = v.id,
					target_post_id = p.id,
				)
			g.db.add(ma)
			position = 'a site admin'
		else:
			ma = HoleAction(
					hole = p.hole,
					kind = "unset_nsfw",
					user_id = v.id,
					target_post_id = p.id,
				)
			g.db.add(ma)
			position = f'a /h/{p.hole} mod'

		send_repeatable_notification(p.author_id, f"@{v.username} ({position}) has unmarked {p.textlink} as NSFW")

	return {"message": "Post has been unmarked as NSFW!"}

@app.post("/save_post/<int:pid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def save_post(pid, v):

	p = get_post(pid)

	save = g.db.query(SaveRelationship).filter_by(user_id=v.id, post_id=p.id).one_or_none()

	if not save:
		new_save=SaveRelationship(user_id=v.id, post_id=p.id)
		g.db.add(new_save)
		cache.delete_memoized(userpagelisting)

	return {"message": "Post saved!"}

@app.post("/unsave_post/<int:pid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def unsave_post(pid, v):

	p = get_post(pid)

	save = g.db.query(SaveRelationship).filter_by(user_id=v.id, post_id=p.id).one_or_none()

	if save:
		g.db.delete(save)
		cache.delete_memoized(userpagelisting)

	return {"message": "Post unsaved!"}

@app.post("/profile_pin/<int:post_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def profile_pin(post_id, v):
	p = get_post(post_id)
	if p:
		if v.id != p.author_id: stop(403, "Only the post author can do that!")
		p.profile_pinned = not p.profile_pinned
		g.db.add(p)
		cache.delete_memoized(userpagelisting)
		if p.profile_pinned: return {"message": "Post pinned!"}
		else: return {"message": "Post unpinned!"}
	return stop(404, "Post not found!")

@app.post("/post/<int:post_id>/new")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def set_new_sort(post_id, v):
	p = get_post(post_id)
	if not v.can_edit(p): stop(403, "Only the post author can do that!")
	p.new = True
	g.db.add(p)

	if v.id != p.author_id:
		ma = ModAction(
				kind = "set_new",
				user_id = v.id,
				target_post_id = p.id,
			)
		g.db.add(ma)
		send_repeatable_notification(p.author_id, f"@{v.username} (a site admin) has changed the the default sorting of comments on {p.textlink} to `new`")

	return {"message": "Changed the the default sorting of comments on this post to 'new'"}


@app.post("/post/<int:post_id>/hot")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def unset_new_sort(post_id, v):
	p = get_post(post_id)
	if not v.can_edit(p): stop(403, "Only the post author can do that!")
	p.new = None
	g.db.add(p)

	if v.id != p.author_id:
		ma = ModAction(
				kind = "set_hot",
				user_id = v.id,
				target_post_id = p.id,
			)
		g.db.add(ma)
		send_repeatable_notification(p.author_id, f"@{v.username} (a site admin) has changed the the default sorting of comments on {p.textlink} to `hot`")

	return {"message": "Changed the the default sorting of comments on this post to 'hot'"}


extensions = IMAGE_FORMATS + VIDEO_FORMATS + AUDIO_FORMATS

@app.get("/submit/title")
@limiter.limit("3/minute", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("3/minute", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def get_post_title(v):
	POST_TITLE_TIMEOUT = 5
	url = request.values.get("url")
	if not url or '\\' in url: stop(400)
	url = url.strip()
	if not url.startswith('http'): stop(400)

	checking_url = url.lower().split('?')[0].split('%3F')[0]
	if any(checking_url.endswith(f'.{x}') for x in extensions):
		stop(400)

	try:
		x = gevent.with_timeout(POST_TITLE_TIMEOUT, requests.get, url, headers=HEADERS, timeout=POST_TITLE_TIMEOUT, proxies=proxies)
	except: stop(400)

	content_type = x.headers.get("Content-Type")
	if not content_type or "text/html" not in content_type: stop(400)

	# no you can't just parse html with reeeeeeeegex
	match = html_title_regex.search(x.text)
	if match and match.lastindex >= 1:
		title = match.group(1)
	else: stop(400)

	title = html.unescape(title)

	return {"url": url, "title": title}

@app.post("/edit_post/<int:pid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def edit_post(pid, v):
	p = get_post(pid)
	if not v.can_edit(p): stop(403)

	if SITE_NAME == 'rDrama': days = 7
	else: days = 30
	if not p.effortpost and time.time() - p.created_utc > days*24*60*60 and not p.draft and v.admin_level < PERMS["IGNORE_EDITING_LIMIT"] and v.id not in EXEMPT_FROM_EDITING_LIMIT:
		stop(403, f"You can't edit posts older than {days} days!")

	if p.is_banned:
		stop(403, "You can't edit posts that were removed by admins!")

	title = request.values.get("title", "").strip()
	if len(title) > POST_TITLE_LENGTH_LIMIT:
		stop(400, f'Post title is too long (max {POST_TITLE_LENGTH_LIMIT} characters)')

	body = request.values.get("body", "").strip()
	if len(body) > POST_BODY_LENGTH_LIMIT(g.v):
		stop(400, f'Post body is too long (max {POST_BODY_LENGTH_LIMIT(g.v)} characters)')

	body = body.replace('@jannies', '!jannies')

	if not p.distinguished:
		if p.author.longpost and (len(body) < 280 or ' [](' in body or body.startswith('[](')):
			stop(403, "You have to type more than 280 characters!")
		elif p.author.bird and len(body) > 140:
			stop(403, "You have to type less than 140 characters!")

	if not title:
		stop(400, "Please enter a better title!")


	if not p.draft:
		notify_users = NOTIFY_USERS(f'{title} {body}', v, oldtext=f'{p.title} {p.body}', ghost=p.ghost, obj=p, followers_ping=False)
		if notify_users:
			cid, text = notif_comment_mention(p)
			if notify_users == 'everyone':
				alert_everyone(cid)
			else:
				for x in notify_users:
					add_notif(cid, x, text, pushnotif_url=p.permalink)

	changed = False
	change_thumb = False

	if int(time.time()) - p.created_utc > 60 * 3:
		edit_log = PostEdit(
			post_id=p.id,
			old_title=p.title,
			old_title_html=p.title_html,
			old_body=p.body,
			old_body_html=p.body_html,
			old_url=p.url,
		)
		g.db.add(edit_log)

	if title != p.title:
		title_html = filter_emojis_only(title, golden=False, obj=p, author=p.author)

		if p.author.hieroglyphs and not p.distinguished and not marseyaward_title_regex.fullmatch(title_html):
			stop(403, "You can only type emojis!")

		if 'megathread' in title.lower() and 'megathread' not in p.title.lower():
			p.new = True

		p.title = title
		p.title_html = title_html

		changed = True

	body = process_files(request.files, v, body).strip()
	if len(body) > POST_BODY_LENGTH_LIMIT(g.v):
		stop(400, f'Post body is too long (max {POST_BODY_LENGTH_LIMIT(g.v)} characters)')

	if body != p.body or p.chudded:
		body_html = sanitize(body, golden=False, limit_pings=POST_PING_LIMIT, obj=p, author=p.author)

		if p.author.hieroglyphs and not p.distinguished and marseyaward_body_regex.search(body_html):
			stop(403, "You can only type emojis!")


		p.body = body

		if len(body_html) > POST_BODY_HTML_LENGTH_LIMIT:
			stop(400, "Rendered post body is too long!")

		p.body_html = body_html

		process_options(v, p)

		changed = True

	url = _make_post_url()

	if request.files.get('file-url') and not g.is_tor:
		_process_post_attachement(p, v)
		changed = True
	elif url != p.url:
		p.url = url
		p.embed = _check_domain_ban_and_make_post_embed(p.url, v)
		changed = True
		change_thumb = True

		if p.url and p.url.startswith(SITE_FULL_VIDEOS):
			_register_duplicate_media_usage_and_get_poster(p)

	if not changed:
		stop(400, "You need to change something!")

	if not p.draft and not complies_with_chud(p):
		stop(403, f'You have to include "{p.author.chud_phrase}" in your post!')

	for text in [p.body, p.title, p.url]:
		if execute_blackjack(v, p, text, 'post'): break

	if v.id == p.author_id:
		if not p.draft and int(time.time()) - p.created_utc > 60 * 3:
			p.edited_utc = int(time.time())
	else:
		ma = ModAction(
			kind="edit_post",
			user_id=v.id,
			target_post_id=p.id
		)
		g.db.add(ma)

	for media_usage in p.media_usages:
		url = SITE_FULL_VIDEOS + media_usage.filename.split('/videos')[1]
		if url not in f'{p.url} {p.body}':
			media_usage.deleted_utc = time.time()
			g.db.add(media_usage)

	if any(i in p.title.lower() for i in ENCOURAGED) or any(i in str(p.url).lower() for i in ENCOURAGED2):
		send_notification(AEVANN_ID, p.permalink)

	if body != p.body or p.chudded or change_thumb:
		g.db.commit()
		gevent.spawn(postprocess_post, p.url, p.body, p.body_html, p.id, change_thumb, True)

	cache.delete_memoized(frontlist)
	cache.delete_memoized(userpagelisting)

	for sort in COMMENT_SORTS.keys():
		cache.delete(f'post_{p.id}_{sort}')

	return {"message": "Post edited successfully!"}

if SITE_NAME == 'WPD':
	@app.post("/mark_post_cw/<int:pid>")
	@limiter.limit('1/second', scope=rpath)
	@limiter.limit('1/second', scope=rpath, key_func=get_ID)
	@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
	@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
	@auth_required
	def mark_post_cw(pid, v):
		p = get_post(pid)

		if p.author_id != v.id and v.admin_level < PERMS['POST_COMMENT_MODERATION']:
			stop(403)

		p.cw = True
		g.db.add(p)

		if p.author_id != v.id:
			ma = ModAction(
					kind = "set_cw",
					user_id = v.id,
					target_post_id = p.id,
				)
			g.db.add(ma)
			send_repeatable_notification(p.author_id, f"@{v.username} (a site admin) has add a child warning to {p.textlink}")

		return {"message": "A child warning has been added to the post!"}

	@app.post("/unmark_post_cw/<int:pid>")
	@limiter.limit('1/second', scope=rpath)
	@limiter.limit('1/second', scope=rpath, key_func=get_ID)
	@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
	@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
	@auth_required
	def unmark_post_cw(pid, v):
		p = get_post(pid)

		if p.author_id != v.id and v.admin_level < PERMS['POST_COMMENT_MODERATION']:
			stop(403)

		p.cw = False
		g.db.add(p)

		if p.author_id != v.id:
			ma = ModAction(
					kind = "unset_cw",
					user_id = v.id,
					target_post_id = p.id,
				)
			g.db.add(ma)
			send_repeatable_notification(p.author_id, f"@{v.username} (a site admin) has removed the child warning from {p.textlink}")

		return {"message": "The child warning has been removed from the post!"}


@app.post("/distinguish/<int:post_id>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def distinguish_post(post_id, v):
	post = get_post(post_id)

	if v.admin_level < PERMS['POST_COMMENT_DISTINGUISH'] and not v.mods_hole(post.hole):
		stop(403, "You can't distinguish this post")

	if post.distinguished:
		post.distinguished = False
		kind = 'undistinguish_post'
	else:
		post.distinguished = True
		kind = 'distinguish_post'

	g.db.add(post)

	if v.admin_level >= PERMS['POST_COMMENT_DISTINGUISH']:
		cls = ModAction
	else:
		cls = HoleAction

	ma = cls(
		kind=kind,
		user_id=v.id,
		target_post_id=post.id
	)
	if cls == HoleAction:
		ma.hole = post.hole
	g.db.add(ma)


	if post.distinguished: return {"message": "Post distinguished!"}
	else: return {"message": "Post undistinguished!"}
