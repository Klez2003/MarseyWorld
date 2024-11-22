from shutil import copyfile, move
import imagehash

from files.classes.art_submissions import *
from files.helpers.config.const import *
from files.helpers.media import *
from files.helpers.useractions import badge_grant
from files.routes.wrappers import *
from files.__main__ import app, limiter

@app.get("/submit/sidebar")
@app.get("/submit/banners")
@feature_required('ART_SUBMISSIONS')
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def submit_art(v):
	kind = request.path.split('/')[-1].rstrip('s')

	entries = g.db.query(ArtSubmission).filter(
		ArtSubmission.kind == kind,
		ArtSubmission.approved == False,
	).order_by(ArtSubmission.id.desc()).all()

	for entry in entries:
		entry.author = g.db.query(User.username).filter_by(id=entry.author_id).one()[0]
		entry.submitter = g.db.query(User.username).filter_by(id=entry.submitter_id).one()[0]

	return render_template("submit_art.html", v=v, entries=entries, kind=kind.title())


@app.post("/submit/art")
@feature_required('ART_SUBMISSIONS')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("20/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("20/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def submit_art_post(v):
	if g.is_tor:
		stop(400, "File uploads are not allowed through TOR!")

	file = request.files["image"]
	if not file or not file.content_type.startswith('image/'):
		stop(400, "You need to submit an image!")

	kind = request.values.get('kind', '').strip()
	if kind not in {"sidebar", "banner"}:
		stop(400, "Invalid kind!")

	username = request.values.get('author', '').lower().strip()
	author = get_user(username, v=v)

	hole = request.values.get('hole', '').lower().strip()
	if hole:
		if not g.db.get(Hole, hole):
			stop(404, "Hole not found!")
	else:
		hole = None

	entry = ArtSubmission(
				kind=kind,
				author_id=author.id,
				submitter_id=v.id,
				hole=hole,
			)
	g.db.add(entry)
	g.db.flush()

	highquality = f'/asset_submissions/art/{entry.id}.webp'
	file.save(highquality)
	process_image(highquality, v) #to ensure not malware

	# #to ensure under 2MB
	temp = f'/asset_submissions/art/{entry.id}-t.webp'
	copyfile(highquality, temp)
	try: process_image(temp, v, resize=entry.resize)
	except: 
		os.remove(highquality)
		stop(413, f"Max size for site assets is {MAX_IMAGE_SIZE_BANNER_RESIZED_MB} MB")
	os.remove(temp)

	if kind == "banner" and v.id != AEVANN_ID:
		with Image.open(highquality) as i:
			if i.width != 2000 or i.height != 200:
				os.remove(highquality)
				stop(400, "Banners must be 2000x200 px")

	path = f"files/assets/images/{SITE_NAME}/{entry.location_kind}"
	if not entry.hashes:
		for img in os.listdir(path):
			img_path = f'{path}/{img}'
			with Image.open(img_path) as i:
				i_hash = str(imagehash.phash(i))
			if i_hash not in entry.hashes.keys():
				entry.hashes[i_hash] = img_path

	with Image.open(highquality) as i:
		i_hash = str(imagehash.phash(i))
	if i_hash in entry.hashes.keys():
		os.remove(highquality)
		stop(400, f"Image already exists as a {entry.formatted_kind}!")


	return {"message": f"{entry.msg_kind} submitted successfully!"}


@app.post("/admin/approve/art/<int:id>")
@feature_required('ART_SUBMISSIONS')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@admin_level_required(PERMS['MODERATE_PENDING_SUBMITTED_ASSETS'])
def approve_art(v, id):
	comment = request.values.get("comment", "").strip()

	entry = g.db.get(ArtSubmission, id)
	if not entry:
		stop(404, "Art submission not found!")

	old = f'/asset_submissions/art/{entry.id}.webp'
	copyfile(old, f"/asset_submissions/art/original/{entry.id}.webp")

	hole = request.values.get('hole', '').lower().strip()
	if hole:
		hole = g.db.get(Hole, hole)
		if not hole:
			stop(404, "Hole not found!")

		filename = f'/images/{time.time()}'.replace('.','') + '.webp'
		entry_url = SITE_FULL_IMAGES + filename
		if entry.kind == "sidebar":
			hole.sidebarurls.append(f"{SITE_FULL_IMAGES}{filename}")
		else:
			hole.bannerurls.append(f"{SITE_FULL_IMAGES}{filename}")
	else:
		filename = f"files/assets/images/{SITE_NAME}/{entry.location_kind}/{entry.id}.webp"
		entry_url = f"{SITE_FULL_IMAGES}/i/{SITE_NAME}/{entry.location_kind}/{entry.id}.webp"

	copyfile(old, filename)
	process_image(filename, v, resize=entry.resize)
	os.remove(old)

	author = request.values.get('author').strip()
	author = get_user(author)
	entry.author_id = author.id
	g.db.add(entry)

	pay_reason = f'Reward for making <a href="{entry_url}">{entry.formatted_kind}</a>'
	author.pay_account('coins', 250, pay_reason)
	g.db.add(author)

	if v.id != author.id:
		msg = f"@{v.username} (a site admin) has approved a {entry.formatted_kind} you made:\n{entry_url}\n\nYou have received 250 coins as a reward!" 

		if comment:
			msg += f"\nComment:\n> {comment}"

		send_repeatable_notification(author.id, msg)

	if v.id != entry.submitter_id and author.id != entry.submitter_id:
		msg = f"@{v.username} (a site admin) has approved a {entry.formatted_kind} you submitted:\n{entry_url}" 
		
		if comment:
			msg += f"\nComment:\n> {comment}"

		send_repeatable_notification(entry.submitter_id, msg)


	note = entry_url
	if comment:
		note += f' - Comment: "{comment}"'

	ma = ModAction(
		kind=f"approve_{entry.kind}",
		user_id=v.id,
		target_user_id=entry.author_id,
		_note=note
	)
	g.db.add(ma)

	entry.approved = True

	all_by_author = g.db.query(ArtSubmission).filter_by(kind=entry.kind, author_id=author.id, approved=True).count()
	if all_by_author >= 99:
		badge_grant(badge_id=entry.badge_id_100, user=author)
	if all_by_author >= 9:
		badge_grant(badge_id=entry.badge_id_10, user=author)
	badge_grant(badge_id=entry.badge_id_1, user=author)

	return {"message": f"{entry.msg_kind} approved!"}

@app.post("/remove/art/<int:id>")
@feature_required('ART_SUBMISSIONS')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def remove_art(v, id):
	comment = request.values.get("comment", "").strip()

	entry = g.db.get(ArtSubmission, id)
	if not entry:
		stop(404, "Art submission not found!")

	if v.id != entry.submitter_id and v.admin_level < PERMS['MODERATE_PENDING_SUBMITTED_ASSETS']:
		stop(403)
	
	if v.id != entry.submitter_id:
		entry_url = f'{SITE_FULL_IMAGES}/asset_submissions/art/{entry.id}.webp'
		msg = f"@{v.username} (a site admin) has rejected a {entry.formatted_kind} you submitted:\n{entry_url}" 
		
		if comment:
			msg += f"\nComment:\n> {comment}"

		send_repeatable_notification(entry.submitter_id, msg)

		note = entry_url
		if comment:
			note += f' - Comment: "{comment}"'

		ma = ModAction(
			kind=f"reject_{entry.kind}",
			user_id=v.id,
			target_user_id=entry.author_id,
			_note=note
		)
		g.db.add(ma)

	if os.path.isfile(f'/asset_submissions/art/{entry.id}.webp'):
		os.remove(f'/asset_submissions/art/{entry.id}.webp')

	msg = f"{entry.msg_kind} removed!"
	g.db.delete(entry)

	return {"message": msg}
