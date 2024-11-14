import time
import uuid
import random

from sqlalchemy.orm import aliased, deferred
from sqlalchemy.sql import case, literal, func
from sqlalchemy.sql.expression import or_

from flask import g, session

from files.classes import Alt, Comment, User, Post
from files.helpers.config.const import *
from files.helpers.security import generate_hash, validate_hash
from files.__main__ import cache

def check_session_id():
	if not session.get("session_id"):
		session.permanent = True
		session["session_id"] = str(uuid.uuid4())

def get_raw_formkey(u):
	check_session_id()
	return f"{session['session_id']}+{u.id}+{u.login_nonce}"

def get_formkey(u):
	if not u: return "" # if no user exists, give them a blank formkey
	return generate_hash(get_raw_formkey(u))

def validate_formkey(u, formkey):
	if not formkey: return False
	return validate_hash(get_raw_formkey(u), formkey)

@cache.memoize(timeout=86400)
def get_alt_graph_ids(uid):
	if SITE_NAME == 'WPD':
		alts = g.db.query(Alt.user1).filter_by(user2=uid).all() + g.db.query(Alt.user2).filter_by(user1=uid).all()
		return {x[0] for x in alts}

	alt_graph_cte = g.db.query(literal(uid).label('user_id')).select_from(Alt).cte('alt_graph', recursive=True)

	alt_graph_cte_inner = g.db.query(
		case(
			(Alt.user1 == alt_graph_cte.c.user_id, Alt.user2),
			(Alt.user2 == alt_graph_cte.c.user_id, Alt.user1),
		)
	).select_from(Alt, alt_graph_cte).filter(
		or_(alt_graph_cte.c.user_id == Alt.user1, alt_graph_cte.c.user_id == Alt.user2)
	)

	alt_graph_cte = alt_graph_cte.union(alt_graph_cte_inner)
	return {x[0] for x in g.db.query(User.id).filter(User.id == alt_graph_cte.c.user_id, User.id != uid)}

def get_alt_graph(uid):
	alt_ids = get_alt_graph_ids(uid)
	return g.db.query(User).filter(User.id.in_(alt_ids)).order_by(func.lower(User.username)).all()

def add_alt(user1, user2):
	if user1 in {1375580,14713} or user2 in {1375580,14713}:
		session.pop("history", None)

	if session.get("GLOBAL"):
		return

	li = [user1, user2]

	if AEVANN_ID in li:
		return

	g.db.flush()
	if user1 not in get_alt_graph_ids(user2):
		users_exist = (g.db.query(User).filter(User.id.in_(li)).count() == 2)
		if not users_exist:
			session.pop("history", None)
			return
		new_alt = Alt(user1=user1, user2=user2)
		g.db.add(new_alt)
		g.db.flush()
		cache.delete_memoized(get_alt_graph_ids, user1)
		cache.delete_memoized(get_alt_graph_ids, user2)

def check_for_alts(current, include_current_session=False):
	if session.get("GLOBAL"):
		return

	past_accs = set(session.get("history", [])) if include_current_session else set()

	if current.email and current.email_verified:
		more_ids = [x[0] for x in g.db.query(User.id).filter(
			User.email == current.email,
			User.email_verified == True,
			User.id != current.id,
		).all()]
		past_accs.update(more_ids)

	for past_id in list(past_accs):
		if past_id == current.id: continue

		li = [past_id, current.id]
		add_alt(past_id, current.id)
		other_alts = g.db.query(Alt).filter(Alt.user1.in_(li), Alt.user2.in_(li)).all()
		for a in other_alts:
			if a.user1 != past_id: add_alt(a.user1, past_id)
			if a.user1 != current.id: add_alt(a.user1, current.id)
			if a.user2 != past_id: add_alt(a.user2, past_id)
			if a.user2 != current.id: add_alt(a.user2, current.id)

	past_accs.add(current.id)
	if include_current_session:
		session["history"] = list(past_accs)
	g.db.flush()
	for u in get_alt_graph(current.id):
		if u.shadowbanned and not current.shadowbanned:
			current.shadowbanned = u.shadowbanned
			current.shadowban_reason = u.shadowban_reason
			g.db.add(current)
		elif current.shadowbanned and not u.shadowbanned:
			u.shadowbanned = current.shadowbanned
			u.shadowban_reason = current.shadowban_reason
			g.db.add(u)
		elif u.is_permabanned and not current.is_permabanned:
			current.is_banned = u.is_banned
			current.ban_reason = u.ban_reason
			current.unban_utc = None
			g.db.add(current)
		elif current.is_permabanned and not u.is_permabanned:
			u.is_banned = current.is_banned
			u.ban_reason = current.ban_reason
			u.unban_utc = None
			g.db.add(u)
		elif u.is_underage and not current.is_underage:
			current.is_banned = u.is_banned
			current.ban_reason = u.ban_reason
			current.unban_utc = u.unban_utc
			g.db.add(current)
		elif current.is_underage and not u.is_underage:
			u.is_banned = current.is_banned
			u.ban_reason = current.ban_reason
			u.unban_utc = current.unban_utc
			g.db.add(u)

		if u.is_muted and not current.is_muted:
			current.is_muted = u.is_muted
			g.db.add(current)
		elif current.is_muted and not u.is_muted:
			u.is_muted = current.is_muted
			g.db.add(u)

		if u.blacklisted_by and not current.blacklisted_by:
			current.blacklisted_by = u.blacklisted_by
			g.db.add(current)
		elif current.blacklisted_by and not u.blacklisted_by:
			u.blacklisted_by = current.blacklisted_by
			g.db.add(u)

def execute_shadowban_viewers_and_voters(v, target):
	if not v or not v.shadowbanned: return
	if not target: return
	if v.id != target.author_id: return
	if not (86400 > time.time() - target.created_utc > 20):
		return

	ti = max(int((time.time() - target.created_utc)/60), 3)
	max_upvotes = min(ti, 13)
	rand = random.randint(0, max_upvotes)
	if target.upvotes >= rand: return

	amount = random.randint(0, 3)

	target.upvotes += amount
	if isinstance(target, Post):
		target.views += amount*random.randint(3, 5)
	g.db.add(target)
