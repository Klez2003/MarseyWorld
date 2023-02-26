from files.classes import *
from files.helpers.alerts import *
from files.helpers.regex import *
from files.helpers.get import *

from files.routes.wrappers import *

from files.__main__ import app, limiter

@app.get("/ping_groups")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def ping_groups(v:User):
	groups = g.db.query(Group).order_by(Group.created_utc).all()
	return render_template('groups.html', v=v, groups=groups, cost=GROUP_COST, msg=get_msg(), error=get_error())

@app.post("/create_group")
@limiter.limit('1/second', scope=rpath)
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@is_not_permabanned
def create_group(v):
	name = request.values.get('name')
	if not name: abort(400)
	name = name.strip().lower()

	if not valid_sub_regex.fullmatch(name):
		return redirect(f"/ping_groups?error=Name does not match the required format!")

	group = g.db.get(Group, name)
	if not group:
		if not v.charge_account('coins', GROUP_COST):
			return redirect(f"/ping_groups?error=You don't have enough coins!")

		g.db.add(v)
		if v.shadowbanned: abort(500)

		group = Group(name=name)
		g.db.add(group)
		g.db.flush()

		group_membership = GroupMembership(
			user_id=v.id,
			group_name=group.name,
			created_utc=time.time(),
			approved_utc=time.time()
			)
		g.db.add(group_membership)

		admins = [x[0] for x in g.db.query(User.id).filter(User.admin_level >= PERMS['NOTIFICATIONS_HOLE_CREATION'], User.id != v.id).all()]
		for admin in admins:
			send_repeatable_notification(admin, f":!marseyparty: !{group} has been created by @{v.username} :marseyparty:")

	return redirect(f'/ping_groups?msg=!{group} created successfully!')

@app.post("/!<group_name>/apply")
@limiter.limit('1/second', scope=rpath)
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def join_group(v:User, group_name):
	group = g.db.get(Group, group_name)
	if not group: abort(404)
	existing = g.db.query(GroupMembership).filter_by(user_id=v.id, group_name=group_name).one_or_none()
	if not existing:
		join = GroupMembership(user_id=v.id, group_name=group_name)
		g.db.add(join)
		send_notification(group.owner.id, f"@{v.username} has applied to join !{group}. You can approve or reject the application [here](/!{group}).")

	return {"message": f"Application submitted to !{group}'s owner (@{group.owner.username}) successfully!"}

@app.post("/!<group_name>/leave")
@limiter.limit('1/second', scope=rpath)
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def leave_group(v:User, group_name):
	group = g.db.get(Group, group_name)
	if not group: abort(404)
	existing = g.db.query(GroupMembership).filter_by(user_id=v.id, group_name=group_name).one_or_none()
	if existing:
		if existing.approved_utc:
			text = f"@{v.username} has left !{group}"
			msg = f"You have left !{group} successfully!"
		else:
			text = f"@{v.username} has cancelled their application to !{group}"
			msg = f"You have cancelled your application to !{group} successfully!"

		send_notification(group.owner.id, text)
		g.db.delete(existing)
		
		return {"message": msg}

	return {"message": ''}


@app.get("/!<group_name>")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def memberships(v:User, group_name):
	group = g.db.get(Group, group_name)
	if not group: abort(404)

	members = g.db.query(GroupMembership).filter(
			GroupMembership.group_name == group_name,
			GroupMembership.approved_utc != None
		).order_by(GroupMembership.approved_utc).all()

	applications = g.db.query(GroupMembership).filter(
			GroupMembership.group_name == group_name,
			GroupMembership.approved_utc == None
		).order_by(GroupMembership.created_utc).all()

	return render_template('group_memberships.html', v=v, group=group, members=members, applications=applications)

@app.post("/!<group_name>/<user_id>/approve")
@limiter.limit('1/second', scope=rpath)
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def group_approve(v:User, group_name, user_id):
	group = g.db.get(Group, group_name)
	if not group: abort(404)
	
	if v.id != group.owner.id:
		abort(403, f"Only the group owner (@{group.owner.username}) can approve applications!")
	
	application = g.db.query(GroupMembership).filter_by(user_id=user_id, group_name=group.name).one_or_none()
	if not application:
		abort(404, "There is no application to approve!")

	if not application.approved_utc:
		application.approved_utc = time.time()
		g.db.add(application)
		send_repeatable_notification(application.user_id, f"@{v.username} (!{group}'s owner) has approved your application!")

	return {"message": f'You have approved @{application.user.username} successfully!'}

@app.post("/!<group_name>/<user_id>/reject")
@limiter.limit('1/second', scope=rpath)
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def group_reject(v:User, group_name, user_id):
	group = g.db.get(Group, group_name)
	if not group: abort(404)
	
	if v.id != group.owner.id:
		abort(403, f"Only the group owner (@{group.owner.username}) can reject memberships!")

	membership = g.db.query(GroupMembership).filter_by(user_id=user_id, group_name=group.name).one_or_none()
	if not membership:
		abort(404, "There is no membership to reject!")

	if membership.approved_utc:
		text = f"@{v.username} (!{group}'s owner) has kicked you from !{group}"
		msg = f"You have kicked @{membership.user.username} successfully!"
	else:
		text = f"@{v.username} (!{group}'s owner) has rejected your application!"
		msg = f"You have rejected @{membership.user.username} successfully!"

	send_repeatable_notification(membership.user_id, text)

	g.db.delete(membership)

	return {"message": msg}
