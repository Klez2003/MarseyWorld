import time

from sqlalchemy.sql import func
from sqlalchemy.sql.sqltypes import *
from flask import g

from files.helpers.config.const import *

from files.classes.subscriptions import Subscription
from files.classes.saves import *

def apply_time_filter(t, objects, cls):
	now = int(time.time())

	if t == 'hour':
		cutoff = now - 3600
	elif t == 'day':
		cutoff = now - 86400
	elif t == 'week':
		cutoff = now - 604800
	elif t == 'month':
		cutoff = now - 2592000
	elif t == 'year':
		cutoff = now - 31536000
	else:
		return objects

	return objects.filter(cls.created_utc >= cutoff)


def sort_objects(sort, objects, cls):
	if sort == 'hot':
		if not (SITE == 'watchpeopledie.tv' and g.v and g.v.id == GTIX_ID):
			objects = objects.order_by(func.cast(cls.is_banned, Boolean), func.cast(cls.deleted_utc, Boolean))

		ti = int(time.time()) + 3600
		metric = cls.realupvotes + 1
		if cls.__name__ == "Post":
			metric += cls.comment_count/5
			churn_rate = 1.4
		else:
			if SITE_NAME == 'rDrama': churn_rate = 1.7
			else: churn_rate = 1.3
		return objects.order_by(-1000000*(metric / func.power(((ti - cls.created_utc)/1000), churn_rate)), cls.created_utc.desc())
	elif sort == "views" and cls.__name__ == "Post":
		return objects.order_by(cls.views.desc(), cls.created_utc.desc())
	elif sort == "bump" and cls.__name__ == "Post":
		return objects.filter(cls.comment_count > 1).order_by(cls.bump_utc.desc(), cls.created_utc.desc())
	elif sort == "comments" and cls.__name__ == "Post":
		return objects.order_by(cls.comment_count.desc(), cls.created_utc.desc())
	elif sort == "subscriptions" and cls.__name__ == "Post":
		return objects.outerjoin(Subscription, Subscription.post_id == cls.id).group_by(cls.id).order_by(func.count(Subscription.post_id).desc(), cls.created_utc.desc())
	elif sort == "saves" and cls.__name__ == "Post":
		return objects.outerjoin(SaveRelationship, SaveRelationship.post_id == cls.id).group_by(cls.id).order_by(func.count(SaveRelationship.post_id).desc(), cls.created_utc.desc())
	elif sort == "saves" and cls.__name__ == "Comment":
		return objects.outerjoin(CommentSaveRelationship, CommentSaveRelationship.comment_id == cls.id).group_by(cls.id).order_by(func.count(CommentSaveRelationship.comment_id).desc(), cls.created_utc.desc())
	elif sort == "new":
		return objects.order_by(cls.created_utc.desc())
	elif sort == "old":
		return objects.order_by(cls.created_utc)
	elif sort == "controversial" and cls.__name__ == "Post":
		return objects.order_by((cls.upvotes+1)/(cls.downvotes+1) + (cls.downvotes+1)/(cls.upvotes+1) - cls.comment_count/500, cls.downvotes.desc(), cls.created_utc.desc())
	elif sort == "controversial":
		return objects.order_by((cls.upvotes+1)/(cls.downvotes+1) + (cls.downvotes+1)/(cls.upvotes+1) - cls.downvotes/10, cls.downvotes.desc(), cls.created_utc.desc())
	elif sort == "bottom":
		return objects.order_by(cls.upvotes - cls.downvotes, cls.created_utc.desc())
	elif sort == "random":
		return objects.order_by(func.random())
	else:
		return objects.order_by(cls.downvotes - cls.upvotes, cls.created_utc.desc())

def make_age_string(compare):
	if not compare or compare < 1577865600: return ""
	age = int(time.time()) - compare

	if age < 60:
		return "just now"
	elif age < 3600:
		minutes = int(age / 60)
		return f"{minutes}m ago"
	elif age < 86400:
		hours = int(age / 3600)
		return f"{hours}hr ago"
	elif age < 2678400:
		days = int(age / 86400)
		return f"{days}d ago"

	now = time.gmtime()
	ctd = time.gmtime(compare)
	months = now.tm_mon - ctd.tm_mon + 12 * (now.tm_year - ctd.tm_year)
	if now.tm_mday < ctd.tm_mday:
		months -= 1
	if months < 12:
		return f"{months}mo ago"
	else:
		years = int(months / 12)
		return f"{years}yr ago"
