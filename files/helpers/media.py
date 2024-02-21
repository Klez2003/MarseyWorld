import os
import subprocess
import time
from shutil import copyfile
import json

import requests
import ffmpeg
import gevent
import imagehash
from flask import abort, g, has_request_context, request
from mimetypes import guess_extension
from PIL import Image
from PIL import UnidentifiedImageError
from PIL.ImageSequence import Iterator

from files.classes.media import *
from files.classes.badges import BadgeDef
from files.helpers.cloudflare import purge_files_in_cloudflare_cache
from files.helpers.settings import get_setting

from .config.const import *
from .regex import badge_name_regex

if SITE == 'watchpeopledie.tv':
	from rclone_python import rclone

def remove_media_using_link(path):
	if SITE in path:
		path = path.split(SITE, 1)[1]
	os.remove(path)

def media_ratelimit(v):
	if v.id in {15014,1718156}: # Marseygen exception
		return
	t = time.time() - 86400
	count = g.db.query(Media).filter(Media.user_id == v.id, Media.created_utc > t).count()

	if v.patron or (SITE == 'rdrama.net' and v.id == 2158):
		limit = 300 
	else:
		limit = 100

	if count > limit and v.admin_level < PERMS['USE_ADMIGGER_THREADS']:
		print(STARS, flush=True)
		print(f'@{v.username} hit the {limit} file daily limit!')
		print(STARS, flush=True)
		abort(500)

def process_files(files, v, body, is_dm=False, dm_user=None, admigger_thread=None, comment_body=None):
	if g.is_tor or not files.get("file"): return body
	files = files.getlist('file')[:20]

	if files:
		media_ratelimit(v)


	for file in files:
		if f'[{file.filename}]' not in body:
			continue

		if file.content_type.startswith('image/'):
			name = f'/images/{time.time()}'.replace('.','') + '.webp'
			file.save(name)
			url = process_image(name, v)
			if admigger_thread:
				process_admigger_entry(name, v, admigger_thread, comment_body)
		elif file.content_type.startswith('video/'):
			url = process_video(file, v)
		elif file.content_type.startswith('audio/'):
			url = f'{SITE_FULL}{process_audio(file, v)}'
		elif has_request_context():
			abort(415)
		else:
			return None

		body = body.replace(f'[{file.filename}]', f' {url} ', 1)

		if is_dm:
			with open(f"{LOG_DIRECTORY}/dm_media.log", "a+") as f:
				if dm_user:
					f.write(f'{url}, {v.username}, {v.id}, {dm_user.username}, {dm_user.id}, {int(time.time())}\n')
				else:
					f.write(f'{url}, {v.username}, {v.id}, Modmail, Modmail, {int(time.time())}\n')

	return body.replace('\n ', '\n').strip()


def process_audio(file, v, old=None):
	if not old:
		old = f'/audio/{time.time()}'.replace('.','')

	file.save(old)

	size = os.stat(old).st_size
	if size > MAX_IMAGE_AUDIO_SIZE_MB_PATRON * 1024 * 1024 or not v.patron and size > MAX_IMAGE_AUDIO_SIZE_MB * 1024 * 1024:
		os.remove(old)
		abort(413, f"Max image/audio size is {MAX_IMAGE_AUDIO_SIZE_MB} MB ({MAX_IMAGE_AUDIO_SIZE_MB_PATRON} MB for {patron}s)")

	extension = guess_extension(file.content_type)
	if not extension:
		os.remove(old)
		abort(400, "Unsupported audio format.")
	new = old + extension

	try:
		ffmpeg.input(old).output(new, loglevel="quiet", map_metadata=-1).run()
	except:
		os.remove(old)
		if os.path.isfile(new):
			os.remove(new)
		abort(400, "Something went wrong processing your audio on our end. Please try uploading it to https://pomf2.lain.la and post the link instead.")

	os.remove(old)

	media = Media(
		kind='audio',
		filename=new,
		user_id=v.id,
		size=size
	)
	g.db.add(media)

	return new


def reencode_video(old, new, check_sizes=False):
	tmp = new.replace('.mp4', '-t.mp4')
	try:
		ffmpeg.input(old).output(tmp, loglevel="quiet", map_metadata=-1).run()
	except:
		os.remove(old)
		if os.path.isfile(tmp):
			os.remove(tmp)
		return

	if check_sizes:
		old_size = os.stat(old).st_size
		new_size = os.stat(tmp).st_size
		if new_size > old_size:
			os.remove(tmp)
			return

	os.replace(tmp, new)
	os.remove(old)

	if SITE == 'watchpeopledie.tv':
		url = f'https://videos.{SITE}' + new.split('/videos')[1]
	else:
		url = f"{SITE_FULL}{new}"

	purge_files_in_cloudflare_cache(url)



def process_video(file, v):
	old = f'/videos/{time.time()}'.replace('.','')
	file.save(old)

	size = os.stat(old).st_size
	if size > MAX_VIDEO_SIZE_MB_PATRON * 1024 * 1024 or (not v.patron and size > MAX_VIDEO_SIZE_MB * 1024 * 1024):
		os.remove(old)
		abort(413, f"Max video size is {MAX_VIDEO_SIZE_MB} MB ({MAX_VIDEO_SIZE_MB_PATRON} MB for {patron}s)")

	new = f'{old}.mp4'

	try:
		video_info = ffmpeg.probe(old)['streams'][0]
		codec = video_info['codec_name']
		bitrate = int(video_info.get('bit_rate', 3000000))
	except:
		os.remove(old)
		abort(400, "Something went wrong processing your video on our end. Please try uploading it to https://pomf2.lain.la and post the link instead.")

	if codec != 'h264':
		copyfile(old, new)
		gevent.spawn(reencode_video, old, new)
	elif bitrate >= 3000000:
		copyfile(old, new)
		gevent.spawn(reencode_video, old, new, True)
	else:
		try:
			ffmpeg.input(old).output(new, loglevel="quiet", map_metadata=-1, acodec="copy", vcodec="copy").run()
		except:
			os.remove(old)
			if os.path.isfile(new):
				os.remove(new)
			abort(400, "Something went wrong processing your video on our end. Please try uploading it to https://pomf2.lain.la and post the link instead.")

		os.remove(old)

	media = Media(
		kind='video',
		filename=new,
		user_id=v.id,
		size=os.stat(new).st_size
	)
	g.db.add(media)

	if SITE == 'watchpeopledie.tv' and v and v.username.lower().startswith("icosaka"):
		gevent.spawn(delete_file, new, f'https://videos.{SITE}' + new.split('/videos')[1])

	if SITE == 'watchpeopledie.tv':
		gevent.spawn(send_file, new)
		return f'https://videos.{SITE}' + new.split('/videos')[1]
	else:
		return f"{SITE_FULL}{new}"

def process_image(filename, v, resize=0, trim=False, uploader_id=None):
	# thumbnails are processed in a thread and not in the request context
	# if an image is too large or webp conversion fails, it'll crash
	# to avoid this, we'll simply return None instead
	original_resize = resize
	has_request = has_request_context()
	size = os.stat(filename).st_size
	if v and v.patron:
		max_size = MAX_IMAGE_AUDIO_SIZE_MB_PATRON * 1024 * 1024
	else:
		max_size = MAX_IMAGE_AUDIO_SIZE_MB * 1024 * 1024

	try:
		with Image.open(filename) as i:
			if not resize and size > max_size:
				ratio = max_size / size
				resize = i.width * ratio

			oldformat = i.format
			params = ["magick"]
			if resize == 99: params.append(f"{filename}[0]")
			else: params.append(filename)
			params.extend(["-coalesce", "-quality", "88", "-strip", "-auto-orient"])
			if trim and len(list(Iterator(i))) == 1:
				params.append("-trim")
			if resize and i.width > resize:
				params.extend(["-resize", f"{resize}>"])
	except:
		os.remove(filename)
		if has_request and not filename.startswith('/chat_images/'):
			abort(400, "Something went wrong processing your image on our end. Please try uploading it to https://pomf2.lain.la and post the link instead.")
		return None

	params.append(filename)
	try:
		subprocess.run(params, check=True, timeout=30)
	except:
		os.remove(filename)
		if has_request:
			abort(400, "An uploaded image couldn't be converted to WEBP. Please convert it to WEBP elsewhere then upload it again.")
		return None

	size_after_conversion = os.stat(filename).st_size

	if original_resize:
		if size_after_conversion > MAX_IMAGE_SIZE_BANNER_RESIZED_MB * 1024 * 1024:
			os.remove(filename)
			if has_request:
				abort(413, f"Max size for site assets is {MAX_IMAGE_SIZE_BANNER_RESIZED_MB} MB")
			return None

		if filename.startswith('files/assets/images/'):
			path = filename.rsplit('/', 1)[0]
			kind = path.split('/')[-1]

			if kind in {'banners','sidebar'}:
				hashes = {}

				for img in os.listdir(path):
					img_path = f'{path}/{img}'
					if img_path == filename: continue

					with Image.open(img_path) as i:
						i_hash = str(imagehash.phash(i))

					if i_hash not in hashes.keys():
						hashes[i_hash] = img_path

				with Image.open(filename) as i:
					i_hash = str(imagehash.phash(i))

				if i_hash in hashes.keys():
					os.remove(filename)
					return None

	media = g.db.query(Media).filter_by(filename=filename, kind='image').one_or_none()
	if media: g.db.delete(media)

	media = Media(
		kind='image',
		filename=filename,
		user_id=uploader_id or v.id,
		size=os.stat(filename).st_size
	)
	g.db.add(media)

	if SITE == 'watchpeopledie.tv' and v and "dylan" in v.username.lower() and "hewitt" in v.username.lower():
		gevent.spawn(delete_file, filename, f'{SITE_FULL_IMAGES}{filename}')

	return f'{SITE_FULL_IMAGES}{filename}'

def delete_file(filename, url):
	time.sleep(60)
	os.remove(filename)
	purge_files_in_cloudflare_cache(url)

def send_file(filename):
	rclone.copy(filename, 'no:/videos', ignore_existing=True)


def process_sidebar_or_banner(oldname, v, type, resize):
	li = sorted(os.listdir(f'files/assets/images/{SITE_NAME}/{type}'),
		key=lambda e: int(e.split('.webp')[0]))[-1]
	num = int(li.split('.webp')[0]) + 1
	filename = f'files/assets/images/{SITE_NAME}/{type}/{num}.webp'
	copyfile(oldname, filename)
	process_image(filename, v, resize=resize)

def process_admigger_entry(oldname, v, admigger_thread, comment_body):
	if admigger_thread == SIDEBAR_THREAD:
		process_sidebar_or_banner(oldname, v, 'sidebar', 600)
	elif admigger_thread == BANNER_THREAD:
		banner_width = 1600
		process_sidebar_or_banner(oldname, v, 'banners', banner_width)
	elif admigger_thread == BADGE_THREAD:
		try:
			json_body = '{' + comment_body.split('{')[1].split('}')[0] + '}'
			badge_def = json.loads(json_body)
			name = badge_def["name"]

			if len(name) > 50:
				abort(400, "Badge name is too long (max 50 characters)")

			if not badge_name_regex.fullmatch(name):
				abort(400, "Invalid badge name!")

			existing = g.db.query(BadgeDef).filter_by(name=name).one_or_none()
			if existing: abort(409, "A badge with this name already exists!")

			badge = BadgeDef(name=name, description=badge_def["description"])
			g.db.add(badge)
			g.db.flush()
			filename = f'files/assets/images/{SITE_NAME}/badges/{badge.id}.webp'
			copyfile(oldname, filename)
			process_image(filename, v, resize=300, trim=True)
			purge_files_in_cloudflare_cache(f"{SITE_FULL_IMAGES}/i/{SITE_NAME}/badges/{badge.id}.webp")
		except Exception as e:
			abort(400, str(e))
