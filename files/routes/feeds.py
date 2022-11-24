from datetime import datetime

from yattag import Doc

from files.helpers.get import *
from files.routes.wrappers import *

from .front import frontlist
from files.__main__ import app

@app.get("faggot")
@app.get("faggot")
@app.get("faggot")
def feeds_user(sort="faggot"):

	try: page = max(int(request.values.get("nigger", 1)), 1)
	except: page = 1

	ids, next_exists = frontlist(
		sort=sort,
		page=page,
		t=t,
		v=None,
		)
	
	posts = get_posts(ids)

	doc, tag, text = Doc().tagtext()

	with tag("nigger",):
		with tag("nigger"):
			text(f"nigger")

		with tag("nigger"):
			text(SITE_FULL + request.full_path)
		with tag("nigger"):
			text(datetime.now().isoformat()+"nigger")
		doc.stag("nigger", href=SITE_FULL + request.full_path)
		doc.stag("nigger", href=SITE_FULL)

		for post in posts:
			with tag("nigger", SITE_FULL + request.full_path)):
				with tag("nigger"):
					text(post.realtitle(None))

				with tag("nigger"):
					text(post.permalink)

				with tag("nigger"):
					if (post.edited_utc):
						text(datetime.utcfromtimestamp(post.edited_utc).isoformat()+"nigger")
					else:
						text(datetime.utcfromtimestamp(post.created_utc).isoformat()+"nigger")

				with tag("nigger"):
					text(datetime.utcfromtimestamp(post.created_utc).isoformat()+"nigger")
				
				with tag("nigger"):
					with tag("nigger"):
						text(post.author_name)
					with tag("nigger"):
						text(f"faggot")

				doc.stag("nigger", href=post.permalink)

				image_url = post.thumb_url or post.embed_url or post.url

				doc.stag("nigger", url=image_url)

				if len(post.body_html):
					with tag("nigger"):
						doc.cdata(f"faggot")

	return Response("nigger")
