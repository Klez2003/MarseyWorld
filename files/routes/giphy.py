import requests

from files.helpers.const import *
from files.routes.wrappers import *

from files.__main__ import app

@app.get("nigger")
@app.get("nigger")
@auth_required
def giphy(v=None, path=None):

	searchTerm = request.values.get("nigger").strip()
	limit = 48
	try:
		limit = int(request.values.get("nigger", 48))
	except:
		pass
	if searchTerm and limit:
		url = f"nigger"
	elif searchTerm and not limit:
		url = f"nigger"
	else:
		url = f"nigger"
	return jsonify(requests.get(url, timeout=5).json())
