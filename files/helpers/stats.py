from flask import g
import time
import calendar
import matplotlib.pyplot as plt
from sqlalchemy.sql import func, or_

from files.classes.user import User
from files.classes.post import Post
from files.classes.comment import Comment
from files.classes.votes import Vote, CommentVote
from files.classes.emoji import *
from files.classes.award import AwardRelationship
from files.helpers.config.const import *

def generate_charts_task(site):
	chart(kind='daily', site=site)
	chart(kind='weekly', site=site)

def chart(kind, site):
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

	plt.rcParams['figure.figsize'] = (chart_width, chart_width)

	signup_chart = plt.subplot2grid((chart_width, chart_width), (0, 0), rowspan=6, colspan=chart_width)
	posts_chart = plt.subplot2grid((chart_width, chart_width), (10, 0), rowspan=6, colspan=chart_width)
	comments_chart = plt.subplot2grid((chart_width, chart_width), (20, 0), rowspan=6, colspan=chart_width)

	signup_chart.grid(), posts_chart.grid(), comments_chart.grid()

	signup_chart.plot(daily_times, daily_signups, color='red')
	posts_chart.plot(daily_times, post_stats, color='blue')
	comments_chart.plot(daily_times, comment_stats, color='purple')

	signup_chart.set_ylim(ymin=0)
	posts_chart.set_ylim(ymin=0)
	comments_chart.set_ylim(ymin=0)

	signup_chart.set_xlabel("Signups", labelpad=10.0, size=30)
	posts_chart.set_xlabel("Posts", labelpad=10.0, size=30)
	comments_chart.set_xlabel("Comments", labelpad=10.0, size=30)

	file = chart_path(kind, site)

	plt.savefig(file, bbox_inches='tight')
	plt.clf()
	return file

def chart_path(kind, site):
	return f'/{site}_{kind}.png'

def stats():
	now = time.time()
	day = int(now) - 86400
	week = int(now) - 604800

	stats = {
			"time": int(time.time()),
			"marseys": "{:,}".format(g.db.query(Emoji).filter(Emoji.kind=="Marsey", Emoji.submitter_id==None).count()),
			"total emojis": "{:,}".format(g.db.query(Emoji).filter(Emoji.submitter_id==None).count()),
			"users": "{:,}".format(g.db.query(User).count()),
			"private users": "{:,}".format(g.db.query(User).filter_by(is_private=True).count()),
			"banned users": "{:,}".format(g.db.query(User).filter(User.is_banned != None).count()),
			"verified email users": "{:,}".format(g.db.query(User).filter_by(email_verified=True).count()),
			"coins in circulation": "{:,}".format(g.db.query(func.sum(User.coins)).scalar()),
			"total shop sales": "{:,}".format(g.db.query(func.sum(User.coins_spent)).scalar()),
			"signups last 24h": "{:,}".format(g.db.query(User).filter(User.created_utc > day).count()),
			"total posts": "{:,}".format(g.db.query(Post).count()),
			"posting users": "{:,}".format(g.db.query(Post.author_id).distinct().count()),
			"listed posts": "{:,}".format(g.db.query(Post).filter_by(is_banned=False).filter(Post.deleted_utc == 0).count()),
			"removed posts (by admins)": "{:,}".format(g.db.query(Post).filter_by(is_banned=True).count()),
			"deleted posts (by author)": "{:,}".format(g.db.query(Post).filter(Post.deleted_utc > 0).count()),
			"posts last 24h": "{:,}".format(g.db.query(Post).filter(Post.created_utc > day).count()),
			"total comments": "{:,}".format(g.db.query(Comment).filter(Comment.author_id != AUTOJANNY_ID).count()),
			"commenting users": "{:,}".format(g.db.query(Comment.author_id).distinct().count()),
			"removed comments (by admins)": "{:,}".format(g.db.query(Comment).filter_by(is_banned=True).count()),
			"deleted comments (by author)": "{:,}".format(g.db.query(Comment).filter(Comment.deleted_utc > 0).count()),
			"comments last 24h": "{:,}".format(g.db.query(Comment).filter(Comment.created_utc > day, Comment.author_id != AUTOJANNY_ID).count()),
			"post votes": "{:,}".format(g.db.query(Vote).count()),
			"comment votes": "{:,}".format(g.db.query(CommentVote).count()),
			"total upvotes": "{:,}".format(g.db.query(Vote).filter_by(vote_type=1).count() + g.db.query(CommentVote).filter_by(vote_type=1).count()),
			"total downvotes": "{:,}".format(g.db.query(Vote).filter_by(vote_type=-1).count() + g.db.query(CommentVote).filter_by(vote_type=-1).count()),
			"total awards": "{:,}".format(g.db.query(AwardRelationship).count()),
			"awards given": "{:,}".format(g.db.query(AwardRelationship).filter(or_(AwardRelationship.post_id != None, AwardRelationship.comment_id != None)).count()),
			"users who posted, commented, or voted in the past 7 days": "{:,}".format(g.db.query(User).filter(User.last_active > week).count()),
		}

	if FEATURES['HOUSES']:
		stats2 = {
			"House Furry members": "{:,}".format(g.db.query(User).filter(User.house.like('Furry%')).count()),
			"House Femboy members": "{:,}".format(g.db.query(User).filter(User.house.like('Femboy%')).count()),
			"House Vampire members": "{:,}".format(g.db.query(User).filter(User.house.like('Vampire%')).count()),
			"House Racist members": "{:,}".format(g.db.query(User).filter(User.house.like('Racist%')).count()),
			"House Edgy members": "{:,}".format(g.db.query(User).filter(User.house.like('Edgy%')).count()),
			"House Furry total truescore": "{:,}".format(g.db.query(func.sum(User.truescore)).filter(User.house.like('Furry%')).scalar() or 0),
			"House Femboy total truescore": "{:,}".format(g.db.query(func.sum(User.truescore)).filter(User.house.like('Femboy%')).scalar() or 0),
			"House Vampire total truescore": "{:,}".format(g.db.query(func.sum(User.truescore)).filter(User.house.like('Vampire%')).scalar() or 0),
			"House Racist total truescore": "{:,}".format(g.db.query(func.sum(User.truescore)).filter(User.house.like('Racist%')).scalar() or 0),
			"House Edgy total truescore": "{:,}".format(g.db.query(func.sum(User.truescore)).filter(User.house.like('Edgy%')).scalar() or 0),
			}
		stats.update(stats2)

	return stats
