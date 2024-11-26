from urllib.parse import parse_qs, urlparse

def get_youtube_id_and_t(url):
	params = parse_qs(urlparse(url).query, keep_blank_values=True)

	id = params.get('v')

	if not id: return (None, None)

	id = id[0]

	t = None
	split = id.split('?t=')
	if len(split) == 2:
		id = split[0]
		t = split[1]

	id = id.split('?')[0]

	return (id, t)

def handle_youtube_links(url):
	url = url.replace('&amp;','&')
	params = parse_qs(urlparse(url).query, keep_blank_values=True)
	html = None
	id, t = get_youtube_id_and_t(url)
	if not id: return None
	if yt_id_regex.fullmatch(id):
		for param in ('t','start','time_continue'):
			if t: break
			t = params.get(param, [0])[0]
		if isinstance(t, str):
			t = t.replace('s','').replace('S','')
			split = t.split('m')
			if len(split) == 2:
				minutes = int(split[0])
				if split[1]: seconds = int(split[1])
				else: seconds = 0
				t = minutes*60 + seconds
		html = f'<lite-youtube videoid="{id}"'
		if t and int(t) > 0:
			try: html += f' params="start={int(t)}"'
			except: stop(400, f"Something is wrong with the url you submitted ({url}) and it couldn't be parsed.")
		html += '></lite-youtube>'
	return html