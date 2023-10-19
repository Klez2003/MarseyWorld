from os import path, rename
from shutil import copyfile, move

from files.classes.emoji import *
from files.classes.hats import Hat, HatDef
from files.classes.mod_logs import ModAction
from files.helpers.cloudflare import purge_files_in_cloudflare_cache
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
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def submit_emojis(v):
	emojis = g.db.query(Emoji).filter(Emoji.submitter_id != None)

	emojis = emojis.order_by(Emoji.created_utc.desc()).all()

	for emoji in emojis:
		emoji.author = g.db.query(User.username).filter_by(id=emoji.author_id).one()[0]
		emoji.submitter = g.db.query(User.username).filter_by(id=emoji.submitter_id).one()[0]

	return render_template("submit_emojis.html", v=v, emojis=emojis)


emoji_modifiers = ('pat', 'talking', 'genocide', 'love')

@app.post("/submit/emojis")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def submit_emoji(v):
	file = request.files["image"]
	name = request.values.get('name', '').lower().strip()
	tags = request.values.get('tags', '').lower().strip()
	username = request.values.get('author', '').lower().strip()
	kind = request.values.get('kind', '').strip()
	nsfw = bool(request.values.get("nsfw"))

	for modifier in emoji_modifiers:
		if name.endswith(modifier):
			abort(400, f'Submitted emoji names should NOT end with the word "{modifier}"')

	if kind not in EMOJI_KINDS:
		abort(400, "Invalid emoji kind!")

	if kind in {"Platy", "Wolf", "Tay", "Carp", "Capy"} and not name.startswith(kind.lower()):
		abort(400, f'The name of this emoji should start with the word "{kind.lower()}"')

	if kind == "Marsey" and not name.startswith("marsey") and not name.startswith("marcus"):
		abort(400, 'The name of this emoji should start with the word "Marsey" or "Marcus"')

	if kind == "Marsey Flags" and not name.startswith("marseyflag"):
		abort(400, 'The name of this emoji should start with the word "marseyflag"')

	if g.is_tor:
		abort(400, "Image uploads are not allowed through TOR!")

	if not file or not file.content_type.startswith('image/'):
		abort(400, "You need to submit an image!")

	if not emoji_name_regex.fullmatch(name):
		abort(400, "Invalid name!")

	existing = g.db.query(Emoji.name).filter_by(name=name).one_or_none()
	if existing:
		abort(400, "Someone already submitted an emoji with this name!")

	if not tags_regex.fullmatch(tags):
		abort(400, "Invalid tags!")

	author = get_user(username, v=v)

	highquality = f'/asset_submissions/emojis/{name}'
	file.save(highquality)
	process_image(highquality, v) #to ensure not malware

	filename = f'/asset_submissions/emojis/{name}.webp'
	copyfile(highquality, filename)
	process_image(filename, v, resize=300, trim=True)

	emoji = Emoji(
				name=name,
				kind=kind,
				author_id=author.id,
				tags=tags,
				count=0,
				submitter_id=v.id,
				nsfw=nsfw,
			)
	g.db.add(emoji)

	return {"message": f"'{name}' submitted successfully!"}


def verify_permissions_and_get_asset(cls, asset_type, v, name, make_lower=False):
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
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
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

	if new_kind not in EMOJI_KINDS:
		abort(400, "Invalid kind!")

	nsfw = request.values.get("nsfw") == 'true'

	emoji.name = new_name
	emoji.kind = new_kind
	emoji.tags = tags
	emoji.nsfw = nsfw
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
	elif emoji.kind == "Capy":
		all_by_author = g.db.query(Emoji).filter_by(kind="Capy", author_id=author.id).count()
		if all_by_author >= 9:
			badge_grant(badge_id=115, user=author)
		badge_grant(badge_id=114, user=author)
	elif emoji.kind == "Carp":
		all_by_author = g.db.query(Emoji).filter_by(kind="Carp", author_id=author.id).count()
		if all_by_author >= 9:
			badge_grant(badge_id=288, user=author)
		badge_grant(badge_id=287, user=author)
	elif emoji.kind == "Wolf":
		all_by_author = g.db.query(Emoji).filter_by(kind="Wolf", author_id=author.id).count()
		if all_by_author >= 9:
			badge_grant(badge_id=111, user=author)
		badge_grant(badge_id=110, user=author)
	elif emoji.kind == "Platy":
		all_by_author = g.db.query(Emoji).filter_by(kind="Platy", author_id=author.id).count()
		if all_by_author >= 9:
			badge_grant(badge_id=113, user=author)
		badge_grant(badge_id=112, user=author)

	cache.delete(f"emojis_{emoji.nsfw}")
	cache.delete(f"emoji_list_{emoji.kind}_{emoji.nsfw}")

	purge_files_in_cloudflare_cache(f"{SITE_FULL_IMAGES}/e/{emoji.name}/webp")

	move(f"/asset_submissions/emojis/{name}.webp", f"files/assets/images/emojis/{emoji.name}.webp")

	highquality = f"/asset_submissions/emojis/{name}"
	with Image.open(highquality) as i:
		new_path = f'/asset_submissions/emojis/original/{name}.{i.format.lower()}'
	rename(highquality, new_path)

	if 'pkmn' in emoji.tags: amount = 500
	else: amount = 250

	author.pay_account('coins', amount)
	g.db.add(author)

	if v.id != author.id:
		msg = f"@{v.username} (a site admin) has approved an emoji you made: :{emoji.name}:\n\nYou have received {amount} coins as a reward!"

		comment = request.values.get("comment")
		if comment:
			msg += f"\nComment: `{comment}`"

		send_repeatable_notification(author.id, msg)

	if v.id != emoji.submitter_id and author.id != emoji.submitter_id:
		msg = f"@{v.username} (a site admin) has approved an emoji you submitted: :{emoji.name}:"
		
		comment = request.values.get("comment")
		if comment:
			msg += f"\nComment: `{comment}`"

		send_repeatable_notification(emoji.submitter_id, msg)

	emoji.submitter_id = None

	ma = ModAction(
		kind="approve_emoji",
		user_id=v.id,
		_note=f'<img loading="lazy" data-bs-toggle="tooltip" alt=":{name}:" title=":{name}:" src="{SITE_FULL_IMAGES}/e/{name}.webp">'
	)
	g.db.add(ma)

	if emoji.nsfw:
		OVER_18_EMOJIS.append(emoji.name)

	return {"message": f"'{emoji.name}' approved!"}

def remove_asset(cls, type_name, v, name):
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

		comment = request.values.get("comment")
		if comment:
			msg += f"\nComment: `{comment}`"

		send_repeatable_notification(asset.submitter_id, msg)

		ma = ModAction(
			kind=f"reject_{type_name}",
			user_id=v.id,
			_note=name
		)
		g.db.add(ma)

	g.db.delete(asset)

	os.remove(f"/asset_submissions/{type_name}s/{name}.webp")
	os.remove(f"/asset_submissions/{type_name}s/{name}")

	return {"message": f"'{name}' removed!"}

@app.post("/remove/emoji/<name>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def remove_emoji(v, name):
	return remove_asset(Emoji, "emoji", v, name)

@app.get("/submit/hats")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def submit_hats(v):
	hats = g.db.query(HatDef).filter(HatDef.submitter_id != None).order_by(HatDef.created_utc.desc()).all()

	return render_template("submit_hats.html", v=v, hats=hats)


@app.post("/submit/hats")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def submit_hat(v):
	name = request.values.get('name', '').strip()
	description = request.values.get('description', '').strip()
	username = request.values.get('author', '').strip()

	if g.is_tor:
		abort(400, "Image uploads are not allowed through TOR!")

	file = request.files["image"]
	if not file or not file.content_type.startswith('image/'):
		abort(400, "You need to submit an image!")

	if not hat_name_regex.fullmatch(name):
		abort(400, "Invalid name!")

	existing = g.db.query(HatDef.name).filter_by(name=name).one_or_none()
	if existing:
		abort(400, "A hat with this name already exists!")

	if not description_regex.fullmatch(description):
		abort(400, "Invalid description!")

	author = get_user(username, v=v)

	highquality = f'/asset_submissions/hats/{name}'
	file.save(highquality)
	process_image(highquality, v) #to ensure not malware

	with Image.open(highquality) as i:
		if i.width > 100 or i.height > 130:
			os.remove(highquality)
			abort(400, "Images must be 100x130")

		if len(list(Iterator(i))) > 1: price = 1000
		else: price = 500

	filename = f'/asset_submissions/hats/{name}.webp'
	copyfile(highquality, filename)
	process_image(filename, v, resize=100)

	hat = HatDef(name=name, author_id=author.id, description=description, price=price, submitter_id=v.id)
	g.db.add(hat)

	return {"message": f"'{name}' submitted successfully!"}


@app.post("/admin/approve/hat/<name>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("120/minute;200/hour;1000/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("120/minute;200/hour;1000/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['MODERATE_PENDING_SUBMITTED_ASSETS'])
def approve_hat(v, name):
	hat = verify_permissions_and_get_asset(HatDef, "hat", v, name, False)
	description = request.values.get('description').strip()
	if not description: abort(400, "You need to include a description!")

	new_name = request.values.get('name').strip()
	if not new_name: abort(400, "You need to include a name!")
	if not hat_name_regex.fullmatch(new_name): abort(400, "Invalid name!")
	if not description_regex.fullmatch(description): abort(400, "Invalid description!")

	try:
		hat.price = int(request.values.get('price'))
		if hat.price < 0: raise ValueError("Invalid hat price")
	except:
		abort(400, "Invalid hat price")
	hat.name = new_name
	hat.description = description
	g.db.add(hat)

	author = hat.author

	all_by_author = g.db.query(HatDef).filter_by(author_id=author.id).count()

	if all_by_author >= 249:
		badge_grant(badge_id=166, user=author)
	elif all_by_author >= 99:
		badge_grant(badge_id=165, user=author)
	elif all_by_author >= 49:
		badge_grant(badge_id=164, user=author)
	elif all_by_author >= 9:
		badge_grant(badge_id=163, user=author)

	hat_copy = Hat(
		user_id=author.id,
		hat_id=hat.id
	)
	g.db.add(hat_copy)


	if v.id != author.id:
		msg = f"@{v.username} (a site admin) has approved a hat you made: `'{hat.name}'`"

		comment = request.values.get("comment")
		if comment:
			msg += f"\nComment: `{comment}`"

		send_repeatable_notification(author.id, msg)

	if v.id != hat.submitter_id and author.id != hat.submitter_id:
		msg = f"@{v.username} (a site admin) has approved a hat you submitted: `'{hat.name}'`"

		comment = request.values.get("comment")
		if comment:
			msg += f"\nComment: `{comment}`"

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
		_note=f'<a href="{SITE_FULL_IMAGES}/i/hats/{name}.webp">{name}</a>'
	)
	g.db.add(ma)

	return {"message": f"'{hat.name}' approved!"}

@app.post("/remove/hat/<name>")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def remove_hat(v, name):
	return remove_asset(HatDef, 'hat', v, name)

@app.get("/admin/update/emojis")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['UPDATE_ASSETS'])
def update_emojis(v):
	return render_template("admin/update_assets.html", v=v, type="Emoji")


@app.post("/admin/update/emojis")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['UPDATE_ASSETS'])
def update_emoji(v):
	name = request.values.get('name', '').lower().strip()

	file = request.files["image"]
	kind = request.values.get('kind', '').strip()
	new_name = request.values.get('new_name', '').strip()
	tags = request.values.get('tags', '').lower().strip()
	nsfw = request.values.get('nsfw', '').strip()		

	existing = g.db.get(Emoji, name)
	if not existing:
		abort(400, "An emoji with this name doesn't exist!")

	updated = False

	if new_name and existing.name != new_name:
		if not emoji_name_regex.fullmatch(new_name):
			abort(400, "Invalid new name!")

		old_path = f"files/assets/images/emojis/{existing.name}.webp"
		new_path = f"files/assets/images/emojis/{new_name}.webp"
		copyfile(old_path, new_path)

		for x in IMAGE_FORMATS:
			original_old_path = f'/asset_submissions/emojis/original/{existing.name}.{x}'
			original_new_path = f'/asset_submissions/emojis/original/{new_name}.{x}'
			if path.isfile(original_old_path):
				rename(original_old_path, original_new_path)

		existing.name = new_name
		updated = True
		name = existing.name

	if file:
		if g.is_tor:
			abort(400, "Image uploads are not allowed through TOR!")
		if not file.content_type.startswith('image/'):
			abort(400, "You need to submit an image!")

		for x in IMAGE_FORMATS:
			if path.isfile(f'/asset_submissions/emojis/original/{name}.{x}'):
				os.remove(f'/asset_submissions/emojis/original/{name}.{x}')

		highquality = f"/asset_submissions/emojis/{name}"
		file.save(highquality)
		process_image(highquality, v) #to ensure not malware
		with Image.open(highquality) as i:
			format = i.format.lower()
		new_path = f'/asset_submissions/emojis/original/{name}.{format}'
		rename(highquality, new_path)

		filename = f"files/assets/images/emojis/{name}.webp"
		copyfile(new_path, filename)
		process_image(filename, v, resize=300, trim=True)
		purge_files_in_cloudflare_cache([f"{SITE_FULL_IMAGES}/e/{name}.webp", f"{SITE_FULL_IMAGES}/asset_submissions/emojis/original/{name}.{format}"])
		updated = True

	if kind and existing.kind != kind:
		if kind not in EMOJI_KINDS:
			abort(400, "Invalid kind!")
		existing.kind = kind
		updated = True

	if tags and existing.tags != tags:
		if not tags_regex.fullmatch(tags):
			abort(400, "Invalid tags!")
		existing.tags += f" {tags}"
		updated = True

	if nsfw:
		nsfw = (nsfw == 'NSFW')
		if existing.nsfw != nsfw:
			existing.nsfw = nsfw
			updated = True

	if not updated:
		abort(400, "You need to actually update something!")

	g.db.add(existing)

	ma = ModAction(
		kind="update_emoji",
		user_id=v.id,
		_note=f'<img loading="lazy" data-bs-toggle="tooltip" alt=":{name}:" title=":{name}:" src="{SITE_FULL_IMAGES}/e/{name}.webp">'
	)
	g.db.add(ma)

	cache.delete(f"emojis_{existing.nsfw}")
	cache.delete(f"emoji_list_{existing.kind}_{existing.nsfw}")

	return {"message": f"'{name}' updated successfully!"}

@app.get("/admin/update/hats")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['UPDATE_ASSETS'])
def update_hats(v):
	return render_template("admin/update_assets.html", v=v, type="Hat")


@app.post("/admin/update/hats")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['UPDATE_ASSETS'])
def update_hat(v):
	name = request.values.get('name', '').strip()

	file = request.files["image"]
	new_name = request.values.get('new_name', '').strip()

	existing = g.db.query(HatDef).filter_by(name=name).one_or_none()
	if not existing:
		abort(400, "A hat with this name doesn't exist!")

	updated = False

	if new_name and existing.name != new_name:
		if not hat_name_regex.fullmatch(new_name):
			abort(400, "Invalid new name!")

		old_path = f"files/assets/images/hats/{existing.name}.webp"
		new_path = f"files/assets/images/hats/{new_name}.webp"
		rename(old_path, new_path)

		for x in IMAGE_FORMATS:
			original_old_path = f'/asset_submissions/hats/original/{existing.name}.{x}'
			original_new_path = f'/asset_submissions/hats/original/{new_name}.{x}'
			if path.isfile(original_old_path):
				rename(original_old_path, original_new_path)

		existing.name = new_name
		updated = True
		name = existing.name
	
	if file:
		if g.is_tor:
			abort(400, "Image uploads are not allowed through TOR!")
		if not file.content_type.startswith('image/'):
			abort(400, "You need to submit an image!")

		highquality = f"/asset_submissions/hats/{name}"
		file.save(highquality)
		process_image(highquality, v) #to ensure not malware

		with Image.open(highquality) as i:
			if i.width > 100 or i.height > 130:
				os.remove(highquality)
				abort(400, "Images must be 100x130")
			format = i.format.lower()

		new_path = f'/asset_submissions/hats/original/{name}.{format}'

		for x in IMAGE_FORMATS:
			if path.isfile(f'/asset_submissions/hats/original/{name}.{x}'):
				os.remove(f'/asset_submissions/hats/original/{name}.{x}')

		rename(highquality, new_path)

		filename = f"files/assets/images/hats/{name}.webp"
		copyfile(new_path, filename)
		process_image(filename, v, resize=100)
		purge_files_in_cloudflare_cache([f"{SITE_FULL_IMAGES}/i/hats/{name}.webp", f"{SITE_FULL_IMAGES}/asset_submissions/hats/original/{name}.{format}"])
		updated = True


	if not updated:
		abort(400, "You need to actually update something!")

	g.db.add(existing)

	ma = ModAction(
		kind="update_hat",
		user_id=v.id,
		_note=f'<a href="{SITE_FULL_IMAGES}/i/hats/{name}.webp">{name}</a>'
	)
	g.db.add(ma)

	return {"message": f"'{name}' updated successfully!"}
