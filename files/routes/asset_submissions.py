from os import path, rename
from shutil import copyfile, move

from files.classes.emoji import *
from files.classes.hats import Hat, HatDef
from files.classes.mod_logs import ModAction
from files.helpers.cloudflare import purge_files_in_cache
from files.helpers.config.const import *
from files.helpers.get import *
from files.helpers.media import *
from files.helpers.useractions import *
from files.routes.wrappers import *
from files.__main__ import app, cache, limiter

ASSET_TYPES = (Emoji, HatDef)

@app.get("/submit/marseys")
def submit_marseys_redirect():
	return redirect("/submit/emojis")

@app.get("/submit/emojis")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def submit_emojis(v:User):
	if v.admin_level >= PERMS['VIEW_PENDING_SUBMITTED_EMOJIS']:
		emojis = g.db.query(Emoji).filter(Emoji.submitter_id != None)
	else:
		emojis = g.db.query(Emoji).filter(Emoji.submitter_id == v.id)

	emojis = emojis.order_by(Emoji.created_utc.desc()).all()

	for emoji in emojis:
		emoji.author = g.db.query(User.username).filter_by(id=emoji.author_id).one()[0]
		emoji.submitter = g.db.query(User.username).filter_by(id=emoji.submitter_id).one()[0]

	return render_template("submit_emojis.html", v=v, emojis=emojis, kinds=EMOJIS_KINDS, msg=get_msg(), error=get_error())


@app.post("/submit/emojis")
@limiter.limit('1/second', scope=rpath)
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def submit_emoji(v:User):
	file = request.files["image"]
	name = request.values.get('name', '').lower().strip()
	tags = request.values.get('tags', '').lower().strip()
	username = request.values.get('author', '').lower().strip()
	kind = request.values.get('kind', '').strip()

	def error(error):
		return redirect(f"/submit/emojis?error={error}")

	if kind not in EMOJIS_KINDS:
		return error("Invalid emoji kind!")

	if kind in {"Marsey", "Platy", "Wolf", "Tay"} and not name.startswith(kind.lower()):
		return error(f'The name of this emoji should start with the word "{kind.lower()}"')

	if kind == "Marsey Flags" and not name.startswith("marseyflag"):
		return error('The name of this emoji should start with the word "marseyflag"')

	if g.is_tor:
		return error("Image uploads are not allowed through TOR!")

	if not file or not file.content_type.startswith('image/'):
		return error("You need to submit an image!")

	if not emoji_name_regex.fullmatch(name):
		return error("Invalid name!")

	existing = g.db.query(Emoji.name).filter_by(name=name).one_or_none()
	if existing:
		return error("Someone already submitted an emoji with this name!")

	if not tags_regex.fullmatch(tags):
		return error("Invalid tags!")

	author = get_user(username, v=v, graceful=True)
	if not author:
		return error(f"A user with the name '{username}' was not found!")

	highquality = f'/asset_submissions/marseys/{name}'
	file.save(highquality)

	filename = f'/asset_submissions/marseys/{name}.webp'
	copyfile(highquality, filename)
	process_image(filename, v, resize=200, trim=True)

	emoji = Emoji(name=name, kind=kind, author_id=author.id, tags=tags, count=0, submitter_id=v.id)
	g.db.add(emoji)

	return redirect(f"/submit/emojis?msg='{name}' submitted successfully!")

def verify_permissions_and_get_asset(cls, asset_type:str, v:User, name:str, make_lower=False):
	if cls not in ASSET_TYPES: raise Exception("not a valid asset type")
	name = name.strip()
	if make_lower: name = name.lower()
	asset = None
	if cls == HatDef:
		asset = g.db.query(cls).filter_by(name=name).one_or_none()
	else:
		asset = g.db.get(cls, name)
	if not asset:
		abort(404, f"This {asset} '{name}' doesn't exist!")
	return asset

@app.post("/admin/approve/emoji/<name>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['MODERATE_PENDING_SUBMITTED_ASSETS'])
def approve_emoji(v, name):
	emoji = verify_permissions_and_get_asset(Emoji, "emoji", v, name, True)
	tags = request.values.get('tags').lower().strip()
	if not tags:
		abort(400, "You need to include tags!")

	new_name = request.values.get('name').lower().strip()
	if not new_name:
		abort(400, "You need to include name!")

	new_kind = request.values.get('kind').strip()
	if not new_kind:
		abort(400, "You need to include kind!")

	if not emoji_name_regex.fullmatch(new_name):
		abort(400, "Invalid name!")

	if not tags_regex.fullmatch(tags):
		abort(400, "Invalid tags!")

	if new_kind not in EMOJIS_KINDS:
		abort(400, "Invalid kind!")


	emoji.name = new_name
	emoji.kind = new_kind
	emoji.tags = tags
	g.db.add(emoji)

	author = get_account(emoji.author_id)

	if emoji.kind == "Marsey":
		all_by_author = g.db.query(Emoji).filter_by(kind="Marsey", author_id=author.id).count()
		if all_by_author >= 99:
			badge_grant(badge_id=143, user=author)
		elif all_by_author >= 9:
			badge_grant(badge_id=16, user=author)
		else:
			badge_grant(badge_id=17, user=author)			
	elif emoji.kind == "Wolf":
		all_by_author = g.db.query(Emoji).filter_by(kind="Wolf", author_id=author.id).count()
		if all_by_author >= 9:
			badge_grant(badge_id=111, user=author)
		else:
			badge_grant(badge_id=110, user=author)
	elif emoji.kind == "Platy":
		all_by_author = g.db.query(Emoji).filter_by(kind="Platy", author_id=author.id).count()
		if all_by_author >= 9:
			badge_grant(badge_id=113, user=author)
		else:
			badge_grant(badge_id=112, user=author)
	

	if emoji.kind == "Marsey":
		cache.delete(MARSEYS_CACHE_KEY)

	purge_files_in_cache([f"https://{SITE}/e/{emoji.name}/webp", f"https://{SITE}/emojis.csv"])

	move(f"/asset_submissions/marseys/{name}.webp", f"files/assets/images/emojis/{emoji.name}.webp")

	highquality = f"/asset_submissions/marseys/{name}"
	with Image.open(highquality) as i:
		new_path = f'/asset_submissions/marseys/original/{name}.{i.format.lower()}'
	rename(highquality, new_path)

	author.pay_account('coins', 250)
	g.db.add(author)

	if v.id != author.id:
		msg = f"@{v.username} (a site admin) has approved an emoji you made: :{emoji.name}:\n\nYou have received 250 coins as a reward!"
		send_repeatable_notification(author.id, msg)

	if v.id != emoji.submitter_id and author.id != emoji.submitter_id:
		msg = f"@{v.username} (a site admin) has approved an emoji you submitted: :{emoji.name}:"
		send_repeatable_notification(emoji.submitter_id, msg)

	emoji.submitter_id = None

	ma = ModAction(
		kind="approve_emoji",
		user_id=v.id,
		_note=f'<img loading="lazy" data-bs-toggle="tooltip" alt=":{name}:" title=":{name}:" src="/e/{name}.webp">'
	)
	g.db.add(ma)

	return {"message": f"'{emoji.name}' approved!"}

def remove_asset(cls, type_name:str, v:User, name:str) -> dict[str, str]:
	if cls not in ASSET_TYPES: raise Exception("not a valid asset type")
	should_make_lower = cls == Emoji
	if should_make_lower: name = name.lower()
	name = name.strip()
	if not name:
		abort(400, f"You need to specify a {type_name}!")
	asset = None
	if cls == HatDef:
		asset = g.db.query(cls).filter_by(name=name).one_or_none()
	else:
		asset = g.db.get(cls, name)
	if not asset:
		abort(404, f"This {type_name} '{name}' doesn't exist!")
	if v.id != asset.submitter_id and v.admin_level < PERMS['MODERATE_PENDING_SUBMITTED_ASSETS']:
		abort(403)
	name = asset.name

	if v.id != asset.submitter_id:
		msg = f"@{v.username} has rejected a {type_name} you submitted: `'{name}'`"
		send_repeatable_notification(asset.submitter_id, msg)

		ma = ModAction(
			kind=f"reject_{type_name}",
			user_id=v.id,
			_note=name
		)
		g.db.add(ma)

	g.db.delete(asset)

	if type_name == "emoji": type_name = "marsey"
	remove_media_using_link(f"/asset_submissions/{type_name}s/{name}.webp")
	remove_media_using_link(f"/asset_submissions/{type_name}s/{name}")

	return {"message": f"'{name}' removed!"}

@app.post("/remove/emoji/<name>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def remove_emoji(v:User, name):
	return remove_asset(Emoji, "emoji", v, name)

@app.get("/submit/hats")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def submit_hats(v:User):
	if v.admin_level >= PERMS['VIEW_PENDING_SUBMITTED_HATS']: hats = g.db.query(HatDef).filter(HatDef.submitter_id != None)
	else: hats = g.db.query(HatDef).filter(HatDef.submitter_id == v.id)
	hats = hats.order_by(HatDef.created_utc.desc()).all()

	return render_template("submit_hats.html", v=v, hats=hats, msg=get_msg(), error=get_error())


@app.post("/submit/hats")
@limiter.limit('1/second', scope=rpath)
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def submit_hat(v:User):
	name = request.values.get('name', '').strip()
	description = request.values.get('description', '').strip()
	username = request.values.get('author', '').strip()

	def error(error):
		return redirect(f"/submit/hats?error={error}")

	if g.is_tor:
		return error("Image uploads are not allowed through TOR!")

	file = request.files["image"]
	if not file or not file.content_type.startswith('image/'):
		return error("You need to submit an image!")

	if not hat_regex.fullmatch(name):
		return error("Invalid name!")

	existing = g.db.query(HatDef.name).filter_by(name=name).one_or_none()
	if existing:
		return error("A hat with this name already exists!")

	if not description_regex.fullmatch(description):
		return error("Invalid description!")

	author = get_user(username, v=v, graceful=True)
	if not author:
		return error(f"A user with the name '{username}' was not found!")

	highquality = f'/asset_submissions/hats/{name}'
	file.save(highquality)

	with Image.open(highquality) as i:
		if i.width > 100 or i.height > 130:
			remove_media_using_link(highquality)
			return error("Images must be 100x130")

		if len(list(Iterator(i))) > 1: price = 1000
		else: price = 500

	filename = f'/asset_submissions/hats/{name}.webp'
	copyfile(highquality, filename)
	process_image(filename, v, resize=100)

	hat = HatDef(name=name, author_id=author.id, description=description, price=price, submitter_id=v.id)
	g.db.add(hat)

	return redirect(f"/submit/hats?msg='{name}' submitted successfully!")


@app.post("/admin/approve/hat/<name>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit("120/minute;200/hour;1000/day")
@limiter.limit("120/minute;200/hour;1000/day", key_func=get_ID)
@admin_level_required(PERMS['MODERATE_PENDING_SUBMITTED_ASSETS'])
def approve_hat(v, name):
	hat = verify_permissions_and_get_asset(HatDef, "hat", v, name, False)
	description = request.values.get('description').strip()
	if not description: abort(400, "You need to include a description!")

	new_name = request.values.get('name').strip()
	if not new_name: abort(400, "You need to include a name!")
	if not hat_regex.fullmatch(new_name): abort(400, "Invalid name!")
	if not description_regex.fullmatch(description): abort(400, "Invalid description!")

	try:
		hat.price = int(request.values.get('price'))
		if hat.price < 0: raise ValueError("Invalid hat price")
	except:
		abort(400, "Invalid hat price")
	hat.name = new_name
	hat.description = description
	g.db.add(hat)


	g.db.flush()
	author = hat.author

	all_by_author = g.db.query(HatDef).filter_by(author_id=author.id).count()

	if all_by_author >= 250:
		badge_grant(badge_id=166, user=author)
	elif all_by_author >= 100:
		badge_grant(badge_id=165, user=author)
	elif all_by_author >= 50:
		badge_grant(badge_id=164, user=author)
	elif all_by_author >= 10:
		badge_grant(badge_id=163, user=author)

	hat_copy = Hat(
		user_id=author.id,
		hat_id=hat.id
	)
	g.db.add(hat_copy)


	if v.id != author.id:
		msg = f"@{v.username} (a site admin) has approved a hat you made: '{hat.name}'"
		send_repeatable_notification(author.id, msg)

	if v.id != hat.submitter_id and author.id != hat.submitter_id:
		msg = f"@{v.username} (a site admin) has approved a hat you submitted: '{hat.name}'"
		send_repeatable_notification(hat.submitter_id, msg)

	hat.submitter_id = None

	move(f"/asset_submissions/hats/{name}.webp", f"files/assets/images/hats/{hat.name}.webp")

	highquality = f"/asset_submissions/hats/{name}"
	with Image.open(highquality) as i:
		new_path = f'/asset_submissions/hats/original/{name}.{i.format.lower()}'
	rename(highquality, new_path)

	ma = ModAction(
		kind="approve_hat",
		user_id=v.id,
		_note=f'<a href="/i/hats/{name}.webp">{name}</a>'
	)
	g.db.add(ma)

	return {"message": f"'{hat.name}' approved!"}

@app.post("/remove/hat/<name>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@auth_required
def remove_hat(v:User, name):
	return remove_asset(HatDef, 'hat', v, name)

@app.get("/admin/update/emojis")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['UPDATE_ASSETS'])
def update_emojis(v):
	name = request.values.get('name')
	tags = None
	error = None
	if name:
		emoji = g.db.get(Emoji, name)
		if emoji:
			tags = emoji.tags or ''
		else:
			name = ''
			tags = ''
			error = "An emoji with this name doesn't exist!"
	return render_template("admin/update_assets.html", v=v, error=error, name=name, tags=tags, type="Emoji")


@app.post("/admin/update/emojis")
@limiter.limit('1/second', scope=rpath)
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['UPDATE_ASSETS'])
def update_emoji(v):
	file = request.files["image"]
	name = request.values.get('name', '').lower().strip()
	tags = request.values.get('tags', '').lower().strip()

	def error(error):
		return render_template("admin/update_assets.html", v=v, error=error, name=name, tags=tags, type="Emoji")

	existing = g.db.get(Emoji, name)
	if not existing:
		return error("An emoji with this name doesn't exist!")

	updated = False

	if file:
		if g.is_tor:
			return error("Image uploads are not allowed through TOR!")
		if not file.content_type.startswith('image/'):
			return error("You need to submit an image!")

		for x in IMAGE_FORMATS:
			if path.isfile(f'/asset_submissions/marseys/original/{name}.{x}'):
				remove_media_using_link(f'/asset_submissions/marseys/original/{name}.{x}')

		highquality = f"/asset_submissions/marseys/{name}"
		file.save(highquality)
		with Image.open(highquality) as i:
			format = i.format.lower()
		new_path = f'/asset_submissions/marseys/original/{name}.{format}'
		rename(highquality, new_path)

		filename = f"files/assets/images/emojis/{name}.webp"
		copyfile(new_path, filename)
		process_image(filename, v, resize=200, trim=True)
		purge_files_in_cache([f"https://{SITE}/e/{name}.webp", f"https://{SITE}/assets/images/emojis/{name}.webp", f"https://{SITE}/asset_submissions/marseys/original/{name}.{format}"])
		updated = True


	if tags and existing.tags != tags and tags != "none":
		if not tags_regex.fullmatch(tags):
			abort(400, "Invalid tags!")
		existing.tags += f" {tags}"
		g.db.add(existing)
		updated = True

	if not updated:
		return error("You need to actually update something!")

	ma = ModAction(
		kind="update_emoji",
		user_id=v.id,
		_note=f'<img loading="lazy" data-bs-toggle="tooltip" alt=":{name}:" title=":{name}:" src="/e/{name}.webp">'
	)
	g.db.add(ma)
	return render_template("admin/update_assets.html", v=v, msg=f"'{name}' updated successfully!", name=name, tags=tags, type="Emoji")

@app.get("/admin/update/hats")
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['UPDATE_ASSETS'])
def update_hats(v):
	return render_template("admin/update_assets.html", v=v, type="Hat")


@app.post("/admin/update/hats")
@limiter.limit('1/second', scope=rpath)
@limiter.limit(DEFAULT_RATELIMIT)
@limiter.limit(DEFAULT_RATELIMIT, key_func=get_ID)
@admin_level_required(PERMS['UPDATE_ASSETS'])
def update_hat(v):
	file = request.files["image"]
	name = request.values.get('name', '').strip()

	def error(error):
		return render_template("admin/update_assets.html", v=v, error=error, type="Hat")

	if g.is_tor:
		return error("Image uploads are not allowed through TOR!")

	if not file or not file.content_type.startswith('image/'):
		return error("You need to submit an image!")

	if not hat_regex.fullmatch(name):
		return error("Invalid name!")

	existing = g.db.query(HatDef.name).filter_by(name=name).one_or_none()
	if not existing:
		return error("A hat with this name doesn't exist!")

	highquality = f"/asset_submissions/hats/{name}"
	file.save(highquality)

	with Image.open(highquality) as i:
		if i.width > 100 or i.height > 130:
			remove_media_using_link(highquality)
			return error("Images must be 100x130")

		format = i.format.lower()
	new_path = f'/asset_submissions/hats/original/{name}.{format}'

	for x in IMAGE_FORMATS:
		if path.isfile(f'/asset_submissions/hats/original/{name}.{x}'):
			remove_media_using_link(f'/asset_submissions/hats/original/{name}.{x}')

	rename(highquality, new_path)

	filename = f"files/assets/images/hats/{name}.webp"
	copyfile(new_path, filename)
	process_image(filename, v, resize=100)
	purge_files_in_cache([f"https://{SITE}/i/hats/{name}.webp", f"https://{SITE}/assets/images/hats/{name}.webp", f"https://{SITE}/asset_submissions/hats/original/{name}.{format}"])
	ma = ModAction(
		kind="update_hat",
		user_id=v.id,
		_note=f'<a href="/i/hats/{name}.webp">{name}</a>'
	)
	g.db.add(ma)
	return render_template("admin/update_assets.html", v=v, msg=f"'{name}' updated successfully!", type="Hat")
