from files.classes import *
from files.helpers.alerts import *
from files.helpers.regex import *
from files.helpers.get import *
from files.helpers.actions import execute_under_siege

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
	name = request.values.get("name", "").strip().lstrip("!").strip().lower()
	if not name: stop(400)

	if name.startswith('slots') or name.startswith('remindme'):
		stop(400, "You can't make a group with that name!")

	if not hole_group_name_regex.fullmatch(name):
		stop(400, "Name does not match the required format!")

	if name in {'everyone', 'jannies', 'holejannies', 'followers', 'commenters'} or g.db.get(Group, name):
		stop(400, "This group already exists!")

	charge_reason = f'Cost of creating <a href="/!{name}">!{name}</a>'
	if not v.charge_account('coins/marseybux', GROUP_COST, charge_reason):
		stop(403, "You don't have enough coins or marseybux!")

	g.db.add(v)
	if v.shadowbanned: stop(500)

	group = Group(
			name=name,
			owner_id=v.id,
		)
	g.db.add(group)

	group_membership = GroupMembership(
		user_id=v.id,
		group_name=group.name,
		created_utc=time.time(),
		approved_utc=time.time(),
		is_mod=True,
		)
	g.db.add(group_membership)

	g.db.flush() #Necessary, to make linkfying the ping group in the notification work

	text = f":!marseyparty: !{group} has been created by @{v.username} :marseyparty:"
	alert_active_users(text, v.id, User.group_creation_notifs == True)

	cache.delete("group_count")

	return {"message": f"!{group} created successfully!"}

@app.post("/!<group_name>/apply")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def join_group(v, group_name):
	group_name = group_name.strip().lower()

	if group_name == 'verifiedrich' and not v.patron:
		stop(403, f"Only {patron}s can join !verifiedrich")

	if group_name in {'verifiedrich', 'focusgroup'}:
		join = GroupMembership(
				user_id=v.id,
				group_name=group_name,
				approved_utc = time.time()
			)
		g.db.add(join)
		return {"message": f"You have joined !{group_name} successfully!"}

	group = g.db.get(Group, group_name)
	if not group: stop(404)

	blacklist = g.db.query(GroupBlacklist.user_id).filter_by(user_id=v.id, group_name=group_name).one_or_none()
	if blacklist:
		stop(403, f"You're blacklisted from !{group_name}")

	execute_under_siege(v, group, "ping group application")

	existing = g.db.query(GroupMembership).filter_by(user_id=v.id, group_name=group_name).one_or_none()
	if not existing:
		join = GroupMembership(user_id=v.id, group_name=group_name)
		g.db.add(join)

		notified_ids = [group.owner_id]
		notified_ids += [x[0] for x in g.db.query(GroupMembership.user_id).filter_by(group_name=group_name, is_mod=True).all()]
		notified_ids = list(set(notified_ids))

		if 2249 in notified_ids:
			notified_ids.remove(2249)

		text = f"@{v.username} has applied to join !{group}. You can approve or reject the application [here](/!{group})."
		cid = notif_comment(text)
		for uid in notified_ids:
			add_notif(cid, uid, text, pushnotif_url=f'{SITE_FULL}/!{group}')

	return {"message": f"Application to !{group} submitted successfully!"}

@app.post("/!<group_name>/leave")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def leave_group(v, group_name):
	group_name = group_name.strip().lower()

	group = g.db.get(Group, group_name)
	if not group: stop(404)
	existing = g.db.query(GroupMembership).filter_by(user_id=v.id, group_name=group_name).one_or_none()
	if existing:
		if existing.approved_utc:
			text = f"@{v.username} has left !{group}"
			msg = f"You have left !{group} successfully!"
			func = send_repeatable_notification
		else:
			text = f"@{v.username} has cancelled their application to !{group}"
			msg = f"You have cancelled your application to !{group} successfully!"
			func = send_notification

		if v.id == group.owner_id:
			new_owner_id = g.db.query(GroupMembership.user_id).filter(
				GroupMembership.user_id != group.owner_id,
				GroupMembership.group_name == group.name,
				GroupMembership.approved_utc != None,
			).order_by(GroupMembership.is_mod.desc(), GroupMembership.approved_utc).first()

			if new_owner_id:
				new_owner_id = new_owner_id[0]
				send_repeatable_notification(new_owner_id, f"@{group.owner.username} (!{group}'s owner) has left the group, You're now the new owner!")
				group.owner_id = new_owner_id
				g.db.add(group)
		else:
			func(group.owner_id, text)

		g.db.delete(existing)

		return {"message": msg}

	return {"message": ''}


@app.get("/!<group_name>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def memberships(v, group_name):
	page = get_page()

	group_name = group_name.strip().lower()

	group = g.db.get(Group, group_name)
	if not group: stop(404)

	members = g.db.query(GroupMembership).join(GroupMembership.user).options(
				joinedload(GroupMembership.user),
				joinedload(GroupMembership.approver),
			).filter(
				GroupMembership.group_name == group_name,
				GroupMembership.approved_utc != None,
				GroupMembership.user_id != group.owner_id,
			)
	total = members.count()
	if page == 1: size = 499
	else: size = 500
	members = members.order_by(GroupMembership.is_mod.desc(), GroupMembership.approved_utc).offset(size * (page - 1)).limit(size).all()

	if page == 1:
		owner = [g.db.query(GroupMembership).options(
					joinedload(GroupMembership.user),
					joinedload(GroupMembership.approver),
				).filter(
					GroupMembership.group_name == group_name,
					GroupMembership.approved_utc != None,
					GroupMembership.user_id == group.owner_id,
				).one()]
		members = owner + members

	applications = g.db.query(GroupMembership).filter(
			GroupMembership.group_name == group_name,
			GroupMembership.approved_utc == None
		).order_by(GroupMembership.created_utc).all()

	return render_template('group_memberships.html', v=v, group=group, members=members, applications=applications, page=page, total=total, size=size)

@app.post("/!<group_name>/<user_id>/approve")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def group_approve(v, group_name, user_id):
	group_name = group_name.strip().lower()

	group = g.db.get(Group, group_name)
	if not group: stop(404)

	if not v.mods_group(group):
		stop(403, f"Only the group owner and its mods can approve applications!")

	application = g.db.query(GroupMembership).filter_by(user_id=user_id, group_name=group.name).one_or_none()
	if not application:
		stop(404, "There is no application to approve!")

	if not application.approved_utc:
		application.approved_utc = time.time()
		application.approver_id = v.id
		g.db.add(application)
		if v.id != application.user_id:
			send_repeatable_notification(application.user_id, f"@{v.username} has approved your application to !{group}")

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
	if not group: stop(404)

	if not v.mods_group(group):
		stop(403, f"Only the group owner and its mods can reject memberships!")

	membership = g.db.query(GroupMembership).filter_by(user_id=user_id, group_name=group.name).one_or_none()
	if not membership:
		stop(404, "There is no membership to reject!")
	uid = membership.user_id

	if membership.user_id == group.owner_id and v.admin_level < PERMS["MODS_EVERY_GROUP"]:
		stop(403, "You can't kick the group owner!")

	if v.id != group.owner_id and membership.is_mod and v.admin_level < PERMS["MODS_EVERY_GROUP"]:
		stop(403, "Only the group owner can kick mods!")

	if membership.approved_utc:
		text = f"@{v.username} has kicked you from !{group}"
		msg = f"You have kicked @{membership.user.username} successfully!"
	else:
		text = f"@{v.username} has rejected your application to !{group}"
		msg = f"You have rejected @{membership.user.username} successfully!"
	send_repeatable_notification(membership.user_id, text)

	if membership.user_id == group.owner_id:
		new_owner_id = g.db.query(GroupMembership.user_id).filter(
			GroupMembership.user_id != group.owner_id,
			GroupMembership.group_name == group.name,
			GroupMembership.approved_utc != None,
		).order_by(GroupMembership.is_mod.desc(), GroupMembership.approved_utc).first()

		if new_owner_id:
			new_owner_id = new_owner_id[0]
			send_repeatable_notification(new_owner_id, f"@{group.owner.username} (!{group}'s owner) has been kicked from the group by site admins, You're now the new owner!")
			group.owner_id = new_owner_id
			g.db.add(group)

	g.db.delete(membership)

	g.db.flush()
	count = g.db.query(GroupMembership).filter_by(group_name=group.name).count()
	if not count:
		g.db.commit() #need it to fix "Dependency rule tried to blank-out primary key column 'group_memberships.group_name' on instance"
		g.db.delete(group)
		msg = f"You have deleted !{group} successfully!"

		text = f':marseydisintegrate: !{group} has been deleted by @{v.username} :!marseydisintegrate:'
		alert_active_users(text, None, User.group_creation_notifs == True)

	if count and v.id != uid:
		group_blacklist = GroupBlacklist(
			user_id=uid,
			group_name=group.name,
			blacklister_id=v.id,
			)
		g.db.add(group_blacklist)

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
	if not group: stop(404)

	if v.id != group.owner_id:
		stop(403, f"Only the group owner (@{group.owner.username}) can add mods!")

	membership = g.db.query(GroupMembership).filter_by(user_id=user_id, group_name=group.name).one_or_none()
	if not membership:
		stop(404, "The user is not a member of the group!")

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
	if not group: stop(404)

	if v.id != group.owner_id:
		stop(403, f"Only the group owner (@{group.owner.username}) can remove mods!")

	membership = g.db.query(GroupMembership).filter_by(user_id=user_id, group_name=group.name).one_or_none()
	if not membership:
		stop(404, "The user is not a member of the group!")

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
	if not group: stop(404)

	if v.mods_group(group):
		stop(403, f"You're a mod of !{group.name} can't usurp it!")

	if not v.is_member_of_group(group):
		stop(403, "Only members of groups can usurp them!")

	search_html = f'''%</a> has % your application to <a href="/!{group.name}" rel="nofollow">!{group.name}</a></p>'''
	two_mo_ago = time.time() - 86400 * 60
	is_active = g.db.query(Notification.created_utc).join(Notification.comment).filter(
		Notification.created_utc > two_mo_ago,
		Comment.author_id == AUTOJANNY_ID,
		Comment.parent_post == None,
		Comment.body_html.like(search_html),
	).first()

	two_mo_old_applications = g.db.query(GroupMembership.user_id).join(GroupMembership.user).filter(
		GroupMembership.group_name == group.name,
		GroupMembership.approved_utc == None,
		GroupMembership.created_utc < two_mo_ago,
		User.shadowbanned == None,
	).first()

	if is_active or not two_mo_old_applications:
		send_notification(group.owner_id, f"@{v.username} has tried to usurp control of !{group.name} from you and failed because you reviewed a membership application in the past 2 months!")
		g.db.commit()
		stop(403, "The current regime has reviewed a membership application in the past 2 months, so you can't usurp them!")

	send_repeatable_notification(group.owner_id, f"@{v.username} has usurped control of !{group.name} from you. This was possible because you (and your mods) have spent more than 2 months not reviewing membership applications. Be active next time sweaty :!marseycheeky:")

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
	if not group: stop(404)

	if v.id != group.owner_id:
		stop(403, f"Only the group owner (@{group.owner.username}) can change the description!")

	description = request.values.get('description')

	if description:
		description = description.strip()
		if len(description) > 100:
			stop(400, "New description is too long (max 100 characters)")

		description_html = filter_emojis_only(description, link=True)
		if len(description_html) > 1000:
			stop(400, "Rendered description is too long!")
	else:
		description = None
		description_html = None

	group.description = description
	group.description_html = description_html
	g.db.add(group)

	return {"message": 'Description changed successfully!'}

@app.post("/!<group_name>/<user_id>/unblacklist")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def group_unblacklist(v, group_name, user_id):
	group_name = group_name.strip().lower()

	group = g.db.get(Group, group_name)
	if not group: stop(404)

	if not v.mods_group(group):
		stop(403, "Only the group owner and its mods can unblacklist someone!")

	blacklist = g.db.query(GroupBlacklist).filter_by(user_id=user_id, group_name=group.name).one_or_none()
	if not blacklist:
		stop(404, "This user is not blacklisted!")

	g.db.delete(blacklist)

	send_repeatable_notification(user_id, f"@{v.username} has unblacklisted you from !{group}")

	u = get_account(user_id)

	return {"message": f"@{u.username} has been unblacklisted from !{group} successfully!"}