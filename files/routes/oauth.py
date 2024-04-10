import sqlalchemy.exc

from files.classes import *
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.get import *
from files.routes.wrappers import *
from files.__main__ import app, limiter

@app.get("/authorize")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def authorize_prompt(v):
	client_id = request.values.get("client_id")
	application = g.db.query(OauthApp).filter_by(client_id=client_id).one_or_none()
	if not application:
		return {"oauth_error": "Invalid `client_id`"}, 400
	return render_template("oauth.html", v=v, application=application)

@app.post("/authorize")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def authorize(v):
	client_id = request.values.get("client_id")
	application = g.db.query(OauthApp).filter_by(client_id=client_id).one_or_none()
	if not application:
		return {"oauth_error": "Invalid `client_id`"}, 400
	access_token = secrets.token_urlsafe(128)[:128]

	new_auth = ClientAuth(oauth_client = application.id, user_id = v.id, access_token=access_token)
	g.db.add(new_auth)

	return redirect(f"{application.redirect_uri}?token={access_token}")

@app.post("/rescind/<int:aid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def rescind(v, aid):

	auth = g.db.query(ClientAuth).filter_by(oauth_client = aid, user_id = v.id).one_or_none()
	if not auth: abort(400)
	g.db.delete(auth)
	return {"message": "Authorization revoked!"}


@app.post("/api_keys")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def request_api_keys(v):
	description = request.values.get("description", "").strip()
	if len(description) > 256:
		abort(400, 'App description is too long (max 256 characters)')

	new_app = OauthApp(
		app_name=request.values.get('name').replace('<','').replace('>',''),
		redirect_uri=request.values.get('redirect_uri'),
		author_id=v.id,
		description=description,
	)

	g.db.add(new_app)

	body = f"@{v.username} has requested API keys for `{request.values.get('name')}`. You can approve or deny the request [here](/admin/apps)."
	notified_user_id = AEVANN_ID if AEVANN_ID else 5
	send_repeatable_notification(notified_user_id, body)

	return {"message": "API keys requested successfully!"}


@app.post("/delete_app/<int:aid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def delete_oauth_app(v, aid):
	try:
		aid = int(aid)
	except:
		abort(404)
	app = g.db.get(OauthApp, aid)
	if not app: abort(404)

	if app.author_id != v.id: abort(403)

	for auth in g.db.query(ClientAuth).filter_by(oauth_client=app.id):
		g.db.delete(auth)

	g.db.delete(app)


	return redirect('/apps')


@app.post("/edit_app/<int:aid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def edit_oauth_app(v, aid):
	try:
		aid = int(aid)
	except:
		abort(404)
	app = g.db.get(OauthApp, aid)
	if not app: abort(404)

	if app.author_id != v.id: abort(403)

	app.redirect_uri = request.values.get('redirect_uri')
	app.app_name = request.values.get('name')

	description = request.values.get("description", "").strip()
	if len(description) > 256:
		abort(400, 'App description is too long (max 256 characters)')

	app.description = description

	g.db.add(app)

	return {"message": "App edited successfully!"}


@app.post("/admin/app/approve/<int:aid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['APPS_MODERATION'])
def admin_app_approve(v, aid):

	app = g.db.get(OauthApp, aid)
	if not app: abort(404)

	user = app.author

	if not app.client_id:
		app.client_id = secrets.token_urlsafe(64)[:64]
		g.db.add(app)

		access_token = secrets.token_urlsafe(128)[:128]
		new_auth = ClientAuth(
			oauth_client = app.id,
			user_id = user.id,
			access_token=access_token
		)

		g.db.add(new_auth)

		send_repeatable_notification(user.id, f"@{v.username} (a site admin) has approved your application `{app.app_name}`.\n\nHere's your access token: ||{access_token}||\n\nPlease check the guide [here](/api) if you don't know what to do next!")

		ma = ModAction(
			kind="approve_app",
			user_id=v.id,
			target_user_id=user.id,
		)
		g.db.add(ma)


	return {"message": f"'{app.app_name}' approved!"}


@app.post("/admin/app/revoke/<int:aid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['APPS_MODERATION'])
def admin_app_revoke(v, aid):

	app = g.db.get(OauthApp, aid)
	if app:
		for auth in g.db.query(ClientAuth).filter_by(oauth_client=app.id): g.db.delete(auth)

		if v.id != app.author.id:
			send_repeatable_notification(app.author.id, f"@{v.username} (a site admin) has revoked your application `{app.app_name}`.")

		g.db.delete(app)

		ma = ModAction(
			kind="revoke_app",
			user_id=v.id,
			target_user_id=app.author.id,
		)
		g.db.add(ma)


	return {"message": f"'{app.app_name}' revoked!"}


@app.post("/admin/app/reject/<int:aid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['APPS_MODERATION'])
def admin_app_reject(v, aid):

	app = g.db.get(OauthApp, aid)

	if app:
		for auth in g.db.query(ClientAuth).filter_by(oauth_client=app.id): g.db.delete(auth)

		if v.id != app.author.id:
			send_repeatable_notification(app.author.id, f"@{v.username} (a site admin) has rejected your application `{app.app_name}`.")

		g.db.delete(app)

		ma = ModAction(
			kind="reject_app",
			user_id=v.id,
			target_user_id=app.author.id,
		)
		g.db.add(ma)


	return {"message": f"'{app.app_name}' rejected!"}


@app.get("/admin/app/<int:aid>/posts")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['APPS_MODERATION'])
def admin_app_id_posts(v, aid):
	oauth = g.db.get(OauthApp, aid)
	if not oauth: abort(404)

	page = get_page()

	pids, total = oauth.idlist(Post, page=page)

	posts = get_posts(pids, v=v)

	return render_template("admin/app.html",
						v=v,
						app=oauth,
						listing=posts,
						total=total
						)

@app.get("/admin/app/<int:aid>/comments")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['APPS_MODERATION'])
def admin_app_id_comments(v, aid):

	oauth = g.db.get(OauthApp, aid)
	if not oauth: abort(404)

	page = get_page()

	cids, total = oauth.idlist(Comment, page=page)

	comments = get_comments(cids, v=v)


	return render_template("admin/app.html",
						v=v,
						app=oauth,
						comments=comments,
						total=total,
						standalone=True
						)


@app.get("/admin/apps")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['APPS_MODERATION'])
def admin_apps_list(v):

	not_approved = g.db.query(OauthApp).filter(OauthApp.client_id == None).order_by(OauthApp.id.desc()).all()

	approved = g.db.query(OauthApp).filter(OauthApp.client_id != None).order_by(OauthApp.id.desc()).all()

	apps = not_approved + approved

	return render_template("admin/apps.html", v=v, apps=apps)


@app.post("/reroll/<int:aid>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def reroll_oauth_tokens(aid, v):

	aid = aid

	a = g.db.get(OauthApp, aid)
	if not a: abort(404)

	if a.author_id != v.id: abort(403)

	a.client_id = secrets.token_urlsafe(64)[:64]
	g.db.add(a)


	return {"message": f"Client ID for '{a.app_name}' has been rerolled!", "id": a.client_id}
