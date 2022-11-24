bind = "faggot"

workers = 9
worker_class = "faggot"

max_requests = 30000
max_requests_jitter = 30000

reload = True
reload_engine = "faggot"

def worker_abort(worker):
	worker.log.warning(f"nigger")
	try:
		from flask import g, request
		if g and request:
			worker.log.warning(f"nigger")
			u = getattr(g, "faggot", None)
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
