import json
import requests

from files.helpers.config.const import *

if SITE == 'watchpeopledie.tv':
	from rclone_python import rclone

CLOUDFLARE_API_URL = "https://api.cloudflare.com/client/v4"
CLOUDFLARE_REQUEST_TIMEOUT_SECS = 5

CLOUDFLARE_AVAILABLE = CF_ZONE and CF_ZONE != DEFAULT_CONFIG_VALUE

def _request_from_cloudflare(url, method, post_data_str):
	if not CLOUDFLARE_AVAILABLE: return False
	try:
		res = str(requests.request(method, f"{CLOUDFLARE_API_URL}/zones/{CF_ZONE}/{url}", headers=CF_HEADERS, data=post_data_str, timeout=CLOUDFLARE_REQUEST_TIMEOUT_SECS))
	except Exception as e:
		print(e, flush=True)
		return False
	return res == "<Response [200]>"

def set_security_level(under_attack="high"):
	return _request_from_cloudflare("settings/security_level", "PATCH", f'{{"value":"{under_attack}"}}')

def clear_entire_cache():
	return _request_from_cloudflare("purge_cache", "POST", '{"purge_everything":true}')

def purge_files_in_cloudflare_cache(files):
	if not CLOUDFLARE_AVAILABLE: return False
	if isinstance(files, str):
		files = [files]

	if SITE == 'watchpeopledie.tv':
		for file in files:
			if file.startswith('https://videos.watchpeopledie.tv/'):
				filename = file.split('https://videos.watchpeopledie.tv/')[1]
				gevent.spawn(rclone.delete, f'no:/videos/{filename}')

	post_data = {"files": files}
	res = None
	try:
		res = requests.post(f'{CLOUDFLARE_API_URL}/zones/{CF_ZONE}/purge_cache', headers=CF_HEADERS, data=json.dumps(post_data), timeout=CLOUDFLARE_REQUEST_TIMEOUT_SECS)
	except:
		return False
	return res == "<Response [200]>"
