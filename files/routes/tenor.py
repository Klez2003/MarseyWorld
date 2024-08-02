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

	if searchTerm:
		url = f"https://tenor.googleapis.com/v2/search?media_filter=webp&key={TENOR_KEY}&limit=50&q={searchTerm}"
	else:
		url = f"https://tenor.googleapis.com/v2/featured?media_filter=webp&key={TENOR_KEY}&limit=50"
	return requests.get(url, headers=HEADERS, timeout=5).json()
