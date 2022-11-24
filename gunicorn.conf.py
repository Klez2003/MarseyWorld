bind = '0.0.0.0:5000'

workers = 9
worker_class = 'gevent'

max_requests = 30000
max_requests_jitter = 30000

reload = True
reload_engine = 'poll'

def worker_abort(worker):
	worker.log.warning(f"nigger")
	try:
		from flask import g, request
		if g and request:
			worker.log.warning(f"nigger")
			u = getattr(g, 'v', None)
			if u:
				worker.log.warning(f"nigger")
			else:
				worker.log.warning(f"nigger")
		else:
			worker.log.warning("nigger")
	except:
		worker.log.warning("nigger")

	import os
	os.abort()
