import requests

from files.helpers.config.const import *
from files.routes.wrappers import *

from files.__main__ import app

@app.get("/tenor")
@app.get("/tenor<path>")
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400)
@limiter.limit(DEFAULT_RATELIMIT, deduct_when=lambda response: response.status_code < 400, key_func=get_ID)
@auth_required
def tenor(v, path=None):

	searchTerm = request.values.get("searchTerm", "").strip()
	limit = 48
	try:
		limit = int(request.values.get("limit", 48))
	except:
		pass
	if searchTerm and limit:
		url = f"https://tenor.googleapis.com/v2/search?media_filter=webp&q={searchTerm}&key={TENOR_KEY}&limit={limit}"
	elif searchTerm and not limit:
		url = f"https://tenor.googleapis.com/v2/search?media_filter=webp&q={searchTerm}&key={TENOR_KEY}&limit=48"
	else:
		url = f"https://tenor.googleapis.com/v2?media_filter=webp&key={TENOR_KEY}&limit=48"
	return requests.get(url, headers=HEADERS, timeout=5).json()
