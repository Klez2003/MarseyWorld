from files.classes import *
from files.helpers.alerts import *
from files.helpers.regex import *
from files.helpers.get import *

from files.routes.wrappers import *

from files.__main__ import app, limiter

@app.get("/ping_groups")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def ping_groups(v):
	groups = g.db.query(Group).order_by(Group.created_utc).all()
	return render_template('groups.html', v=v, groups=groups, cost=GROUP_COST)

@app.post("/create_group")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def create_group(v):
	name = request.values.get('name')
	if not name: abort(400)
	name = name.strip().lower()

	if name.startswith('slots') or name.startswith('remindme'):
		abort(400, "You can't make a group with that name!")

	if not hole_group_name_regex.fullmatch(name):
		abort(400, "Name does not match the required format!")

	if name in {'everyone', 'jannies', 'holejannies', 'followers', 'commenters'} or g.db.get(Group, name):
		abort(400, "This group already exists!")

	if not v.charge_account('coins/marseybux', GROUP_COST)[0]:
		abort(403, "You don't have enough coins or marseybux!")

	g.db.add(v)
	if v.shadowbanned: abort(500)

	group = Group(
			name=name,
			owner_id=v.id,
		)
	g.db.add(group)

	group_membership = GroupMembership(
		user_id=v.id,
		group_name=group.name,
		created_utc=time.time(),
		approved_utc=time.time()
		)
	g.db.add(group_membership)

	g.db.flush() #Necessary, to make linkfying the ping group in the notification work

	text = f":!marseyparty: !{group} has been created by @{v.username} :marseyparty:"
	alert_active_users(text, v.id, User.group_creation_notifs == True)

	return {"message": f"!{group} created successfully!"}

@app.post("/!<group_name>/apply")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def join_group(v, group_name):
	group_name = group_name.strip().lower()

	if group_name == 'verifiedrich':
		if not v.patron:
			abort(403, f"Only {patron}s can join !verifiedrich")

		join = GroupMembership(
				user_id=v.id,
				group_name=group_name,
				approved_utc = time.time()
			)
		g.db.add(join)
		return {"message": "You have joined !verifiedrich successfully!"}

	group = g.db.get(Group, group_name)
	if not group: abort(404)

	existing = g.db.query(GroupMembership).filter_by(user_id=v.id, group_name=group_name).one_or_none()
	if not existing:
		join = GroupMembership(user_id=v.id, group_name=group_name)
		g.db.add(join)

		notified_ids = [group.owner_id]
		notified_ids += [x[0] for x in g.db.query(GroupMembership.user_id).filter_by(group_name=group_name, is_mod=True).all()]
		notified_ids = list(set(notified_ids))

		for uid in notified_ids:
			send_notification(uid, f"@{v.username} has applied to join !{group}. You can approve or reject the application [here](/!{group}).")

	return {"message": f"Application submitted to !{group}'s owner (@{group.owner.username}) successfully!"}

@app.post("/!<group_name>/leave")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leave_group(v, group_name):
	group_name = group_name.strip().lower()

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

		send_notification(group.owner_id, text)
		g.db.delete(existing)

		return {"message": msg}

	return {"message": ''}


@app.get("/!<group_name>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def memberships(v, group_name):
	group_name = group_name.strip().lower()

	group = g.db.get(Group, group_name)
	if not group: abort(404)

	members = \
		[g.db.query(GroupMembership).filter(
			GroupMembership.group_name == group_name,
			GroupMembership.approved_utc != None,
			GroupMembership.user_id == group.owner_id,
		).one()] + \
		g.db.query(GroupMembership).filter(
			GroupMembership.group_name == group_name,
			GroupMembership.approved_utc != None,
			GroupMembership.user_id != group.owner_id,
		).order_by(GroupMembership.is_mod.desc(), GroupMembership.approved_utc).all()

	applications = g.db.query(GroupMembership).filter(
			GroupMembership.group_name == group_name,
			GroupMembership.approved_utc == None
		).order_by(GroupMembership.created_utc).all()

	return render_template('group_memberships.html', v=v, group=group, members=members, applications=applications)

@app.post("/!<group_name>/<user_id>/approve")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def group_approve(v, group_name, user_id):
	group_name = group_name.strip().lower()

	group = g.db.get(Group, group_name)
	if not group: abort(404)

	if not v.mods_group(group):
		abort(403, f"Only the group owner and its mods can approve applications!")

	application = g.db.query(GroupMembership).filter_by(user_id=user_id, group_name=group.name).one_or_none()
	if not application:
		abort(404, "There is no application to approve!")

	if not application.approved_utc:
		application.approved_utc = time.time()
		g.db.add(application)
		if v.id != application.user_id:
			send_repeatable_notification(application.user_id, f"@{v.username} (!{group}'s owner) has approved your application!")

	return {"message": f'You have approved @{application.user.username} successfully!'}

@app.post("/!<group_name>/<user_id>/reject")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def group_reject(v, group_name, user_id):
	group_name = group_name.strip().lower()

	group = g.db.get(Group, group_name)
	if not group: abort(404)

	if not v.mods_group(group):
		abort(403, f"Only the group owner and its mods can reject memberships!")

	membership = g.db.query(GroupMembership).filter_by(user_id=user_id, group_name=group.name).one_or_none()
	if not membership:
		abort(404, "There is no membership to reject!")

	if v.id != membership.user_id: #implies kicking and not leaving
		if membership.user_id == group.owner_id:
			abort(403, "You can't kick the group owner!")

		if v.id != group.owner_id and membership.is_mod:
			abort(403, "Only the group owner can kick mods!")

	if v.id == membership.user_id:
		msg = f"You have left !{group} successfully!"

		if v.id == group.owner_id:
			new_owner_id = g.db.query(GroupMembership.user_id).filter(
				GroupMembership.user_id != v.id,
				GroupMembership.group_name == group.name,
				GroupMembership.approved_utc != None,
			).order_by(GroupMembership.is_mod.desc(), GroupMembership.approved_utc).first()[0]

			if new_owner_id:
				send_repeatable_notification(new_owner_id, f"@{v.username} (!{group}'s owner) has left the group, You're now the new owner!")
				group.owner_id = new_owner_id
				g.db.add(group)
	else:
		if membership.approved_utc:
			text = f"@{v.username} (!{group}'s owner) has kicked you from the group!"
			msg = f"You have kicked @{membership.user.username} successfully!"
		else:
			text = f"@{v.username} (!{group}'s owner) has rejected your application!"
			msg = f"You have rejected @{membership.user.username} successfully!"
		send_repeatable_notification(membership.user_id, text)

	g.db.delete(membership)

	g.db.flush()
	count = g.db.query(GroupMembership).filter_by(group_name=group.name).count()
	if not count:
		g.db.commit() #need it to fix "Dependency rule tried to blank-out primary key column 'group_memberships.group_name' on instance"
		g.db.delete(group)

	return {"message": msg}

@app.post("/!<group_name>/<user_id>/add_mod")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def group_add_mod(v, group_name, user_id):
	group_name = group_name.strip().lower()

	group = g.db.get(Group, group_name)
	if not group: abort(404)

	if v.id != group.owner_id:
		abort(403, f"Only the group owner (@{group.owner.username}) can add mods!")

	membership = g.db.query(GroupMembership).filter_by(user_id=user_id, group_name=group.name).one_or_none()
	if not membership:
		abort(404, "The user is not a member of the group!")

	membership.is_mod = True
	g.db.add(membership)

	send_repeatable_notification(membership.user_id, f"@{v.username} (!{group}'s owner) has added you as a mod!")

	return {"message": f'You have added @{membership.user.username} as a mod successfully!'}

@app.post("/!<group_name>/<user_id>/remove_mod")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def group_remove_mod(v, group_name, user_id):
	group_name = group_name.strip().lower()

	group = g.db.get(Group, group_name)
	if not group: abort(404)

	if v.id != group.owner_id:
		abort(403, f"Only the group owner (@{group.owner.username}) can remove mods!")

	membership = g.db.query(GroupMembership).filter_by(user_id=user_id, group_name=group.name).one_or_none()
	if not membership:
		abort(404, "The user is not a member of the group!")

	membership.is_mod = False
	g.db.add(membership)

	send_repeatable_notification(membership.user_id, f"@{v.username} (!{group}'s owner) has removed you as a mod!")

	return {"message": f'You have removed @{membership.user.username} as a mod successfully!'}


@app.post("/!<group_name>/usurp")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def group_usurp(v, group_name):
	group_name = group_name.strip().lower()

	group = g.db.get(Group, group_name)
	if not group: abort(404)

	if v.mods_group(group):
		abort(403, f"You're a mod of /h/{group.name} can't usurp it!")

	if not v.is_member_of_group(group):
		abort(403, "Only members of groups can usurp them!")

	one_month_ago = time.time() - 2592000

	less_than_month_old_memberships = g.db.query(GroupMembership.user_id).filter(
		GroupMembership.group_name == group.name,
		GroupMembership.approved_utc > one_month_ago,
	).first()

	month_old_applications = g.db.query(GroupMembership.user_id).filter(
		GroupMembership.group_name == group.name,
		GroupMembership.approved_utc == None,
		GroupMembership.created_utc < one_month_ago,
	).first()

	if less_than_month_old_memberships or not month_old_applications:
		abort(403, "The current regime has reviewed a membership application in the past month, so you can't usurp them!")

	send_repeatable_notification(group.owner_id, f"@{v.username} has usurped control of !{group.name} from you. This was possible because you (and your mods) have spent more than a month not reviewing membership applications. Be active next time sweaty :!marseycheeky:")

	group.owner_id = v.id
	g.db.add(group)

	return {"message": f'You have usurped control of !{group.name} successfully!'}

@app.post("/!<group_name>/description")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def group_change_description(v, group_name):
	group_name = group_name.strip().lower()

	group = g.db.get(Group, group_name)
	if not group: abort(404)

	if v.id != group.owner_id:
		abort(403, f"Only the group owner (@{group.owner.username}) can change the description!")

	description = request.values.get('description')

	if description:
		description = description.strip()
		if len(description) > 100:
			abort(400, "New description is too long (max 100 characters)")

		description_html = filter_emojis_only(description, link=True)
		if len(description_html) > 1000:
			abort(400, "Rendered description is too long!")
	else:
		description = None
		description_html = None

	group.description = description
	group.description_html = description_html
	g.db.add(group)

	return {"message": 'Description changed successfully!'}
