import requests
from flask import g

from files.helpers.config.const import *
from files.classes.comment import Comment
from files.helpers.sanitize import *
from files.helpers.alerts import push_notif
from files.classes.notifications import Notification

def notify(text, created_utc):
	text = sanitize(text, blackjack="offsite mention", golden=False)

	existing_comment = g.db.query(Comment.id).filter_by(
		author_id=AUTOJANNY_ID,
		parent_post=None,
		body_html=text).one_or_none()

	if existing_comment:
		return 1

	new_comment = Comment(
						author_id=AUTOJANNY_ID,
						parent_post=None,
						body_html=text,
						distinguished=True,
						created_utc=created_utc,
					)

	g.db.add(new_comment)
	g.db.flush()
	new_comment.top_comment_id = new_comment.id


def lemmy_mentions_task():
	for q in OFFSITE_NOTIF_QUERIES:
		url = f'https://lemm.ee/api/v3/search?q={q}'
		data = requests.get(url, headers=HEADERS, timeout=5).json()

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

				if 'erdrama' in text: continue

				permalink = thing['ap_id']
				text =  f'New site mention by {author_string}\n\n{permalink}\n\n{text}'
				try: created_utc = int(time.mktime(time.strptime(thing['published'].split('.')[0], "%Y-%m-%dT%H:%M:%S")))
				except: created_utc = int(time.mktime(time.strptime(thing['published'].split('.')[0], "%Y-%m-%dT%H:%M:%SZ")))
				if notify(text, created_utc) == 1: break


def fourchan_mentions_task():
	queries = OFFSITE_NOTIF_QUERIES - {'r/drama'}
	for q in queries:
		url = f'https://archived.moe/_/api/chan/search?text={q}'
		data = requests.get(url, headers=HEADERS).json()['0']['posts']

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

			text = f'New site mention by {author_string}\n\n{permalink}\n\n{text}'
			created_utc = thing["timestamp"]
			if notify(text, created_utc) == 1: break


def soyjak_mentions_task():
	for q in OFFSITE_NOTIF_QUERIES:
		url = f'https://api.marge.moe/search?q={q}'
		data = requests.get(url, headers={"User-Agent": "MarseyFromWPD"}, proxies=proxies).json()['results']

		for thing in data:
			text = f'<blockquote><p>{thing["comment"]}</p></blockquote>'
			permalink = thing['url']
			text =  f'New site mention\n\n{permalink}\n\n{text}'
			created_utc = int(time.mktime(time.strptime(thing['date'].split('.')[0], "%Y-%m-%dT%H:%M:%S")))
			if notify(text, created_utc) == 1: break
