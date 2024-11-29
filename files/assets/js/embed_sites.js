function embed_sites() {
	if (navigator.doNotTrack == "1") return

	if (document.getElementById('orgy-top-container')) return

	//twitter
	const twitter = document.getElementById('twitter').value
	for (const blockquote of document.querySelectorAll('blockquote.twitter-tweet')) {
		const a = blockquote.lastChild
		const id = a.href.split('/status/')[1].split('?ref_src')[0]
		let iframe_src = `https://platform.twitter.com/embed/Tweet.html?dnt=true&hideThread=true&id=${id}`
		if (document.body.dataset.dark)
			iframe_src += "&theme=dark"

		let iframe_html = `<iframe class="twitter-embed" credentialless="true" allowfullscreen="true" height="0" src="${iframe_src}" scrolling="no" sandbox="allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox"></iframe>`
		if (twitter != 'x.com') {
			a.classList.add('d-block')
			a.innerHTML = a.href
			iframe_html = a.outerHTML + iframe_html
		}
		blockquote.insertAdjacentHTML('afterend', iframe_html);
	}

	//bluesky
	for (const blockquote of document.querySelectorAll('blockquote.bluesky-embed')) {
		const a = blockquote.lastChild
		const iframe_src = a.href.replace('https://bsky.app/profile/', 'https://embed.bsky.app/embed/').replace('/post/', '/app.bsky.feed.post/')

		let iframe_html = `<iframe credentialless="true" sandbox="allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox" scrolling="no" class="bluesky-embed" src="${iframe_src}" height="0" width="500"></iframe>`

		blockquote.insertAdjacentHTML('afterend', iframe_html);
	}

	//reddit
	const reddit = document.getElementById('reddit').value
	for (const a of document.querySelectorAll(`a[href^="https://${reddit}/r/"]:not(a[href$="/new"]), a[href^="https://${reddit}/user/"][href*="/comments/"]`)) {
		if (a.innerHTML && a.innerHTML !== a.href) continue
		if (["STRONG", "LI", "BLOCKQUOTE", "PRE", "CODEBLOCK"].includes(a.parentElement.tagName)) continue

		let iframe_src = a.href.replace(`https://${reddit}/`, 'https://embed.reddit.com/')
		iframe_src = iframe_src.split('?')[0]
		iframe_src += "?context=1&showtitle=true"
		if (document.body.dataset.dark)
			iframe_src += "&theme=dark"

		let iframe_html = `<iframe class="reddit-embed" credentialless="true" height="240" src="${iframe_src}" scrolling="no" sandbox="allow-scripts allow-popups allow-popups-to-escape-sandbox"></iframe>`
		if (reddit == "undelete.pullpush.io") {
			iframe_html = a.outerHTML + iframe_html
		}
		a.outerHTML = iframe_html
		a.classList.remove('d-none')
	}

	//substack
	for (const a of document.querySelectorAll(`a[href*="substack.com/"]`)) {
		if (a.innerHTML && a.innerHTML !== a.href) continue
		if (["STRONG", "LI", "BLOCKQUOTE", "PRE", "CODEBLOCK"].includes(a.parentElement.tagName)) continue

		let iframe_src
		if (a.href.includes('substack.com/p/') && a.href.split("/").length == 5) {
			iframe_src = a.href.replaceAll('substack.com/p/', 'substack.com/embed/p/') + '?origin=' + location.origin
		}
		else if (a.href.includes('/note/c-')) {
			const id = a.href.split('/note/c-').pop()
			iframe_src = `https://substack.com/embed/c/${id}?origin=${location.origin}`
		}
		else {
			continue
		}

		let iframe_html = `<iframe credentialless="true" sandbox="allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox" scrolling="no" class="substack-embed" src="${iframe_src}" height="500" width="500"></iframe>`
		a.outerHTML = iframe_html
		a.classList.remove('d-none')
	}

	//tiktok
	for (const a of document.querySelectorAll(`a[href^="https://tiktok.com/@"][href*="/video/"]`)) {
		if (a.innerHTML && a.innerHTML !== a.href) continue
		if (["STRONG", "LI", "BLOCKQUOTE", "PRE", "CODEBLOCK"].includes(a.parentElement.tagName)) continue

		const id = a.href.split('/video/')[1]
		const iframe_src = `https://www.tiktok.com/embed/${id}`

		let iframe_html = `<iframe credentialless="true" sandbox="allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox" scrolling="no" class="tiktok-embed" src="${iframe_src}" height="756" width="325"></iframe>`
		a.outerHTML = iframe_html
		a.classList.remove('d-none')
	}

	//blind
	for (const a of document.querySelectorAll(`a[href^="https://www.teamblind.com/"][href*="-"]`)) {
		if (a.innerHTML && a.innerHTML !== a.href) continue
		if (["STRONG", "LI", "BLOCKQUOTE", "PRE", "CODEBLOCK"].includes(a.parentElement.tagName)) continue

		const id = a.href.split('-').pop()
		const iframe_src = `https://www.teamblind.com/embed/${id}`

		let iframe_html = `<iframe credentialless="true" sandbox="allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox" scrolling="no" class="tiktok-embed" src="${iframe_src}" height="500" width="500"></iframe>`
		a.outerHTML = iframe_html
		a.classList.remove('d-none')
	}

	//instagram
	for (const a of document.querySelectorAll(`a[href^="https://instagram.com/"]`)) {
		if (a.innerHTML && a.innerHTML !== a.href) continue
		if (["STRONG", "LI", "BLOCKQUOTE", "PRE", "CODEBLOCK"].includes(a.parentElement.tagName)) continue

		let iframe_src = a.href.split('https://instagram.com/')[1]
		if (iframe_src.endsWith('/'))
			iframe_src = iframe_src.slice(0, -1)
		if (iframe_src.includes('/')) { //implies p/ or reel/
			if (iframe_src.split('/').length == 3) //implies a url like this https://instagram.com/magdalenanderssons/p/C-5Mp93iI3u instead of https://instagram.com/p/C-5Mp93iI3u
				iframe_src = iframe_src.split('/')[1] + '/' + iframe_src.split('/')[2]
			iframe_src = iframe_src + '/embed/captioned'
		}
		else {
			iframe_src = iframe_src + '/embed'
		}
		iframe_src = `https://www.instagram.com/${iframe_src}`

		let iframe_html = `<iframe credentialless="true" sandbox="allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox" scrolling="no" class="instagram-embed" src="${iframe_src}" height="500" width="500"></iframe>`
		a.outerHTML = iframe_html
		a.classList.remove('d-none')
	}
}
embed_sites()



addEventListener("message", function(e) {
	if (e.origin == "https://platform.twitter.com") {
		const height = e.data["twttr.embed"]["params"][0]["height"]
		if (height) {
			for (const iframe of document.getElementsByClassName("twitter-embed")) {
				if (e.source === iframe.contentWindow) {
					if (height == 76) {//not found
						iframe.remove()
					}
					else {
						iframe.height = height
						iframe.previousElementSibling.remove()
					}
				}
			}
		}
	}
	else if (e.origin == "https://embed.bsky.app") {
		const height = e.data.height
		if (height) {
			for (const iframe of document.getElementsByClassName("bluesky-embed")) {
				if (e.source === iframe.contentWindow) {
					if (height == 176) {//not found
						iframe.remove()
					}
					else {
						iframe.height = height
						iframe.previousElementSibling.remove()
					}
				}
			}
		}
	}
	else if (e.origin.endsWith('.substack.com')) {
		const height = e.data.iframeHeight
		if (height) {
			for (const iframe of document.getElementsByClassName("substack-embed")) {
				if (e.source === iframe.contentWindow) {
					iframe.height = height
					break
				}
			}
		}
	}
	else if (e.origin == "https://www.teamblind.com") {
		const height = e.data.height
		if (height) {
			for (const iframe of document.getElementsByClassName("blind-embed")) {
				if (e.source === iframe.contentWindow) {
					iframe.height = height
					break
				}
			}
		}
	}
	else if (e.origin == "https://www.instagram.com") {
		const height = JSON.parse(e.data).details.height
		if (height) {
			for (const iframe of document.getElementsByClassName("instagram-embed")) {
				if (e.source === iframe.contentWindow) {
					iframe.height = height
					break
				}
			}
		}
	}
	else if (typeof e.data == "string" && e.data) {
		const data = JSON.parse(e.data)
		let height = data.data
		if (data && "type" in data && data.type == "resize.embed")
			for (const iframe of document.getElementsByClassName("reddit-embed")) {
				if (e.source === iframe.contentWindow) {
					iframe.height = height
					break
				}
			}
	}
})
