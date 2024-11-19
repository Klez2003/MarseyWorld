import os
import subprocess
import time
from shutil import copyfile
import json

import ffmpeg
import gevent
from flask import g, has_request_context, request
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

def remove_image_using_link(link):
	if not link or not '/images/' in link:
		return
	if SITE in link: path = link.split(SITE, 1)[1]
	else: path = link
	if not os.path.isfile(path): return
	os.remove(path)

def media_ratelimit(v):
	if v.id in {15014,1718156}: # Marseygen exception
		return
	t = time.time() - 86400
	count = g.db.query(Media).filter(Media.user_id == v.id, Media.created_utc > t).count()

	if v.patron or (SITE == 'rdrama.net' and v.id == 2158):
		limit = 300 
	else:
		limit = 200

	if count > limit and v.admin_level < PERMS['USE_ADMIGGER_THREADS']:
		print(STARS, flush=True)
		print(f'@{v.username} hit the {limit} file daily limit!')
		print(STARS, flush=True)
		stop(500)

def process_files(files, v, body, is_dm=False, dm_user=None, is_badge_thread=False, comment_body=None):
	if g.is_tor or not files.get("file"): return body

	files = files.getlist('file')[:50]

	if files:
		media_ratelimit(v)


	for file in files:
		if f'[{file.filename}]' not in body:
			continue

		if file.content_type.startswith('image/'):
			name = f'/images/{time.time()}'.replace('.','') + '.webp'
			file.save(name)
			try: url = process_image(name, v)
			except Exception as e:
				print(e)
				os.remove(name)
				continue
			if is_badge_thread:
				process_badge_entry(name, v, comment_body)
		elif file.content_type.startswith('video/'):
			url, _, _ = process_video(file, v)
		elif file.content_type.startswith('audio/'):
			url = f'{SITE_FULL}{process_audio(file, v)}'
		elif has_request_context():
			stop(415)
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
	if isinstance(file, str):
		old = file
	else:
		if not old:
			old = f'/audio/{time.time()}'.replace('.','')
		file.save(old)

	size = os.stat(old).st_size
	if size > MAX_IMAGE_AUDIO_SIZE_MB_PATRON * 1024 * 1024 or not v.patron and size > MAX_IMAGE_AUDIO_SIZE_MB * 1024 * 1024:
		os.remove(old)
		stop(413, f"Max image/audio size is {MAX_IMAGE_AUDIO_SIZE_MB} MB ({MAX_IMAGE_AUDIO_SIZE_MB_PATRON} MB for {patron}s)")

	if isinstance(file, str):
		extension = '.mp3'
	else:
		extension = guess_extension(file.content_type)
		if not extension:
			os.remove(old)
			stop(400, "Unsupported audio format.")

	new = old + extension

	try:
		ffmpeg.input(old, threads=1).output(new, loglevel="quiet", map_metadata=-1, threads=1).run()
	except:
		os.remove(old)
		if os.path.isfile(new):
			os.remove(new)
		stop(400, "Something went wrong processing your audio on our end. Please try uploading it to https://pomf2.lain.la and post the link instead.")

	os.remove(old)

	media = Media(
		kind='audio',
		filename=new,
		user_id=v.id,
		size=size
	)
	g.db.add(media)

	return new


def reencode_video(old, new):
	tmp = new.replace('.mp4', '-t.mp4')

	print(f'Attempting to reencode {new}', flush=True)

	try:
		ffmpeg.input(old, threads=1).output(tmp, loglevel="quiet", map_metadata=-1, threads=1).run()
	except:
		os.remove(old)
		if os.path.isfile(tmp):
			os.remove(tmp)
		if SITE == 'watchpeopledie.tv':
			rclone_copy(new)
		print(f'Failed (1) reencoding {new}', flush=True)
		return

	os.replace(tmp, new)
	os.remove(old)

	if SITE == 'watchpeopledie.tv':
		rclone_copy(new)

	url = SITE_FULL_VIDEOS + new.split('/videos')[1]
	purge_files_in_cloudflare_cache(url)

	print(f'Finished reencoding {new}', flush=True)


def process_video(file, v, post=None):
	if isinstance(file, str):
		old = file
	else:
		old = f'/videos/{time.time()}'.replace('.','')
		file.save(old)

	size = os.stat(old).st_size
	if not IS_LOCALHOST and (size > MAX_VIDEO_SIZE_MB_PATRON * 1024 * 1024 or (not v.patron and size > MAX_VIDEO_SIZE_MB * 1024 * 1024)):
		os.remove(old)
		stop(413, f"Max video size is {MAX_VIDEO_SIZE_MB} MB ({MAX_VIDEO_SIZE_MB_PATRON} MB for {patron}s)")

	new = f'{old}.mp4'

	reencode = False

	try:
		streams = ffmpeg.probe(old)['streams']
	except:
		os.remove(old)
		stop(400, "Something went wrong processing your video on our end. Please try uploading it to https://pomf2.lain.la and post the link instead.")

	for stream in streams:
		if stream["codec_type"] == "video":
			if stream['codec_name'] != 'h264':
				reencode = True
			if int(stream.get('bit_rate', 3000000)) >= 3000000:
				reencode = True
			if stream.get('profile') != 'High':
				reencode = True
			if stream.get('level') > 52:
				reencode = True
		elif stream["codec_type"] == "audio":
			if stream.get('profile') != 'LC':
				reencode = True

	if reencode:
		copyfile(old, new)
		gevent.spawn(reencode_video, old, new)
	else:
		try:
			ffmpeg.input(old, threads=1).output(new, loglevel="quiet", map_metadata=-1, acodec="copy", vcodec="copy", threads=1).run()
		except:
			os.remove(old)
			if os.path.isfile(new):
				os.remove(new)
			stop(400, "Something went wrong processing your video on our end. Please try uploading it to https://pomf2.lain.la and post the link instead.")

		os.remove(old)

	media = Media(
		kind='video',
		filename=new,
		user_id=v.id,
		size=os.stat(new).st_size
	)
	g.db.add(media)

	if post:
		media_usage = MediaUsage(filename=new)
		media_usage.post_id = post.id
		g.db.add(media_usage)


	url = SITE_FULL_VIDEOS + new.split('/videos')[1]

	name = f'/images/{time.time()}'.replace('.','') + '.webp'
	ffmpeg.input(new, threads=1).output(name, loglevel="quiet", map_metadata=-1, threads=1, **{"vf":"scale='iw':-2", 'frames:v':1}).run()
	posterurl = SITE_FULL_IMAGES + name
	media.posterurl = posterurl

	if SITE == 'watchpeopledie.tv':
		gevent.spawn(rclone_copy, new)

	return url, posterurl, name

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
			oldformat = i.format

			if oldformat == 'WEBP' and not resize and not trim:
				params = ["exiv2", "rm"]
			else:
				if not resize and size > max_size:
					ratio = max_size / size
					resize = i.width * ratio

				params = ["magick"]
				if resize == 199: params.append(f"{filename}[0]")
				else: params.append(filename)
				params.extend(["-coalesce", "-quality", "88", "-strip", "-auto-orient"])
				if trim and len(list(Iterator(i))) == 1:
					params.append("-trim")
				if resize and i.width > resize:
					params.extend(["-resize", f"{resize}>"])
	except:
		os.remove(filename)
		if has_request:
			stop(400, "Something went wrong processing your image on our end. Please try uploading it to https://pomf2.lain.la and post the link instead.")
		return None

	params.append(filename)
	try:
		if v and v.id == FISHY_ID: timeout = 60
		else: timeout = 30
		subprocess.run(params, check=True, timeout=timeout)
	except:
		os.remove(filename)
		if has_request:
			stop(400, "Something went wrong processing your image on our end. Please try uploading it to https://pomf2.lain.la and post the link instead.")
		return None

	size_after_conversion = os.stat(filename).st_size

	if original_resize:
		if size_after_conversion > MAX_IMAGE_SIZE_BANNER_RESIZED_MB * 1024 * 1024:
			os.remove(filename)
			if has_request:
				stop(413, f"Max size for site assets is {MAX_IMAGE_SIZE_BANNER_RESIZED_MB} MB")
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

	return f'{SITE_FULL_IMAGES}{filename}'


def process_badge_entry(oldname, v, comment_body):
	try:
		json_body = '{' + comment_body.split('{')[1].split('}')[0] + '}'
		badge_def = json.loads(json_body)
		name = badge_def["name"]

		if len(name) > 50:
			stop(400, "Badge name is too long (max 50 characters)")

		if not badge_name_regex.fullmatch(name):
			stop(400, "Invalid badge name!")

		existing = g.db.query(BadgeDef).filter_by(name=name).one_or_none()
		if existing: stop(409, "A badge with this name already exists!")

		badge = BadgeDef(name=name, description=badge_def["description"])
		g.db.add(badge)
		g.db.flush()
		filename = f'files/assets/images/{SITE_NAME}/badges/{badge.id}.webp'
		copyfile(oldname, filename)
		process_image(filename, v, resize=300, trim=True)
		purge_files_in_cloudflare_cache(f"{SITE_FULL_IMAGES}/i/{SITE_NAME}/badges/{badge.id}.webp")
	except Exception as e:
		stop(400, str(e))


if SITE == 'watchpeopledie.tv':
	def rclone_copy(filename):
		print(f'Attempting to sync {filename}', flush=True)
		params = ["rclone", "copy", filename, "no:/videos"]
		subprocess.run(params, check=True, timeout=3000)
		print(f'Finished syncing {filename}', flush=True)

	def rclone_delete(path):
		params = ("rclone", "deletefile", path)
		subprocess.run(params, check=True, timeout=30)
