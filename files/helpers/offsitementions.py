import time
import itertools

import requests
from flask_caching import Cache
from flask import g
from sqlalchemy import or_

import files.helpers.config.const as const
from files.classes.badges import Badge
from files.classes.comment import Comment
from files.classes.user import User
from files.helpers.sanitize import *
from files.helpers.alerts import push_notif
from files.classes.notifications import Notification

# Note: while https://api.pushshift.io/meta provides the key
# server_ratelimit_per_minute, in practice Cloudflare puts stricter,
# unofficially documented limits at around 60/minute. We get nowhere near this
# with current keyword quantities. If this ever changes, consider reading the
# value from /meta (or just guessing) and doing a random selection of keywords.

def offsite_mentions_task(cache):
	site_mentions = get_mentions(cache, const.REDDIT_NOTIFS_SITE)
	notify_mentions(site_mentions)

	if const.REDDIT_NOTIFS_USERS:
		for query, send_user in const.REDDIT_NOTIFS_USERS.items():
			user_mentions = get_mentions(cache, [query], reddit_notifs_users=True)
			notify_mentions(user_mentions, send_to=send_user, mention_str='mention of you')

def get_mentions(cache, queries, reddit_notifs_users=False):
	mentions = []
	for kind in ('submission', 'comment'):
		q = " or ".join(queries)
		url = f'https://api.pullpush.io/reddit/search/{kind}?q={q}'
		try: req = requests.get(url, headers=HEADERS, timeout=5, proxies=proxies)
		except: return []
		data = req.json()['data']

		for thing in data:
			if not thing.get('permalink'):
				continue

			if thing['subreddit'] in {'IAmA', 'PokemonGoRaids', 'SubSimulatorGPT2', 'SubSimGPT2Interactive'}: continue
			if 'bot' in thing['author'].lower(): continue
			if 'AutoModerator' == thing['author']: continue
			if kind == 'comment':
				body = thing["body"].replace('>', '> ')
				text = f'<blockquote><p>{body}</p></blockquote>'
			else:
				title = thing["title"].replace('>', '> ')

				# Special case: a spambot says 'WPD' a lot unrelated to us.
				if 'Kathrine Mclaurin' in title: continue
				text = f'<blockquote><p>{title}</p></blockquote>'

				if thing["selftext"]:
					selftext = thing["selftext"].replace('>', '> ')[:5000]
					text += f'<br><blockquote><p>{selftext}</p></blockquote>'
			mentions.append({
				'permalink': thing['permalink'],
				'author': thing['author'],
				'created_utc': thing['created_utc'],
				'text': text,
			})
	return mentions

def notify_mentions(mentions, send_to=None, mention_str='site mention'):
	mentions = sorted(mentions, key=lambda x: int(x['created_utc']), reverse=True)
	for m in mentions:
		author = m['author']
		permalink = m['permalink']
		text = sanitize(m['text'], blackjack="reddit mention", golden=False)
		notif_text = (
			f'<p>New {mention_str} by <a href="https://old.reddit.com/u/{author}" '
				f'rel="nofollow noopener" target="_blank">/u/{author}</a></p>'
			f'<p><a href="https://old.reddit.com{permalink}?context=89" '
				'rel="nofollow noopener" target="_blank">'
				f'https://old.reddit.com{permalink}?context=89</a></p>'
			f'{text}'
		)

		g.db.flush()
		existing_comment = g.db.query(Comment.id).filter_by(
			author_id=const.AUTOJANNY_ID,
			parent_post=None,
			body_html=notif_text).one_or_none()
		if existing_comment: break

		new_comment = Comment(
							author_id=const.AUTOJANNY_ID,
							parent_post=None,
							body_html=notif_text,
							distinguish_level=6,
							created_utc=int(m['created_utc']),
						)
		g.db.add(new_comment)
		g.db.flush()
		new_comment.top_comment_id = new_comment.id

		if send_to:
			notif = Notification(comment_id=new_comment.id, user_id=send_to)
			g.db.add(notif)

			push_notif({send_to}, f'New mention of you on reddit by /u/{author}', '', f'{SITE_FULL}/notification/{new_comment.id}')
