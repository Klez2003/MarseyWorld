from flask import g
import time
import calendar
import matplotlib.pyplot as plt
from sqlalchemy.sql import func, or_

from files.classes.user import User
from files.classes.post import Post
from files.classes.comment import Comment
from files.classes.votes import Vote, CommentVote
from files.classes.chats import ChatMessage
from files.classes.emoji import *
from files.classes.award import AwardRelationship
from files.helpers.config.const import *

def chart(kind):
	now = time.gmtime()
	midnight_this_morning = time.struct_time((
		now.tm_year, now.tm_mon, now.tm_mday,
		0, 0, 0,
		now.tm_wday, now.tm_yday, 0))
	today_cutoff = calendar.timegm(midnight_this_morning)

	num_of_weeks = 30

	chart_width = int(num_of_weeks/0.7)

	if kind == 'daily':
		day_cutoffs = [today_cutoff - 86400 * i for i in range(num_of_weeks)][1:]
	else:
		day_cutoffs = [today_cutoff - 86400 * 7 * i for i in range(num_of_weeks)][1:]
	day_cutoffs.insert(0, calendar.timegm(now))

	daily_times = [time.strftime('%Y-%m-%d', time.gmtime(day_cutoffs[i + 1]))
		for i in range(len(day_cutoffs) - 1)][::-1]

	daily_signups = [g.db.query(User).filter(
			User.created_utc < day_cutoffs[i],
			User.created_utc > day_cutoffs[i + 1]).count()
		for i in range(len(day_cutoffs) - 1)][::-1]

	post_stats = [g.db.query(Post).filter(
			Post.created_utc < day_cutoffs[i],
			Post.created_utc > day_cutoffs[i + 1],
			Post.is_banned == False).count()
		for i in range(len(day_cutoffs) - 1)][::-1]

	comment_stats = [g.db.query(Comment).filter(
			Comment.created_utc < day_cutoffs[i],
			Comment.created_utc > day_cutoffs[i + 1],
			Comment.is_banned == False,
			Comment.author_id != AUTOJANNY_ID).count()
		for i in range(len(day_cutoffs) - 1)][::-1]

	vote_stats = [
		g.db.query(Vote).filter(
			Vote.created_utc < day_cutoffs[i],
			Vote.created_utc > day_cutoffs[i + 1]
		).count() +
		g.db.query(CommentVote).filter(
			CommentVote.created_utc < day_cutoffs[i],
			CommentVote.created_utc > day_cutoffs[i + 1]
		).count()
		for i in range(len(day_cutoffs) - 1)][::-1]

	chat_stats = [g.db.query(ChatMessage).filter(
			ChatMessage.created_utc < day_cutoffs[i],
			ChatMessage.created_utc > day_cutoffs[i + 1]).count()
		for i in range(len(day_cutoffs) - 1)][::-1]

	plt.rcParams['figure.figsize'] = (chart_width, chart_width)

	signup_chart = plt.subplot2grid((chart_width, chart_width), (0, 0), rowspan=6, colspan=chart_width)
	posts_chart = plt.subplot2grid((chart_width, chart_width), (10, 0), rowspan=6, colspan=chart_width)
	comments_chart = plt.subplot2grid((chart_width, chart_width), (20, 0), rowspan=6, colspan=chart_width)
	votes_chart = plt.subplot2grid((chart_width, chart_width), (30, 0), rowspan=6, colspan=chart_width)
	chat_chart = plt.subplot2grid((chart_width, chart_width), (40, 0), rowspan=6, colspan=chart_width)

	signup_chart.plot(daily_times, daily_signups, color='red')
	posts_chart.plot(daily_times, post_stats, color='blue')
	comments_chart.plot(daily_times, comment_stats, color='purple')
	votes_chart.plot(daily_times, vote_stats, color='green')
	chat_chart.plot(daily_times, chat_stats, color='teal')

	signup_chart.set_ylim(ymin=0)
	posts_chart.set_ylim(ymin=0)
	comments_chart.set_ylim(ymin=0)
	votes_chart.set_ylim(ymin=0)
	chat_chart.set_ylim(ymin=0)

	signup_chart.set_xlabel("Signups", labelpad=10.0, size=30)
	posts_chart.set_xlabel("Posts", labelpad=10.0, size=30)
	comments_chart.set_xlabel("Comments", labelpad=10.0, size=30)
	votes_chart.set_xlabel("Votes", labelpad=10.0, size=30)
	chat_chart.set_xlabel("Chat Messages", labelpad=10.0, size=30)

	file = f'/images/{kind}_chart.png'

	plt.savefig(file, bbox_inches='tight')
	plt.clf()
	return file

def stats():
	now = time.time()
	day = int(now) - 86400
	week = int(now) - 604800

	stats = {
			"Time these stats were collected": int(time.time()),
			"Marseys": "{:,}".format(g.db.query(Emoji).filter(Emoji.kind=="Marsey", Emoji.submitter_id==None).count()),
			"Total emojis": "{:,}".format(g.db.query(Emoji).filter(Emoji.submitter_id==None).count()),
			"Users": "{:,}".format(g.db.query(User).count()),
			"Banned users": "{:,}".format(g.db.query(User).filter(User.is_banned != None).count()),
			"Users with a private profile": "{:,}".format(g.db.query(User).filter_by(is_private=True).count()),
			"Users with a verified email": "{:,}".format(g.db.query(User).filter_by(email_verified=True).count()),
			"Currency in circulation": "{:,}".format(g.db.query(func.sum(User.coins + User.marseybux)).scalar()),
			"Total currency spent on awards": "{:,}".format(g.db.query(func.sum(User.currency_spent_on_awards)).scalar()),
			"Total currency spent on hats": "{:,}".format(g.db.query(func.sum(User.currency_spent_on_hats)).scalar()),
			"Signups last 24h": "{:,}".format(g.db.query(User).filter(User.created_utc > day).count()),
			"Total posts": "{:,}".format(g.db.query(Post).count()),
			"Posting users": "{:,}".format(g.db.query(Post.author_id).distinct().count()),
			"Listed posts": "{:,}".format(g.db.query(Post).filter_by(is_banned=False, deleted_utc=0).count()),
			"Removed posts (by admins)": "{:,}".format(g.db.query(Post).filter_by(is_banned=True).count()),
			"Deleted posts (by author)": "{:,}".format(g.db.query(Post).filter(Post.deleted_utc > 0).count()),
			"Posts last 24h": "{:,}".format(g.db.query(Post).filter(Post.created_utc > day).count()),
			"Total comments": "{:,}".format(g.db.query(Comment).filter(Comment.author_id != AUTOJANNY_ID).count()),
			"Commenting users": "{:,}".format(g.db.query(Comment.author_id).distinct().count()),
			"Removed comments (by admins)": "{:,}".format(g.db.query(Comment).filter_by(is_banned=True).count()),
			"Deleted comments (by author)": "{:,}".format(g.db.query(Comment).filter(Comment.deleted_utc > 0).count()),
			"Comments last 24h": "{:,}".format(g.db.query(Comment).filter(Comment.created_utc > day, Comment.author_id != AUTOJANNY_ID).count()),
			"Post votes": "{:,}".format(g.db.query(Vote).count()),
			"Comment votes": "{:,}".format(g.db.query(CommentVote).count()),
			"Total upvotes": "{:,}".format(g.db.query(Vote).filter_by(vote_type=1).count() + g.db.query(CommentVote).filter_by(vote_type=1).count()),
			"Total downvotes": "{:,}".format(g.db.query(Vote).filter_by(vote_type=-1).count() + g.db.query(CommentVote).filter_by(vote_type=-1).count()),
			"Total awards": "{:,}".format(g.db.query(AwardRelationship).count()),
			"Awards given": "{:,}".format(g.db.query(AwardRelationship).filter(or_(AwardRelationship.post_id != None, AwardRelationship.comment_id != None)).count()),
			"Users who posted, commented, or voted in the past 7 days": "{:,}".format(g.db.query(User).filter(User.last_active > week).count()),
		}

	if FEATURES['HOUSES']:
		for house in HOUSES:
			stats[f"House {house} members"] = "{:,}".format(g.db.query(User).filter(User.house.like(f'{house}%')).count())
		for house in HOUSES:
			stats[f"House {house} total truescore"] = "{:,}".format(g.db.query(func.sum(User.truescore)).filter(User.house.like(f'{house}%')).scalar() or 0)

	return stats
