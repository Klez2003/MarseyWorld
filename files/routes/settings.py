from __future__ import unicode_literals

import os
from shutil import copyfile

import pyotp
import requests
import yt_dlp
from calendar import timegm

from sqlalchemy.orm import load_only

from files.helpers.actions import *
from files.helpers.alerts import *
from files.helpers.config.const import *
from files.helpers.slurs_and_profanities import censor_slurs_profanities
from files.helpers.get import *
from files.helpers.mail import *
from files.helpers.media import *
from files.helpers.regex import *
from files.helpers.sanitize import *
from files.helpers.sanitize import filter_emojis_only
from files.helpers.security import *
from files.helpers.useractions import *
from files.routes.wrappers import *

from .front import frontlist
from files.__main__ import app, cache, limiter


@app.get("/settings")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings(v):
	return redirect("/settings/personal")

@app.get("/settings/personal")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_personal(v):
	return render_template("settings/personal.html", v=v, msg=get_msg(), error=get_error())

@app.post('/settings/remove_background')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def remove_background(v):
	if v.background:
		remove_image_using_link(v.background)
		v.background = None
		g.db.add(v)
	return {"message": "Background removed!"}

@app.post('/settings/remove_flag')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def remove_flag(v):
	if v.flag:
		v.flag = None
		g.db.add(v)
	return {"message": "Flag removed!"}

@app.post('/settings/custom_background')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def upload_custom_background(v):
	if g.is_tor: stop(403, "File uploads are not allowed through TOR!")

	if not v.patron:
		stop(403, f"Custom site backgrounds are only available to {patron}s!")

	file = request.files["file"]

	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	background = process_image(name, v)

	if background:
		remove_image_using_link(v.background)
		v.background = background
		g.db.add(v)

	return redirect('/settings/personal')

def notify_removed_users(removed_users, kind):
	if removed_users and removed_users != 'everyone':
		text = f"@{g.v.username} has removed you from their {kind} list!"
		cid = notif_comment(text)
		for x in removed_users:
			add_notif(cid, x, text, pushnotif_url=f'{SITE_FULL}{g.v.url}')

@app.post("/settings/personal")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_personal_post(v):
	updated = False

	# begin common selectors #

	def update_flag(column_name, request_name):
		if not request.values.get(request_name, ''): return False
		request_flag = request.values.get(request_name, '') == 'true'
		if request_flag != getattr(v, column_name):
			setattr(v, column_name, request_flag)
			return True
		return False

	def update_potentially_permanent_flag(column_name, request_name, friendly_name, badge_id):
		if not request.values.get(request_name): return False
		current_value = getattr(v, column_name)
		if FEATURES['USERS_PERMANENT_WORD_FILTERS'] and current_value > 1:
			stop(403, f"Cannot change the {friendly_name} setting after you've already set it permanently!")
		request_flag = int(request.values.get(request_name, '') == 'true')
		if current_value and request_flag and request.values.get("permanent", '') == 'true' and request.values.get("username") == v.username:
			if v.client: stop(403, f"Cannot set {friendly_name} permanently from the API")
			request_flag = int(time.time())
			setattr(v, column_name, request_flag)
			if badge_id: badge_grant(v, badge_id)
			return {"message": f"You have set the {friendly_name} permanently! Enjoy your new badge!"}
		elif current_value != request_flag:
			setattr(v, column_name, request_flag)
			return True
		return False

	def set_selector_option(column_name, api_name, valid_values, error_msg="value"):
		opt = request.values.get(api_name)
		if opt: opt = opt.strip()
		if not opt: return False
		if opt in valid_values.keys():
			setattr(v, column_name, opt)
			return True
		stop(400, f"'{opt}' is not a valid {error_msg}")

	# end common selectors #

	background = request.values.get("background", v.background)
	if background != v.background and background.endswith(".webp") and len(background) <= 20:
		v.background = '/i/backgrounds/' + request.values.get("background")
		updated = True
	elif request.values.get("reddit", v.reddit) != v.reddit:
		reddit = request.values.get("reddit")
		if reddit in {'old.reddit.com', 'new.reddit.com', 'sh.reddit.com', 'reddit.com', 'undelete.pullpush.io'}:
			updated = True
			v.reddit = reddit
	elif request.values.get("poor", v.poor) != v.poor:
		updated = True
		session['poor'] = request.values.get("poor", v.poor) == 'true'
		if session['poor']:
			v.show_sigs = False
			if v.frontsize > 25:
				v.frontsize = 25

	slur_filter_updated = updated or update_potentially_permanent_flag("slurreplacer", "slurreplacer", "slur replacer", 192)
	if isinstance(slur_filter_updated, bool):
		updated = slur_filter_updated
	else:
		g.db.add(v)
		return slur_filter_updated

	profanity_filter_updated = updated or update_potentially_permanent_flag("profanityreplacer", "profanityreplacer", "profanity replacer", 190)
	if isinstance(profanity_filter_updated, bool):
		updated = profanity_filter_updated
	else:
		g.db.add(v)
		return profanity_filter_updated

	updated = updated or update_flag("hidevotedon", "hidevotedon")
	updated = updated or update_flag("hide_cw", "hide_cw")
	updated = updated or update_flag("newtab", "newtab")
	updated = updated or update_flag("newtabexternal", "newtabexternal")
	updated = updated or update_flag("imgsed", "imgsed")
	updated = updated or update_flag("controversial", "controversial")
	updated = updated or update_flag("show_sigs", "show_sigs")
	updated = updated or update_flag("private_posts", "private_posts")
	updated = updated or update_flag("private_comments", "private_comments")
	updated = updated or update_flag("lifetimedonated_visible", "lifetimedonated_visible")
	updated = updated or update_flag("hole_creation_notifs", "hole_creation_notifs")
	updated = updated or update_flag("group_creation_notifs", "group_creation_notifs")
	updated = updated or update_flag("effortpost_notifs", "effortpost_notifs")

	if not updated and request.values.get("spider", v.spider) != v.spider and v.spider <= 1:
		updated = True
		v.spider = int(request.values.get("spider") == 'true')
		if v.spider: badge_grant(user=v, badge_id=179)
		else:
			badge = v.has_badge(179)
			if badge: g.db.delete(badge)

	elif not updated and v.offsite_mentions != None and request.values.get("offsite_mentions", v.offsite_mentions) != v.offsite_mentions:
		updated = True
		v.offsite_mentions = int(request.values.get("offsite_mentions") == 'true')
		if v.offsite_mentions: badge_grant(user=v, badge_id=140)
		else:
			badge = v.has_badge(140)
			if badge: g.db.delete(badge)

	elif not updated and request.values.get("cursormarsey", v.cursormarsey) != v.cursormarsey:
		updated = True
		session["cursormarsey"] = int(request.values.get("cursormarsey") == 'true')

	elif not updated and request.values.get("nsfw_warnings", v.nsfw_warnings) != v.nsfw_warnings:
		updated = True
		session["nsfw_warnings"] = int(request.values.get("nsfw_warnings") == 'true')

	elif not updated and IS_MUSICAL_EVENT() and request.values.get("event_music", v.event_music) != v.event_music:
		if not v.grinch:
			stop(403, "You need to award yourself the grinch award to be able to disable event music!")
		updated = True
		session['event_music'] = request.values.get("event_music", v.event_music) == 'true'

	elif not updated and request.values.get("marsify", v.marsify) != v.marsify and v.marsify <= 1:
		if not v.patron and v.marsify != 1:
			stop(403, f"Perma-marsify is only available to {patron}s!")
		updated = True
		v.marsify = int(request.values.get("marsify") == 'true')
		if v.marsify: badge_grant(user=v, badge_id=170)
		else:
			badge = v.has_badge(170)
			if badge: g.db.delete(badge)

	elif not updated and request.values.get("bio") == "" and not request.files.get('file'):
		v.bio = None
		v.bio_html = None
		g.db.add(v)
		return {"message": "Your bio has been updated."}

	elif not updated and request.values.get("sig") == "":
		v.sig = None
		v.sig_html = None
		g.db.add(v)
		return {"message": "Your sig has been updated."}

	elif not updated and request.values.get("friends") == "" and v.friends:
		removed_users = NOTIFY_USERS(v.friends, v, charge=False)
		notify_removed_users(removed_users, 'friends')
		v.friends = None
		v.friends_html = None
		g.db.add(v)
		return {"message": "Your friends list has been updated."}

	elif not updated and request.values.get("enemies") == "" and v.enemies:
		removed_users = NOTIFY_USERS(v.enemies, v, charge=False)
		notify_removed_users(removed_users, 'enemies')
		v.enemies = None
		v.enemies_html = None
		g.db.add(v)
		return {"message": "Your enemies list has been updated."}

	elif not updated and request.values.get("sig"):
		if v.patron < 3:
			stop(403, f"Signatures are only available to {patron}s donating $10/month or higher!")

		sig = request.values.get("sig").replace('\n','').replace('\r','').strip()
		sig = process_files(request.files, v, sig)
		sig = sig.strip()

		if len(sig) > 200:
			stop(400, "New signature is too long (max 200 characters)")

		sig_html = sanitize(sig, blackjack="signature")
		if len(sig_html) > 1000:
			stop(400, "Your rendered sig is too long!")

		v.sig = sig
		v.sig_html = sig_html
		g.db.add(v)
		return {"message": "Your sig has been updated."}

	elif not updated and FEATURES['USERS_PROFILE_BODYTEXT'] and request.values.get("friends"):
		friends = request.values.get("friends", "").strip()
		if len(friends) > BIO_FRIENDS_ENEMIES_LENGTH_LIMIT:
			stop(400, f'Your friend list is too long (max {BIO_FRIENDS_ENEMIES_LENGTH_LIMIT} characters)')

		friends_html = sanitize(friends, blackjack="friends")
		if len(friends_html) > BIO_FRIENDS_ENEMIES_HTML_LENGTH_LIMIT:
			stop(400, "Your rendered friend list is too long!")

		notify_users = NOTIFY_USERS(friends, v, oldtext=v.friends)
		if notify_users:
			text = f"@{v.username} has added you to their friends list!"
			cid = notif_comment(text)
			if notify_users == 'everyone':
				alert_everyone(cid)
			else:
				for x in notify_users:
					add_notif(cid, x, text, pushnotif_url=f'{SITE_FULL}{v.url}')

		if v.friends:
			try:
				removed_users = NOTIFY_USERS(v.friends, v, charge=False) - NOTIFY_USERS(friends, v, charge=False)
			except TypeError:
				pass
			else:
				notify_removed_users(removed_users, 'friends')

		v.friends = friends
		v.friends_html=friends_html
		g.db.add(v)
		return {"message": "Your friends list has been updated."}


	elif not updated and FEATURES['USERS_PROFILE_BODYTEXT'] and request.values.get("enemies"):
		enemies = request.values.get("enemies", "").strip()
		if len(enemies) > BIO_FRIENDS_ENEMIES_LENGTH_LIMIT:
			stop(400, f'You enemy list is too long (max {BIO_FRIENDS_ENEMIES_LENGTH_LIMIT} characters)')

		enemies_html = sanitize(enemies, blackjack="enemies")
		if len(enemies_html) > BIO_FRIENDS_ENEMIES_HTML_LENGTH_LIMIT:
			stop(400, "Your rendered enemy list is too long!")

		notify_users = NOTIFY_USERS(enemies, v, oldtext=v.enemies)
		if notify_users:
			text = f"@{v.username} has added you to their enemies list!"
			cid = notif_comment(text)
			if notify_users == 'everyone':
				alert_everyone(cid)
			else:
				for x in notify_users:
					add_notif(cid, x, text, pushnotif_url=f'{SITE_FULL}{v.url}')

		if v.enemies:
			try:
				removed_users = NOTIFY_USERS(v.enemies, v, charge=False) - NOTIFY_USERS(enemies, v, charge=False)
			except TypeError:
				pass
			else:
				notify_removed_users(removed_users, 'enemies')

		v.enemies = enemies
		v.enemies_html=enemies_html
		g.db.add(v)
		return {"message": "Your enemies list has been updated."}


	elif not updated and FEATURES['USERS_PROFILE_BODYTEXT'] and (request.values.get("bio") or request.files.get('file')):
		bio = request.values.get("bio", "").strip()
		bio = process_files(request.files, v, bio)
		if len(bio) > BIO_FRIENDS_ENEMIES_LENGTH_LIMIT:
			stop(400, f'Your bio is too long (max {BIO_FRIENDS_ENEMIES_LENGTH_LIMIT} characters)')

		bio_html = sanitize(bio, blackjack="bio")
		if len(bio_html) > BIO_FRIENDS_ENEMIES_HTML_LENGTH_LIMIT:
			stop(400, "Your rendered bio is too long!")

		v.bio = bio
		v.bio_html = bio_html
		g.db.add(v)
		return {"message": "Your bio has been updated."}


	frontsize = request.values.get("frontsize")
	if frontsize:
		frontsize = int(frontsize)
		if frontsize in PAGE_SIZES:
			v.frontsize = frontsize
			updated = True
			cache.delete_memoized(frontlist)
		else: stop(400)

	updated = updated or set_selector_option("defaultsortingcomments", "defaultsortingcomments", COMMENT_SORTS, "comment sort")
	updated = updated or set_selector_option("defaultsorting", "defaultsorting", POST_SORTS, "post sort")
	updated = updated or set_selector_option("defaulttime", "defaulttime", TIME_FILTERS, "time filter")

	theme = request.values.get("theme")
	if not updated and theme:
		if theme in THEMES:
			if v.theme == "win98": v.themecolor = DEFAULT_COLOR
			v.theme = theme
			if theme == "win98": v.themecolor = "30409f"
			updated = True
		else: stop(400, f"{theme} is not a valid theme")

	house = request.values.get("house")
	if not updated and house and house in ["None"]+HOUSES and FEATURES['HOUSES']:
		if v.bite: stop(403)
		if v.house:
			if v.house.replace(' Founder', '') == house: stop(409, f"You're already in House {house}")
			cost = HOUSE_SWITCH_COST
		else:
			cost = HOUSE_JOIN_COST

		success = v.charge_account('coins/marseybux', cost, "Cost of changing houses")
		if not success: stop(403)

		if house == "None":
			house = ''

		v.house = house

		updated = True

	if updated:
		g.db.add(v)
		return {"message": "Your settings have been updated!"}
	else:
		stop(400, "You didn't change anything!")


@app.post("/settings/filters")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def filters(v):
	filters = request.values.get("filters", "").strip()

	if len(filters) > 1000:
		stop(400, "Filters are too long (max 1000 characters)")

	if filters in {"", "None"}:
		filters = None

	if filters == v.custom_filter_list:
		stop(400, "You didn't change anything!")

	v.custom_filter_list = filters
	g.db.add(v)
	return {"message": "Your custom filters have been updated!"}

@app.post("/settings/keyword_notifs")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def keyword_notifs(v):
	if v.patron < 5:
		stop(403, f"Keyword notifications are only available to {patron}s donating $50/month or higher!")

	keyword_notifs = request.values.get("keyword_notifs", "").replace('\r','').strip('\n')

	if keyword_notifs == v.keyword_notifs:
		stop(400, "You didn't change anything!")

	if len(keyword_notifs) > 1000:
		stop(400, "Keywords are too long (max 1000 characters)")

	if not keyword_notifs:
		keywords_notifs = None

	v.keyword_notifs = keyword_notifs
	g.db.add(v)
	return {"message": "Your keyword notifications have been updated!"}

@app.post("/settings/snappy_quotes")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def snappy_quotes(v):
	if v.patron < 5:
		stop(403, f"Custom Snappy quotes are only available to {patron}s donating $50/month or higher!")

	snappy_quotes = request.values.get("snappy_quotes", "").replace('\r','').strip()

	if snappy_quotes.endswith('[para]'):
		snappy_quotes = snappy_quotes[:-6].strip()

	if snappy_quotes == v.snappy_quotes:
		stop(400, "You didn't change anything!")

	if len(snappy_quotes) > USER_SNAPPY_QUOTES_LENGTH:
		stop(400, f"Quotes are too long (max {USER_SNAPPY_QUOTES_LENGTH} characters)")

	if not snappy_quotes:
		snappy_quotes = None

	v.snappy_quotes = snappy_quotes
	g.db.add(v)
	return {"message": "Your custom Snappy quotes have been updated!"}



def set_color(v, attr):
	color = request.values.get(attr)
	current = getattr(v, attr)
	color = color.strip().lower() if color else None
	if color:
		if color.startswith('#'): color = color[1:]
		if not color_regex.fullmatch(color):
			return render_template("settings/personal.html", v=v, error="Invalid color hex code!")
		if color and current != color:
			setattr(v, attr, color)
			g.db.add(v)
	return render_template("settings/personal.html", v=v, msg="Color successfully updated!")


@app.post("/settings/namecolor")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def namecolor(v):
	return set_color(v, "namecolor")

@app.post("/settings/themecolor")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def themecolor(v):
	return set_color(v, "themecolor")

@app.post("/settings/flaircolor")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def flaircolor(v):
	return set_color(v, "flaircolor")

@app.post("/settings/verifiedcolor")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def verifiedcolor(v):
	if not v.verified: stop(403, "You don't have a checkmark to edit its color!")
	return set_color(v, "verifiedcolor")

@app.post("/settings/security")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit('10/day', deduct_when=lambda response: response.status_code < 400)
@limiter.limit('10/day', deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_security_post(v):
	if request.values.get("new_password"):
		if request.values.get("new_password") != request.values.get("cnf_password"):
			stop(400, "Passwords do not match!")

		if not valid_password_regex.fullmatch(request.values.get("new_password")):
			stop(400, "Password must be between 8 and 100 characters!")

		if not v.verifyPass(request.values.get("old_password")):
			stop(400, "Incorrect password")

		v.passhash = hash_password(request.values.get("new_password"))

		g.db.add(v)
		return {"message": "Your password has been changed successfully!"}

	if request.values.get("new_email"):
		if not v.verifyPass(request.values.get('password')):
			return render_template("settings/security.html", v=v, error="Invalid password!")

		new_email = request.values.get("new_email","").strip().lower()

		if new_email == v.email:
			return render_template("settings/security.html", v=v, error="This email is already yours!")

		url = f"{SITE_FULL}/activate"

		now = int(time.time())

		token = generate_hash(f"{new_email}+{v.id}+{now}")
		params = f"?email={quote(new_email)}&id={v.id}&time={now}&token={token}"

		link = url + params

		send_mail(to_address=new_email,
				subject="Verify your email address.",
				html=render_template("email/email_change.html", action_url=link, v=v),
				)

		return render_template("settings/security.html", v=v, msg="We have sent you an email, click the verification link inside it to complete the email change. Please check your spam folder if you can't find it!")

	if request.values.get("2fa_token"):
		if not v.verifyPass(request.values.get('password')):
			stop(400, "Invalid password!")

		secret = request.values.get("2fa_secret")
		x = pyotp.TOTP(secret)
		if not x.verify(request.values.get("2fa_token"), valid_window=1):
			stop(400, "Invalid token!")

		v.mfa_secret = secret
		g.db.add(v)
		return {"message": "Two-factor authentication enabled!"}

	if request.values.get("2fa_remove"):
		if not v.verifyPass(request.values.get('password')):
			stop(400, "Invalid password!")

		if v.mfa_secret:
			token = request.values.get("2fa_remove")
			if not token or not v.validate_2fa(token):
				stop(400, "Invalid token!")
			v.mfa_secret = None
			g.db.add(v)

		return {"message": "Two-factor authentication disabled!"}

@app.post("/settings/log_out_all_others")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_log_out_others(v):
	submitted_password = request.values.get("password", "").strip()
	if not v.verifyPass(submitted_password):
		stop(400, "Incorrect password!")

	v.login_nonce += 1
	session["login_nonce"] = v.login_nonce
	g.db.add(v)

	return {"message": "All other devices have been logged out!"}


@app.post("/settings/images/profile")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_images_profile(v):
	if g.is_tor: stop(403, "File uploads are not allowed through TOR!")

	file = request.files["profile"]

	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	highres = process_image(name, v)

	if not highres: stop(400)

	name2 = name.replace('.webp', 'r.webp')
	copyfile(name, name2)
	imageurl = process_image(name2, v, resize=100)

	if not imageurl: stop(400)

	remove_image_using_link(v.highres)
	remove_image_using_link(v.profileurl)

	v.highres = highres
	v.profileurl = imageurl
	g.db.add(v)

	cache.delete_memoized(get_profile_picture, v.id)
	cache.delete_memoized(get_profile_picture, v.username)
	cache.delete_memoized(get_profile_picture, v.original_username)
	cache.delete_memoized(get_profile_picture, v.extra_username)
	cache.delete_memoized(get_profile_picture, v.prelock_username)

	return redirect("/settings/personal?msg=Profile picture successfully updated!")


@app.post("/settings/images/banner")
@feature_required('USERS_PROFILE_BANNER')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_images_banner(v):
	if g.is_tor: stop(403, "File uploads are not allowed through TOR!")

	file = request.files["banner"]

	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	bannerurl = process_image(name, v)

	if bannerurl:
		remove_image_using_link(v.bannerurl)
		v.bannerurl = bannerurl
		g.db.add(v)

	return redirect("/settings/personal?msg=Banner successfully updated!")


@app.post("/settings/images/profile_background")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_images_profile_background(v):
	if g.is_tor: stop(403, "File uploads are not allowed through TOR!")

	file = request.files["profile_background"]

	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	file.save(name)
	profile_background = process_image(name, v)

	if profile_background:
		remove_image_using_link(v.profile_background)
		v.profile_background = profile_background
		g.db.add(v)
		badge_grant(badge_id=193, user=v)

	return redirect("/settings/personal?msg=Profile background successfully updated!")

@app.get("/settings/css")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_css_get(v):
	return render_template("settings/css.html", v=v, profilecss=v.profilecss)

@app.post("/settings/css")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_css(v):
	if v.chud:
		stop(400, "Chudded users can't edit CSS!")

	css = request.values.get("css", v.css).strip()

	if len(css) > CSS_LENGTH_LIMIT:
		stop(400, f"CSS is too long (max {CSS_LENGTH_LIMIT} characters)")

	v.css = css
	g.db.add(v)
	return {"message": "Custom CSS successfully updated!"}

@app.post("/settings/profilecss")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_profilecss(v):
	profilecss = request.values.get("profilecss", v.profilecss).strip()

	if len(profilecss) > CSS_LENGTH_LIMIT:
		stop(400, f"Profile CSS is too long (max {CSS_LENGTH_LIMIT} characters)")

	valid, error = validate_css(profilecss)
	if not valid:
		stop(400, error)
	v.profilecss = profilecss
	g.db.add(v)
	return {"message": "Profile CSS successfully updated!"}

@app.get("/settings/security")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_security(v):
	return render_template("settings/security.html",
						v=v,
						mfa_secret=pyotp.random_base32() if not v.mfa_secret else None,
						now=int(time.time()),
						)

@app.get("/settings/blocks")
@auth_required
def settings_blocks(v):
	return redirect(f'/@{v.username}/blocking')

@app.post("/block_user")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("20/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("20/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_block_user(v):
	if v.unblockable:
		stop(403, "You're unblockable so you can't block others!")

	user = get_user(request.values.get("username"))

	if user.unblockable:
		send_notification(user.id, f"@{v.username} has tried to block you and failed because of your unblockable status!")
		g.db.commit()
		stop(403, f"@{user.username} is unblockable!")

	if user.id == v.id: stop(400, "You can't block yourself")
	if user.id == AUTOJANNY_ID: stop(403, f"You can't block @{user.username}")
	if v.has_blocked(user): stop(409, f"You have already blocked @{user.username}")

	new_block = UserBlock(user_id=v.id, target_id=user.id)
	g.db.add(new_block)

	send_notification(user.id, f"@{v.username} has blocked you!")

	cache.delete_memoized(frontlist)
	return {"message": f"@{user.username} blocked!"}


@app.post("/unblock_user")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_unblock_user(v):
	user = get_user(request.values.get("username"))
	x = v.has_blocked(user)
	if not x: stop(409, "You can't unblock someone you haven't blocked")
	g.db.delete(x)

	send_notification(user.id, f"@{v.username} has unblocked you!")

	cache.delete_memoized(frontlist)
	return {"message": f"@{user.username} unblocked successfully!"}

@app.get("/settings/apps")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_apps(v):
	return render_template("settings/apps.html", v=v)

@app.get("/settings/advanced")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_advanced_get(v):
	return render_template("settings/advanced.html", v=v)

@app.post("/settings/name_change")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_name_change(v):
	if SITE == 'rdrama.net' and v.id == 10489:
		stop(403)

	if v.namechanged: stop(403)

	new_name = request.values.get("name", "").strip()

	if new_name == v.username:
		stop(400, "You didn't change anything")

	if v.patron >= 4:
		used_regex = valid_username_patron_regex
	else:
		used_regex = valid_username_regex

	if not used_regex.fullmatch(new_name):
		stop(400, "This isn't a valid username.")

	if new_name.title() in GIRL_NAMES_TOTAL:
		stop(400, "This name is reserved for a site award.")

	existing = get_user(new_name, graceful=True)

	if existing and existing.id != v.id:
		stop(400, f"Username `{new_name}` is already in use.")

	if v.patron >= 4 and v.username != v.original_username and not (v.extra_username and len(v.extra_username) <= 3):
		v.extra_username = v.username

	v.username = new_name

	if new_name.lower() == v.original_username.lower() or (v.unban_utc and v.unban_utc >= 32400000000):
		v.original_username = new_name

	g.db.add(v)

	execute_blackjack(v, None, v.username, 'username')
	check_name(v)

	return {"message": "Name successfully changed!"}


@app.post("/settings/flag_change")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("10/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("10/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_flag_change(v):
	new_flag = request.values.get("flag", "").strip(':').strip()

	if new_flag == v.flag:
		stop(400, "You didn't change anything")

	emoji = g.db.query(Emoji).filter_by(kind='Marsey Flags', name=new_flag).one_or_none()
	if not emoji:
		stop(400, "This isn't a valid flag.")

	v.flag = new_flag
	g.db.add(v)

	emoji.count += 1
	g.db.add(emoji)

	return {"message": "Your flag has been updated."}


@app.post("/settings/song_change_mp3")
@feature_required('USERS_PROFILE_SONG')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("10/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("10/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_song_change_mp3(v):
	file = request.files['file']
	if file.content_type != 'audio/mpeg':
		return redirect("/settings/personal?error=Not a valid MP3 file!")

	song = str(time.time()).replace('.','')

	process_audio(file, v, f'/songs/{song}') #to ensure not malware

	if g.db.query(User).filter_by(song=v.song).count() == 1 and path.isfile(f"/songs/{v.song}.mp3") :
		os.remove(f"/songs/{v.song}.mp3")

	v.song = song
	g.db.add(v)

	return redirect("/settings/personal?msg=Profile Anthem successfully updated!")


def _change_song_youtube(vid, id):
	ydl_opts = {
		'cookiefile': '/cookies',
		'outtmpl': '/temp_songs/%(id)s.%(ext)s',
		'format': 'bestaudio/best',
		'postprocessors': [{
			'key': 'FFmpegExtractAudio',
			'preferredcodec': 'mp3',
			'preferredquality': '192',
		}],
	}

	with yt_dlp.YoutubeDL(ydl_opts) as ydl:
		try: ydl.download([f"https://youtube.com/watch?v={id}"])
		except Exception as e:
			print(e, flush=True)
			return

	os.rename(f"/temp_songs/{id}.mp3", f"/songs/{id}.mp3")

	db = db_session()

	v = db.query(User).filter_by(id=vid).options(load_only(User.song)).one()

	if v.song and db.query(User).filter_by(song=v.song).count() == 1 and path.isfile(f"/songs/{v.song}.mp3") :
		os.remove(f"/songs/{v.song}.mp3")

	v.song = id
	db.add(v)
	db.commit()
	db.close()
	stdout.flush()


@app.post("/settings/song_change")
@feature_required('USERS_PROFILE_SONG')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit("10/day", deduct_when=lambda response: response.status_code < 400)
@limiter.limit("10/day", deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_song_change(v):
	song = request.values.get("song").strip()

	if song == "" and v.song:
		if g.db.query(User).filter_by(song=v.song).count() == 1 and path.isfile(f"/songs/{v.song}.mp3") :
			os.remove(f"/songs/{v.song}.mp3")
		v.song = None
		g.db.add(v)
		return redirect("/settings/personal?msg=Profile Anthem successfully removed!")

	song = song.replace("https://music.youtube.com", "https://youtube.com")
	if song.startswith(("https://www.youtube.com/watch?v=", "https://youtube.com/watch?v=", "https://m.youtube.com/watch?v=")):
		id = song.split("v=")[1]
	elif song.startswith("https://youtu.be/"):
		id = song.split("https://youtu.be/")[1]
	else:
		return redirect("/settings/personal?error=Not a YouTube link!")

	if "?" in id: id = id.split("?")[0]
	if "&" in id: id = id.split("&")[0]

	if not yt_id_regex.fullmatch(id):
		return redirect("/settings/personal?error=Not a YouTube link!")

	if path.isfile(f'/songs/{id}.mp3'):
		v.song = id
		g.db.add(v)
		return redirect("/settings/personal?msg=Profile Anthem successfully updated!")


	if YOUTUBE_KEY != DEFAULT_CONFIG_VALUE:
		req = requests.get(f"https://www.googleapis.com/youtube/v3/videos?id={id}&key={YOUTUBE_KEY}&part=contentDetails", headers=HEADERS, timeout=5).json()

		try:
			duration = req['items'][0]['contentDetails']['duration']
		except:
			return redirect("/settings/personal?error=Anthem change failed, please try another video!")

		if "D" in duration:
			return redirect("/settings/personal?error=Can't use a live youtube video!")

		if "H" in duration:
			return redirect("/settings/personal?error=Duration of the video must not exceed 15 minutes!")

		if "M" in duration:
			duration = int(duration.split("PT")[1].split("M")[0])
			if duration > 15:
				return redirect("/settings/personal?error=Duration of the video must not exceed 15 minutes!")

	gevent.spawn(_change_song_youtube, v.id, id)

	return redirect("/settings/personal?msg=Profile Anthem successfully updated. Please wait 5 minutes for the change to take effect.")


def process_settings_plaintext(kind, current, length, default_value):
	value = request.values.get(kind, "").strip()

	if not value:
		return default_value

	if kind == "twitter":
		value = value.lower()

	if len(value) > length:
		stop(400, f"The value you entered exceeds the character limit ({length} characters)")

	if value == current:
		stop(400, "You didn't change anything!")

	return value


@app.post("/settings/change_flair")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_change_flair(v):
	if v.flairchanged: stop(403)

	flair = process_settings_plaintext("flair", v.flair, 100, None)

	if flair:
		flair_html = filter_emojis_only(flair, link=True)
		flair_html = censor_slurs_profanities(flair_html, None)

		if len(flair_html) > 1000:
			stop(400, "Your rendered flair is too long!")

		execute_blackjack(v, None, flair, "flair")
	else:
		flair_html = None

	v.flair = flair
	v.flair_html = flair_html
	g.db.add(v)

	return {"message": "Flair successfully updated!"}


@app.post("/settings/pronouns_change")
@feature_required('PRONOUNS')
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_pronouns_change(v):
	pronouns = process_settings_plaintext("pronouns", v.pronouns, 15, DEFAULT_PRONOUNS)

	if pronouns and not pronouns_regex.fullmatch(pronouns):
		stop(400, "The pronouns you entered don't match the required format!")

	if pronouns:
		bare_pronouns = pronouns.lower().replace('/', '')
		if bare_pronouns.startswith('nig'):
			pronouns = 'BI/POC'
		elif bare_pronouns.startswith('fag'):
			pronouns = 'cute/twink'

	v.pronouns = pronouns
	g.db.add(v)

	return {"message": "Pronouns successfully updated!"}

@app.post("/settings/twitter")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_twitter(v):
	twitter = process_settings_plaintext("twitter", v.twitter, 50, "x.com")

	twitter = twitter.replace('https://', '').rstrip('/')
	v.twitter = twitter
	g.db.add(v)

	return {"message": "Twitter domain successfully updated!"}


@app.post("/settings/checkmark_text")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_checkmark_text(v):
	if not v.verified:
		stop(403, "You don't have a checkmark to edit its hover text!")

	v.verified = process_settings_plaintext("checkmark-text", v.verified, 100, "Verified")
	g.db.add(v)
	return {"message": "Checkmark Text successfully updated!"}

@app.post("/settings/birthday")
@limiter.limit('1/second', scope=rpath)
@limiter.limit('1/second', scope=rpath, key_func=get_ID)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def settings_birthday(v):
	if v.is_suspended:
		return {"message": "Birthday successfully updated!"}

	birthday = request.values.get('birthday')
	try: birthday_utc = timegm(time.strptime(birthday, "%Y-%m-%d"))
	except: stop(400, "Invalid birthday!")

	if birthday_utc > time.time():
		stop(400, "Invalid birthday!")

	eighteen_years_ago = time.time() - 31556952 * 18

	if birthday_utc > eighteen_years_ago:
		unban_utc = birthday_utc + 31556952 * 18
		days = (unban_utc - time.time()) / 86400
		days += random.randint(1, 40)
		v.ban(reason=f"Underage (birthday)", days=days)

	return {"message": "Birthday successfully updated!"}
