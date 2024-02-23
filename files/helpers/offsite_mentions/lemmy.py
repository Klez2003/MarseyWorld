import requests
from flask import g

from files.helpers.config.const import *
from files.classes.comment import Comment
from files.helpers.sanitize import *
from files.helpers.alerts import push_notif
from files.classes.notifications import Notification

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
				text = sanitize(text, blackjack="lemmy mention", golden=False)

				existing_comment = g.db.query(Comment.id).filter_by(
					author_id=AUTOJANNY_ID,
					parent_post=None,
					body_html=text).one_or_none()
				if existing_comment: break

				try: created_utc = int(time.mktime(time.strptime(thing['published'].split('.')[0], "%Y-%m-%dT%H:%M:%S")))
				except: created_utc = int(time.mktime(time.strptime(thing['published'].split('.')[0], "%Y-%m-%dT%H:%M:%SZ")))

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
