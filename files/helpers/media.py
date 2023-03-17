import os
import subprocess
import time
import requests
from shutil import copyfile
from typing import Optional

import gevent
import imagehash
from flask import abort, g, has_request_context, request
from werkzeug.utils import secure_filename
from PIL import Image
from PIL import UnidentifiedImageError
from PIL.ImageSequence import Iterator
from sqlalchemy.orm.session import Session

from files.classes.media import *
from files.helpers.cloudflare import purge_files_in_cache
from files.helpers.settings import get_setting

from .config.const import *

def remove_media_using_link(path):
	if path.startswith(SITE_FULL_IMAGES):
		path = path.split(img_prefix, 1)[1]

	video_prefix = f'https://videos.{SITE}'
	if path.startswith(video_prefix):
		path = path.split(video_prefix, 1)[1]

	os.remove(path)


def media_ratelimit(v):
	t = time.time() - 86400
	count = g.db.query(Media).filter(Media.user_id == v.id, Media.created_utc > t).count()
	if count > 50 and v.admin_level < PERMS['USE_ADMIGGER_THREADS']:
		print(STARS, flush=True)
		print(f'@{v.username} hit the 50 file daily limit!')
		print(STARS, flush=True)
		abort(500)

def process_files(files, v, body):
	if g.is_tor or not files.get("file"): return body
	files = files.getlist('file')[:20]

	if files:
		media_ratelimit(v)


	for file in files:
		if f'[{file.filename}]' not in body:
			body += f'\n[{file.filename}]'

		if file.content_type.startswith('image/'):
			name = f'/images/{time.time()}'.replace('.','') + '.webp'
			file.save(name)
			url = process_image(name, v)
			body = body.replace(f'[{file.filename}]', f'{url} ', 1)
		elif file.content_type.startswith('video/'):
			body = body.replace(f'[{file.filename}]', f'{process_video(file, v)} ', 1)
		elif file.content_type.startswith('audio/'):
			body = body.replace(f'[{file.filename}]', f"{SITE_FULL}{process_audio(file, v)} ", 1)
		else:
			abort(415)
	
	return body


def process_audio(file, v):
	old = f'/audio/{time.time()}'.replace('.','')
	file.save(old)

	size = os.stat(old).st_size
	if size > MAX_IMAGE_AUDIO_SIZE_MB_PATRON * 1024 * 1024 or not v.patron and size > MAX_IMAGE_AUDIO_SIZE_MB * 1024 * 1024:
		os.remove(old)
		abort(413, f"Max image/audio size is {MAX_IMAGE_AUDIO_SIZE_MB} MB ({MAX_IMAGE_AUDIO_SIZE_MB_PATRON} MB for {patron.lower()}s)")

	name_original = secure_filename(file.filename)
	extension = name_original.split('.')[-1].lower()

	if extension not in {'mp3','ogg','flac'}:
		extension = 'mp3'

	new = old + '.' + extension

	try:
		subprocess.run(["ffmpeg", "-y", "-loglevel", "warning", "-nostats", "-i", old, "-map_metadata", "-1", "-c:a", "copy", new], check=True)
	except:
		os.remove(old)
		if os.path.isfile(new):
			os.remove(new)
		abort(400)

	os.remove(old)

	media = Media(
		kind='audio',
		filename=new,
		user_id=v.id,
		size=size
	)
	g.db.add(media)

	return new


def convert_to_mp4(old, new, vid, db):
	tmp = new.replace('.mp4', '-t.mp4')
	try:
		subprocess.run(["ffmpeg", "-y", "-loglevel", "warning", "-nostats", "-threads:v", "1", "-i", old, "-map_metadata", "-1", tmp], check=True, stderr=subprocess.STDOUT)
	except:
		os.remove(old)
		if os.path.isfile(tmp):
			os.remove(tmp)
		abort(400)
	
	os.replace(tmp, new)
	os.remove(old)

	media = Media(
		kind='video',
		filename=new,
		user_id=vid,
		size=os.stat(new).st_size
	)
	db.add(media)
	db.commit()
	db.close()

	purge_files_in_cache(f"{SITE_FULL}{new}")



def process_video(file, v):
	old = f'/videos/{time.time()}'.replace('.','')
	file.save(old)

	size = os.stat(old).st_size
	if (SITE_NAME != 'WPD' and
			(size > MAX_VIDEO_SIZE_MB_PATRON * 1024 * 1024
				or not v.patron and size > MAX_VIDEO_SIZE_MB * 1024 * 1024)):
		os.remove(old)
		abort(413, f"Max video size is {MAX_VIDEO_SIZE_MB} MB ({MAX_VIDEO_SIZE_MB_PATRON} MB for paypigs)")

	name_original = secure_filename(file.filename)
	extension = name_original.split('.')[-1].lower()
	new = old + '.' + extension

	if extension not in {'mp4','avi','mkv'}:
		new = new.replace(f'.{extension}', '.mp4')
		copyfile(old, new)
		db = Session(bind=g.db.get_bind(), autoflush=False)
		gevent.spawn(convert_to_mp4, old, new, v.id, db)
	else:
		try:
			subprocess.run(["ffmpeg", "-y", "-loglevel", "warning", "-nostats", "-i", old, "-map_metadata", "-1", "-c:v", "copy", "-c:a", "copy", new], check=True)
		except:
			os.remove(old)
			if os.path.isfile(new):
				os.remove(new)
			abort(400)

		os.remove(old)

		media = Media(
			kind='video',
			filename=new,
			user_id=v.id,
			size=os.stat(new).st_size
		)
		g.db.add(media)

	if SITE == 'watchpeopledie.tv': 
		return f'https://videos.{SITE}' + new.split('/videos')[1]
	else:
		return f"{SITE_FULL}{new}"

def process_image(filename:str, v, resize=0, trim=False, uploader_id:Optional[int]=None, db=None):
	# thumbnails are processed in a thread and not in the request context
	# if an image is too large or webp conversion fails, it'll crash
	# to avoid this, we'll simply return None instead
	has_request = has_request_context()
	size = os.stat(filename).st_size
	patron = bool(v.patron)

	if size > MAX_IMAGE_AUDIO_SIZE_MB_PATRON * 1024 * 1024 or not patron and size > MAX_IMAGE_AUDIO_SIZE_MB * 1024 * 1024:
		os.remove(filename)
		if has_request:
			abort(413, f"Max image/audio size is {MAX_IMAGE_AUDIO_SIZE_MB} MB ({MAX_IMAGE_AUDIO_SIZE_MB_PATRON} MB for paypigs)")
		return None

	try:
		with Image.open(filename) as i:
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
		print(f"Couldn't identify an image for {filename}; deleting... (user {v.id if v else '-no user-'})")
		os.remove(filename)
		if has_request:
			abort(415)
		return None

	params.append(filename)
	try:
		subprocess.run(params, timeout=MAX_IMAGE_CONVERSION_TIMEOUT)
	except:
		os.remove(filename)
		if has_request:
			abort(400, ("An uploaded image couldn't be converted to WEBP. "
						"Please convert it to WEBP elsewhere then upload it again."))
		return None

	size_after_conversion = os.stat(filename).st_size

	if resize:
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
					if resize == 400 and img in {'256.webp','585.webp'}: continue
					img_path = f'{path}/{img}'
					if img_path == filename: continue

					with Image.open(img_path) as i:
						i_hash = str(imagehash.phash(i))

					if i_hash in hashes.keys():
						print(STARS, flush=True)
						print(hashes[i_hash], flush=True)
						print(img_path, flush=True)
						print(STARS, flush=True)
					else: hashes[i_hash] = img_path

				with Image.open(filename) as i:
					i_hash = str(imagehash.phash(i))

				if i_hash in hashes.keys():
					os.remove(filename)
					if has_request:
						abort(409, "Image already exists! " + hashes[i_hash].split('/')[-1])
					return None

	db = db or g.db

	media = Media(
		kind='image',
		filename=filename,
		user_id=uploader_id or v.id,
		size=os.stat(filename).st_size
	)
	db.add(media)

	return f'{SITE_FULL_IMAGES}{filename}'


def process_dm_images(v, user, body):
	if not request.files.get("file") or g.is_tor or not get_setting("dm_images"):
		return body

	files = request.files.getlist('file')[:20]


	for file in files:
		if f'[{file.filename}]' not in body:
			body += f'\n[{file.filename}]'

		if file.content_type.startswith('image/'):
			filename = f'/dm_images/{time.time()}'.replace('.','') + '.webp'
			file.save(filename)

			try:
				with Image.open(filename) as i:
					pass
			except:
				os.remove(filename)
				abort(415)

			size = os.stat(filename).st_size
			patron = bool(v.patron)

			if size > MAX_IMAGE_AUDIO_SIZE_MB_PATRON * 1024 * 1024 or not patron and size > MAX_IMAGE_AUDIO_SIZE_MB * 1024 * 1024:
				os.remove(filename)
				abort(413, f"Max image/audio size is {MAX_IMAGE_AUDIO_SIZE_MB} MB ({MAX_IMAGE_AUDIO_SIZE_MB_PATRON} MB for paypigs)")

			with open(filename, 'rb') as f:
				os.remove(filename)
				try:
					req = requests.request(
						"POST",
						"https://pomf2.lain.la/upload.php",
						files={'files[]': f},
						timeout=20,
						proxies=proxies
					).json()
				except:
					abort(400, "Image upload timed out, please try again!")

			try: url = req['files'][0]['url']
			except: abort(400, req['description'])

			body = body.replace(f'[{file.filename}]', f'{url} ', 1)
	
			with open(f"{LOG_DIRECTORY}/dm_images.log", "a+", encoding="utf-8") as f:
				if user:
					f.write(f'{url}, {v.username}, {v.id}, {user.username}, {user.id}, {int(time.time())}\n')
				else:
					f.write(f'{url}, {v.username}, {v.id}, Modmail, Modmail, {int(time.time())}\n')

	return body.strip()
