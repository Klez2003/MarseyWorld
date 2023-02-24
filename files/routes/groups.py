from files.classes import *
from files.helpers.alerts import *
from files.helpers.regex import *
from files.helpers.get import *

from files.routes.wrappers import *

from files.__main__ import app, limiter

@app.get("/ping_groups")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def ping_groups(v:User):
	groups = g.db.query(Group).order_by(Group.created_utc).all()
	return render_template('groups.html', v=v, groups=groups, cost=GROUP_COST, msg=get_msg(), error=get_error())

@app.post("/create_group")
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

@app.post("/!<group_name>/join")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def join_group(v:User, group_name):
	group = g.db.get(Group, group_name)
	if not group: abort(404)
	existing = g.db.query(GroupMembership).filter_by(user_id=v.id, group_name=group_name).one_or_none()
	if not existing:
		join = GroupMembership(user_id=v.id, group_name=group_name)
		g.db.add(join)
		send_repeatable_notification(group.owner.id, f"@{v.username} has applied to join !{group}. You can approve or reject the application [here](/!{group}/applications).")

	return redirect(f"/ping_groups?msg=Application submitted to !{group}'s owner (@{group.owner.username}) successfully!")

@app.get("/!<group_name>/applications")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def applications(v:User, group_name):
	group = g.db.get(Group, group_name)
	if not group: abort(404)
	applications = g.db.query(GroupMembership).filter_by(group_name=group_name, approved_utc=None).order_by(GroupMembership.created_utc.desc()).all()
	return render_template('group_applications.html', v=v, group=group, applications=applications, msg=get_msg())

@app.post("/!<group_name>/<user_id>/approve")
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

	return redirect(f'/!{group}/applications?msg=@{application.user.username} has been approved successfully!')

@app.post("/!<group_name>/<user_id>/reject")
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def group_reject(v:User, group_name, user_id):
	group = g.db.get(Group, group_name)
	if not group: abort(404)
	
	if v.id != group.owner.id:
		abort(403, f"Only the group owner (@{group.owner.username}) can reject applications!")
	
	application = g.db.query(GroupMembership).filter_by(user_id=user_id, group_name=group.name).one_or_none()
	if not application:
		abort(404, "There is no application to reject!")

	g.db.delete(application)
	send_repeatable_notification(application.user_id, f"@{v.username} (!{group}'s owner) has rejected your application!")

	return redirect(f'/!{group}/applications?msg=@{application.user.username} has been rejected successfully!')
