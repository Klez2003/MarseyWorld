import requests
from flask import g

from files.helpers.config.const import *
from files.classes.comment import Comment
from files.helpers.sanitize import *
from files.helpers.alerts import push_notif
from files.classes.notifications import Notification

def fourchan_mentions_task():
	queries = OFFSITE_NOTIF_QUERIES - {'r/drama'}
	for q in queries:
		url = f'https://archived.moe/_/api/chan/search?text={q}'
		data = requests.get(url, headers=HEADERS, timeout=5).json()['0']['posts']

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

			text =  f'New site mention by {author_string}\n\n{permalink}\n\n{text}'
			text = sanitize(text, blackjack="fourchan mention", golden=False)

			existing_comment = g.db.query(Comment.id).filter_by(
				author_id=AUTOJANNY_ID,
				parent_post=None,
				body_html=text).one_or_none()
			if existing_comment: break

			created_utc = thing["timestamp"]

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
