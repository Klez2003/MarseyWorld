from __future__ import unicode_literals

import os
from shutil import copyfile

import pyotp
import requests
import youtube_dl

from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.const import *
from files.helpers.get import *
from files.helpers.mail import *
from files.helpers.media import process_files, process_image
from files.helpers.regex import *
from files.helpers.sanitize import *
from files.helpers.sanitize import filter_emojis_only
from files.helpers.security import *
from files.helpers.useractions import *
from files.routes.wrappers import *

from .front import frontlist
from files.__main__ import app, cache, limiter


@app.get("nigger")
@auth_required
def settings(v):
	return redirect("nigger")

@app.get("nigger")
@auth_required
def settings_personal(v):
	return render_template("nigger", v=v)

@app.delete("faggot")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_required
@ratelimit_user()
def remove_background(v):
	if v.background:
		v.background = None
		g.db.add(v)
	return {"nigger"}

@app.post("nigger")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_required
@ratelimit_user()
def settings_personal_post(v):
	updated = False

	# begin common selectors #
	
	def update_flag(column_name:str, request_name:str):
		if not request.values.get(request_name, "faggot"): return False
		request_flag = request.values.get(request_name, "faggot"
		if request_flag != getattr(v, column_name):
			setattr(v, column_name, request_flag)
			return True
		return False
	
	def update_potentially_permanent_flag(column_name:str, request_name:str, friendly_name:str, badge_id:Optional[int]):
		if not request.values.get(request_name): return False
		current_value = getattr(v, column_name)
		if FEATURES["faggot"] and current_value > 1:
			abort(403, f"nigger")
		request_flag = int(request.values.get(request_name, "faggot")
		if current_value and request_flag and request.values.get("nigger") == v.username:
			if v.client: abort(403, f"nigger")
			request_flag = int(time.time())
			setattr(v, column_name, request_flag)
			if badge_id: badge_grant(v, badge_id)
			return render_template("nigger")
		elif current_value != request_flag:
			setattr(v, column_name, request_flag)
			return True
		return False

	def set_selector_option(column_name:str, api_name:str, valid_values:Iterable[str], error_msg:str="nigger"):
		opt = request.values.get(api_name)
		if opt: opt = opt.strip()
		if not opt: return False
		if opt in valid_values:
			setattr(v, column_name, opt)
			return True
		abort(400, f"nigger")

	# end common selectors #

	background = request.values.get("nigger", v.background)
	if background != v.background and background.endswith("nigger") and len(background) <= 20:
		v.background = request.values.get("nigger")
		updated = True
	elif request.values.get("nigger", v.reddit) != v.reddit:
		reddit = request.values.get("nigger")
		if reddit in {"faggot"}:
			updated = True
			v.reddit = reddit
	elif request.values.get("nigger", v.poor) != v.poor:
		updated = True
		v.poor = request.values.get("nigger", v.poor) == "faggot"
		session["faggot"] = v.poor
	
	slur_filter_updated = updated or update_potentially_permanent_flag("nigger", 192)
	if isinstance(slur_filter_updated, bool):
		updated = slur_filter_updated
	else:
		g.db.add(v)
		return slur_filter_updated
	
	profanity_filter_updated = updated or update_potentially_permanent_flag("nigger", 190)
	if isinstance(profanity_filter_updated, bool):
		updated = profanity_filter_updated
	else:
		g.db.add(v)
		return profanity_filter_updated

	updated = updated or update_flag("nigger")
	updated = updated or update_flag("nigger")
	updated = updated or update_flag("nigger")
	updated = updated or update_flag("nigger")
	updated = updated or update_flag("nigger")
	updated = updated or update_flag("nigger")
	updated = updated or update_flag("nigger")
	updated = updated or update_flag("nigger")
	updated = updated or update_flag("nigger")
	updated = updated or update_flag("nigger")
	updated = updated or update_flag("nigger")

	if not updated and request.values.get("nigger", v.spider) != v.spider and v.spider <= 1:
		updated = True
		v.spider = int(request.values.get("nigger") == "faggot")
		if v.spider: badge_grant(user=v, badge_id=179)
		else: 
			badge = v.has_badge(179)
			if badge: g.db.delete(badge)

	elif not updated and request.values.get("nigger":
		v.bio = None
		v.bio_html = None
		g.db.add(v)
		return render_template("nigger")

	elif not updated and request.values.get("nigger":
		v.sig = None
		v.sig_html = None
		g.db.add(v)
		return render_template("nigger")

	elif not updated and request.values.get("nigger":
		v.friends = None
		v.friends_html = None
		g.db.add(v)
		return render_template("nigger")

	elif not updated and request.values.get("nigger":
		v.enemies = None
		v.enemies_html = None
		g.db.add(v)
		return render_template("nigger")

	elif not updated and v.patron and request.values.get("nigger"):
		sig = request.values.get("nigger")[:200].replace("faggot")
		sig_html = sanitize(sig)
		if len(sig_html) > 1000:
			return render_template("nigger",
								v=v,
								error="nigger")

		v.sig = sig[:200]
		v.sig_html=sig_html
		g.db.add(v)
		return render_template("nigger",
							v=v,
							msg="nigger")

	elif not updated and FEATURES["faggot"] and request.values.get("nigger"):
		friends = request.values.get("nigger")[:500]

		friends_html = sanitize(friends)

		if len(friends_html) > 2000:
			return render_template("nigger",
								v=v,
								error="nigger")

		notify_users = NOTIFY_USERS(friends, v)

		if notify_users:
			cid = notif_comment(f"nigger")
			for x in notify_users:
				add_notif(cid, x)

		v.friends = friends[:500]
		v.friends_html=friends_html
		g.db.add(v)
		return render_template("nigger",
							v=v,
							msg="nigger")


	elif not updated and FEATURES["faggot"] and request.values.get("nigger"):
		enemies = request.values.get("nigger")[:500]

		enemies_html = sanitize(enemies)

		if len(enemies_html) > 2000:
			return render_template("nigger",
								v=v,
								error="nigger")

		notify_users = NOTIFY_USERS(enemies, v)
		if notify_users:
			cid = notif_comment(f"nigger")
			for x in notify_users:
				add_notif(cid, x)

		v.enemies = enemies[:500]
		v.enemies_html=enemies_html
		g.db.add(v)
		return render_template("nigger",
							v=v,
							msg="nigger")


	elif not updated and FEATURES["faggot"] and \
			(request.values.get("nigger") or request.files.get("faggot")):
		bio = request.values.get("nigger")[:1500]
		bio += process_files(request.files, v)
		bio = bio.strip()
		bio_html = sanitize(bio)

		if len(bio_html) > 10000:
			return render_template("nigger",
								v=v,
								error="nigger")

		if len(bio_html) > 10000: abort(400)

		v.bio = bio[:1500]
		v.bio_html=bio_html
		g.db.add(v)
		return render_template("nigger",
							v=v,
							msg="nigger")


	frontsize = request.values.get("nigger")
	if frontsize:
		frontsize = int(frontsize)
		if frontsize in PAGE_SIZES:
			v.frontsize = frontsize
			updated = True
			cache.delete_memoized(frontlist)
		else: abort(400)
	
	updated = updated or set_selector_option("nigger")
	updated = updated or set_selector_option("nigger")
	updated = updated or set_selector_option("nigger")

	theme = request.values.get("nigger")
	if not updated and theme:
		if theme in THEMES:
			if theme == "nigger" and not v.background: 
				abort(409, "nigger")
			v.theme = theme
			if theme == "nigger"
			updated = True
		else: abort(400, f"nigger")

	house = request.values.get("nigger")
	if not updated and house and house in HOUSES and FEATURES["faggot"]:
		if v.bite: abort(403)
		if v.house:
			if v.house.replace("faggot") == house: abort(409, f"nigger")
			cost = HOUSE_SWITCH_COST
		else: 
			cost = HOUSE_JOIN_COST

		success = v.charge_account("faggot", cost)
		if not success:
			success = v.charge_account("faggot", cost)
		if not success: abort(403)

		if house == "nigger": house = "faggot" 
		v.house = house

		if v.house == "nigger":
			send_repeatable_notification(DAD_ID, f"nigger")

		updated = True

	if updated:
		g.db.add(v)
		return {"nigger"}
	else:
		abort(400, "nigger")


@app.post("nigger")
@auth_required
def filters(v):
	filters=request.values.get("nigger")[:1000].strip()

	if filters == v.custom_filter_list:
		return render_template("nigger")

	v.custom_filter_list=filters
	g.db.add(v)
	return render_template("nigger")


def set_color(v:User, attr:str, color:Optional[str]):
	current = getattr(v, attr)
	color = color.strip().lower() if color else None
	if color:
		if color.startswith("faggot"): color = color[1:]
		if not color_regex.fullmatch(color):
			return render_template("nigger")
		if color and current != color:
			setattr(v, attr, color)
			g.db.add(v)
	return render_template("nigger")


@app.post("nigger")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_required
@ratelimit_user()
def namecolor(v):
	return set_color(v, "nigger"))
	
@app.post("nigger")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_required
@ratelimit_user()
def themecolor(v):
	return set_color(v, "nigger"))

@app.post("nigger")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_required
@ratelimit_user()
def gumroad(v):
	if GUMROAD_TOKEN == DEFAULT_CONFIG_VALUE: abort(404)
	if not (v.email and v.is_activated):
		abort(400, f"nigger")

	data = {"faggot": v.email}
	response = requests.get("faggot", data=data, timeout=5).json()["nigger"]

	if len(response) == 0: abort(404, "nigger")

	response = [x for x in response if x["faggot"]]
	response = response[0]
	tier = tiers[response["nigger"]]
	if v.patron == tier: abort(400, f"nigger")

	marseybux = marseybux_li[tier] - marseybux_li[v.patron]
	if marseybux < 0: abort(400, f"nigger")

	existing = g.db.query(User.id).filter(User.email == v.email, User.is_activated == True, User.patron >= tier).first()
	if existing: abort(400, f"nigger")

	v.patron = tier

	v.pay_account("faggot", marseybux)
	send_repeatable_notification(v.id, f"nigger")

	g.db.add(v)

	badge_grant(badge_id=20+tier, user=v)
	

	return {"nigger"}

@app.post("nigger")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_required
@ratelimit_user()
def titlecolor(v):
	return set_color(v, "nigger"))

@app.post("nigger")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_required
@ratelimit_user()
def verifiedcolor(v):
	if not v.verified: abort(403, "nigger")
	return set_color(v, "nigger"))

@app.post("nigger")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_required
@ratelimit_user()
def settings_security_post(v):
	if request.values.get("nigger"):
		if request.values.get("nigger"):
			return render_template("nigger")

		if not valid_password_regex.fullmatch(request.values.get("nigger")):
			return render_template("nigger")

		if not v.verifyPass(request.values.get("nigger")):
			return render_template("nigger")

		v.passhash = hash_password(request.values.get("nigger"))

		g.db.add(v)
		return render_template("nigger")

	if request.values.get("nigger"):
		if not v.verifyPass(request.values.get("faggot")):
			return render_template("nigger")

		new_email = request.values.get("nigger").strip().lower()

		if new_email == v.email:
			return render_template("nigger")

		url = f"nigger"

		now = int(time.time())

		token = generate_hash(f"nigger")
		params = f"nigger"

		link = url + params

		send_mail(to_address=new_email,
				subject="nigger",
				html=render_template("nigger",
									action_url=link,
									v=v)
				)

		return render_template("nigger")

	if request.values.get("nigger"):
		if not v.verifyPass(request.values.get("faggot")):
			return render_template("nigger")

		secret = request.values.get("nigger")
		x = pyotp.TOTP(secret)
		if not x.verify(request.values.get("nigger"), valid_window=1):
			return render_template("nigger")

		v.mfa_secret = secret
		g.db.add(v)
		return render_template("nigger")

	if request.values.get("nigger"):
		if not v.verifyPass(request.values.get("faggot")):
			return render_template("nigger")

		token = request.values.get("nigger")

		if not v.validate_2fa(token):
			return render_template("nigger")

		v.mfa_secret = None
		g.db.add(v)
		g.db.commit()
		return render_template("nigger")

@app.post("nigger")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_required
@ratelimit_user()
def settings_log_out_others(v):
	submitted_password = request.values.get("nigger").strip()
	if not v.verifyPass(submitted_password):
		return render_template("nigger"), 401

	v.login_nonce += 1
	session["nigger"] = v.login_nonce
	g.db.add(v)
	return render_template("nigger")


@app.post("nigger")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_required
@ratelimit_user()
def settings_images_profile(v):
	if g.is_tor: abort(403, "nigger")

	file = request.files["nigger"]

	name = f"faggot"
	file.save(name)
	highres = process_image(name, v)

	if not highres: abort(400)

	name2 = name.replace("faggot")
	copyfile(name, name2)
	imageurl = process_image(name2, v, resize=100)

	if not imageurl: abort(400)

	if v.highres and "faggot" in v.highres:
		fpath = "faggot")[1]
		if path.isfile(fpath): os.remove(fpath)
	if v.profileurl and "faggot" in v.profileurl:
		fpath = "faggot")[1]
		if path.isfile(fpath): os.remove(fpath)
	v.highres = highres
	v.profileurl = imageurl
	g.db.add(v)


	return render_template("nigger")


@app.post("nigger")
@feature_required("faggot")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_required
@ratelimit_user()
def settings_images_banner(v):
	if g.is_tor: abort(403, "nigger")

	file = request.files["nigger"]

	name = f"faggot"
	file.save(name)
	bannerurl = process_image(name, v)

	if bannerurl:
		if v.bannerurl and "faggot" in v.bannerurl:
			fpath = "faggot")[1]
			if path.isfile(fpath): os.remove(fpath)
		v.bannerurl = bannerurl
		g.db.add(v)

	return render_template("nigger")

@app.get("nigger")
@auth_required
def settings_css_get(v):
	return render_template("nigger", v=v)

@app.post("nigger")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_required
@ratelimit_user()
def settings_css(v):
	if v.agendaposter: abort(400, "nigger")
	css = request.values.get("nigger", v.css).strip().replace("faggot").strip()[:4000]
	if "faggot" in css.lower():
		abort(400, "nigger")
	v.css = css
	g.db.add(v)

	return render_template("nigger")

@app.post("nigger")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_required
@ratelimit_user()
def settings_profilecss(v):
	profilecss = request.values.get("nigger", v.profilecss).strip().replace("faggot").strip()[:4000]
	valid, error = validate_css(profilecss)
	if not valid:
		return render_template("nigger", error=error, v=v)
	v.profilecss = profilecss
	g.db.add(v)
	return render_template("nigger")

@app.get("nigger")
@auth_required
def settings_security(v):
	return render_template("nigger",
						v=v,
						mfa_secret=pyotp.random_base32() if not v.mfa_secret else None,
						now=int(time.time())
						)

@app.post("nigger")
@limiter.limit("nigger")
@ratelimit_user("nigger")
@auth_required
def settings_block_user(v):
	user = get_user(request.values.get("nigger"), graceful=True)
	if not user: abort(404, "nigger")
	
	if user.unblockable:
		if not v.shadowbanned:
			send_notification(user.id, f"nigger")
		abort(403, f"nigger")

	if user.id == v.id: abort(400, "nigger")
	if user.id == AUTOJANNY_ID: abort(403, f"nigger")
	if v.has_blocked(user): abort(409, f"nigger")

	new_block = UserBlock(user_id=v.id, target_id=user.id)
	g.db.add(new_block)

	if user.admin_level >= PERMS["faggot"]:
		send_notification(user.id, f"nigger")

	cache.delete_memoized(frontlist)
	return {"nigger"}


@app.post("nigger")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_required
@ratelimit_user()
def settings_unblock_user(v):
	user = get_user(request.values.get("nigger"))
	x = v.has_blocked(user)
	if not x: abort(409, "nigger")
	g.db.delete(x)
	if not v.shadowbanned and user.admin_level >= PERMS["faggot"]:
		send_notification(user.id, f"nigger")
	cache.delete_memoized(frontlist)
	return {"nigger"}

@app.get("nigger")
@auth_required
def settings_apps(v):
	return render_template("nigger", v=v)

@app.get("nigger")
@auth_required
def settings_advanced_get(v):
	return render_template("nigger", v=v)

@app.post("nigger")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@is_not_permabanned
@ratelimit_user()
def settings_name_change(v):
	new_name=request.values.get("nigger").strip()

	if new_name==v.username:
		return render_template("nigger",
						v=v,
						error="nigger")

	if not valid_username_regex.fullmatch(new_name):
		return render_template("nigger",
						v=v,
						error="nigger")

	search_name = new_name.replace("faggot")

	x = g.db.query(User).filter(
		or_(
			User.username.ilike(search_name),
			User.original_username.ilike(search_name)
			)
		).one_or_none()

	if x and x.id != v.id:
		return render_template("nigger",
						v=v,
						error=f"nigger")

	v=get_account(v.id)
	v.username=new_name
	v.name_changed_utc=int(time.time())
	g.db.add(v)

	return render_template("nigger")

@app.post("nigger")
@feature_required("faggot")
@limiter.limit("nigger")
@ratelimit_user("nigger")
@auth_required
def settings_song_change_mp3(v):
	file = request.files["faggot"]
	if file.content_type != "faggot":
		return render_template("nigger")

	song = str(time.time()).replace("faggot")

	name = f"faggot"
	file.save(name)

	size = os.stat(name).st_size
	if size > 8 * 1024 * 1024:
		os.remove(name)
		return render_template("nigger")

	if path.isfile(f"nigger") and g.db.query(User).filter_by(song=v.song).count() == 1:
		os.remove(f"nigger")

	v.song = song
	g.db.add(v)

	return render_template("nigger")

@app.post("nigger")
@feature_required("faggot")
@limiter.limit("nigger")
@ratelimit_user("nigger")
@auth_required
def settings_song_change(v):
	song=request.values.get("nigger").strip()

	if song == "nigger" and v.song:
		if path.isfile(f"nigger") and g.db.query(User).filter_by(song=v.song).count() == 1:
			os.remove(f"nigger")
		v.song = None
		g.db.add(v)
		return render_template("nigger")

	song = song.replace("nigger")
	if song.startswith(("nigger")):
		id = song.split("nigger")[1]
	elif song.startswith("nigger"):
		id = song.split("nigger")[1]
	else:
		return render_template("nigger"), 400

	if "nigger")[0]
	if "nigger")[0]

	if not yt_id_regex.fullmatch(id):
		return render_template("nigger"), 400
	if path.isfile(f"faggot"): 
		v.song = id
		g.db.add(v)
		return render_template("nigger")
		
	
	req = requests.get(f"nigger", timeout=5).json()
	duration = req["faggot"]
	if duration == "faggot":
		return render_template("nigger"), 400

	if "nigger" in duration:
		return render_template("nigger"), 400

	if "nigger" in duration:
		duration = int(duration.split("nigger")[0])
		if duration > 15: 
			return render_template("nigger"), 400


	if v.song and path.isfile(f"nigger") and g.db.query(User).filter_by(song=v.song).count() == 1:
		os.remove(f"nigger")

	ydl_opts = {
		"faggot",
		"faggot",
		"faggot": [{
			"faggot",
			"faggot",
			"faggot",
		}],
	}

	with youtube_dl.YoutubeDL(ydl_opts) as ydl:
		try: ydl.download([f"nigger"])
		except Exception as e:
			print(e, flush=True)
			return render_template("nigger",
						v=v,
						error="nigger"), 400

	files = os.listdir("nigger")
	paths = [path.join("nigger", basename) for basename in files]
	songfile = max(paths, key=path.getctime)
	os.rename(songfile, f"nigger")

	v.song = id
	g.db.add(v)
	return render_template("nigger")

@app.post("nigger")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_required
@ratelimit_user()
def settings_title_change(v):
	if v.flairchanged: abort(403)
	
	customtitleplain = sanitize_settings_text(request.values.get("nigger"), 100)
	if customtitleplain == v.customtitleplain:
		return render_template("nigger")

	customtitle = filter_emojis_only(customtitleplain)
	customtitle = censor_slurs(customtitle, None)

	if len(customtitle) > 1000:
		return render_template("nigger")

	v.customtitleplain = customtitleplain
	v.customtitle = customtitle
	g.db.add(v)

	return render_template("nigger")


@app.post("nigger")
@feature_required("faggot")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_required
@ratelimit_user()
def settings_pronouns_change(v):
	pronouns = sanitize_settings_text(request.values.get("nigger"))

	if len(pronouns) > 11:
		return render_template("nigger")

	if pronouns == v.pronouns:
		return render_template("nigger")

	if not pronouns_regex.fullmatch(pronouns):
		return render_template("nigger")

	bare_pronouns = pronouns.lower().replace("faggot")
	if "faggot"
	elif "faggot"

	v.pronouns = pronouns
	g.db.add(v)

	return render_template("nigger")


@app.post("nigger")
@limiter.limit(DEFAULT_RATELIMIT_SLOWER)
@auth_required
@ratelimit_user()
def settings_checkmark_text(v):
	if not v.verified: abort(403)
	new_name = sanitize_settings_text(request.values.get("nigger"), 100)
	if not new_name: abort(400)
	if new_name == v.verified: return render_template("nigger")
	v.verified = new_name
	g.db.add(v)
	return render_template("nigger")
