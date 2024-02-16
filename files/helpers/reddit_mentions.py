import requests
from flask import g

from files.helpers.config.const import *
from files.classes.comment import Comment
from files.helpers.sanitize import *
from files.helpers.alerts import push_notif
from files.classes.notifications import Notification

def reddit_mentions_task():
	site_mentions = get_mentions(OFFSITE_NOTIF_QUERIES)
	notify_mentions(site_mentions)

	if REDDIT_NOTIFS_USERS:
		for query, send_user in REDDIT_NOTIFS_USERS.items():
			user_mentions = get_mentions(cache, [query], reddit_notifs_users=True)
			if user_mentions:
				notify_mentions(user_mentions, send_to=send_user, mention_str='mention of you')

def get_mentions(queries, reddit_notifs_users=False):
	mentions = []
	for kind in ('submission', 'comment'):
		q = " or ".join(queries)
		url = f'https://api.pullpush.io/reddit/search/{kind}?q={q}'
		try: data = requests.get(url, headers=HEADERS, timeout=5).json()['data']
		except: return []

		for thing in data:
			if not thing.get('permalink'):
				continue

			if thing.get('subreddit_subscribers') and thing['subreddit_subscribers'] < 2: continue
			if thing.get('subreddit_type') == 'user': continue
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
		text = (
			f'<p>New {mention_str} by <a href="https://old.reddit.com/user/{author}" '
				f'rel="nofollow noopener" target="_blank">/u/{author}</a></p>'
			f'<p><a href="https://old.reddit.com{permalink}?context=89" '
				'rel="nofollow noopener" target="_blank">'
				f'https://old.reddit.com{permalink}?context=89</a></p>'
			f'{m["text"]}'
		)

		text = sanitize(text, blackjack="reddit mention", golden=False)

		g.db.flush()
		try:
			existing_comment = g.db.query(Comment.id).filter_by(
				author_id=AUTOJANNY_ID,
				parent_post=None,
				body_html=text).one_or_none()
			if existing_comment: break
		except:
			pass

		new_comment = Comment(
							author_id=AUTOJANNY_ID,
							parent_post=None,
							body_html=text,
							distinguished=True,
							created_utc=int(m['created_utc']),
						)
		g.db.add(new_comment)
		g.db.flush()
		new_comment.top_comment_id = new_comment.id

		if send_to:
			notif = Notification(comment_id=new_comment.id, user_id=send_to)
			g.db.add(notif)

			push_notif({send_to}, f'New mention of you on reddit by /u/{author}', '', f'{SITE_FULL}/notification/{new_comment.id}')
