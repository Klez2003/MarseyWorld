from os import environ

STARS = '\n\n★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★★\n\n'

bind = '0.0.0.0:5000'

worker_class = 'gevent'
workers = int(environ.get("WORKER_COUNT").strip())

max_requests = 5000
max_requests_jitter = 10000

limit_request_line = 8190

reload = True
reload_engine = 'poll'

def worker_abort(worker):
	worker.log.warning(f"Worker {worker.pid} received SIGABRT.")
	try:
		from flask import g, request
		if g and request:
			worker.log.warning(STARS)
			worker.log.warning(f"While serving {request.method} {request.url}")
			u = getattr(g, 'v', None)
			if u:
				worker.log.warning(f"User: {u.username!r} id:{u.id}")
			else:
				worker.log.warning(f"User: not logged in")
			worker.log.warning(dict(request.values))
			worker.log.warning(STARS)
		else:
			worker.log.warning("No request info")
	except:
		worker.log.warning("Failed to get request info")

	import os
	os.abort()
