import requests
from flask import g

from files.helpers.config.const import *
from files.classes.comment import Comment
from files.helpers.sanitize import *
from files.helpers.alerts import push_notif
from files.classes.notifications import Notification

def notify(body, created_utc):
	if len(body) > 2000:
		body = body[:2000] + "......"

	existing_comment = g.db.query(Comment.id).filter_by(
		author_id=AUTOJANNY_ID,
		parent_post=None,
		body=body).one_or_none()

	if existing_comment:
		return 1

	body_html = sanitize(body, blackjack="offsite mention", golden=False)

	new_comment = Comment(
						author_id=AUTOJANNY_ID,
						parent_post=None,
						body=body,
						body_html=body_html,
						distinguished=True,
						created_utc=created_utc,
					)

	g.db.add(new_comment)
	g.db.flush()
	new_comment.top_comment_id = new_comment.id


def reddit_mentions_task():
	for kind in ("submission", "comment"):
		q = " or ".join(OFFSITE_NOTIF_QUERIES)
		url = f'https://api.pullpush.io/reddit/search/{kind}?q={q}'
		try: data = requests.get(url, headers=HEADERS, timeout=20).json()['data']
		except Exception as e:
			print(f'reddit mentions: {e}', flush=True)
			return

		for thing in data:
			if not thing.get('permalink'): continue
			if thing.get('subreddit_subscribers') and thing['subreddit_subscribers'] < 2:continue
			if thing.get('subreddit_type') == 'user': continue
			if thing['subreddit'] in {'IAmA', 'PokemonGoRaids', 'SubSimulatorGPT2', 'SubSimGPT2Interactive'}: continue
			if 'bot' in thing['author'].lower(): continue
			if thing['author'] == 'AutoModerator': continue

			if kind == 'comment':
				body = thing["body"].replace('>', '> ')
				if SITE_NAME == 'rDrama' and 'teenager' in body: continue
				text = f'<blockquote><p>{body}</p></blockquote>'
			else:
				title = thing["title"].replace('>', '> ')

				if 'Kathrine Mclaurin' in title: continue
				text = f'<blockquote><p>{title}</p></blockquote>'

				if thing["selftext"]:
					selftext = thing["selftext"].replace('>', '> ')[:5000]
					text += f'<br><blockquote><p>{selftext}</p></blockquote>'

			author_string = f"/u/{thing['author']}"
			permalink = 'https://old.reddit.com' + thing['permalink']
			text = offsite_query_regex.sub(r'<span class="offsite-alert">\1</span>', text)
			text =  f'New site mention by {author_string}\n\n**{permalink}**\n\n{text}'
			created_utc = thing['created_utc']
			if notify(text, created_utc) == 1: break


def lemmy_mentions_task():
	for q in OFFSITE_NOTIF_QUERIES:
		url = f'https://lemm.ee/api/v3/search?q={q}'
		try: data = requests.get(url, headers=HEADERS, timeout=20, proxies=proxies).json()
		except Exception as e:
			print(f'lemmy mentions: {e}', flush=True)
			return

		for kind in ("post", "comment"):
			for thing in data[f'{kind}s']:
				creator = thing['creator']
				author_string = f"[/u/{creator['name']}]({creator['actor_id']})"
				thing = thing[kind]
				if kind == 'comment':
					body = thing["content"]
					text = f'<blockquote><p>{body}</p></blockquote>'
				else:
					title = thing["name"]
					text = f'<blockquote><p>{title}</p></blockquote>'

					if thing.get("body"):
						selftext = thing["body"][:5000]
						text += f'<br><blockquote><p>{selftext}</p></blockquote>'

				if 'erdrama' in text.lower(): continue

				permalink = thing['ap_id']
				text = offsite_query_regex.sub(r'<span class="offsite-alert">\1</span>', text)
				text =  f'New site mention by {author_string}\n\n**{permalink}**\n\n{text}'
				try: created_utc = int(time.mktime(time.strptime(thing['published'].split('.')[0], "%Y-%m-%dT%H:%M:%S")))
				except: created_utc = int(time.mktime(time.strptime(thing['published'].split('.')[0], "%Y-%m-%dT%H:%M:%SZ")))
				if notify(text, created_utc) == 1: break


def fourchan_mentions_task():
	queries = OFFSITE_NOTIF_QUERIES - {'r/drama'}
	for q in queries:
		url = f'https://archived.moe/_/api/chan/search?text={q}'
		try: data = requests.get(url, headers=HEADERS, timeout=20, proxies=proxies).json()['0']['posts']
		except Exception as e:
			print(f'4chan mentions: {e}', flush=True)
			return

		for thing in data:
			board = thing['board']['shortname']
			author_string = thing['name']
			num = thing["num"]
			thread_num = thing["thread_num"]

			if num != thread_num:
				text = f'<blockquote><p>{thing["comment"]}</p></blockquote>'
				permalink = f'https://archived.moe/{board}/thread/{thread_num}/#{num}'
			else:
				text = f'<blockquote><p>{thing["title"]}</p></blockquote><br><blockquote><p>{thing["comment"]}</p></blockquote>'
				permalink = f'https://archived.moe/{board}/thread/{thread_num}'

			text = offsite_query_regex.sub(r'<span class="offsite-alert">\1</span>', text)
			text = f'New site mention by {author_string}\n\n**{permalink}**\n\n{text}'
			created_utc = thing["timestamp"]
			if notify(text, created_utc) == 1: break


def soyjak_mentions_task():
	for q in OFFSITE_NOTIF_QUERIES:
		url = f'https://api.marge.moe/search?q={q}'
		try: data = requests.get(url, headers={"User-Agent": "MarseyFromWPD"}, timeout=20, proxies=proxies).json()['results']
		except Exception as e:
			print(f'soyjak mentions: {e}', flush=True)
			return

		for thing in data:
			text = f'<blockquote><p>{thing["comment"]}</p></blockquote>'
			if 'erdrama' in text.lower(): continue
			if 'rdrama won' in text.lower(): continue
			permalink = thing['url']
			text = offsite_query_regex.sub(r'<span class="offsite-alert">\1</span>', text)
			text =  f'New site mention\n\n**{permalink}**\n\n{text}'
			created_utc = int(time.mktime(time.strptime(thing['date'].split('.')[0], "%Y-%m-%dT%H:%M:%S")))
			if notify(text, created_utc) == 1: break
