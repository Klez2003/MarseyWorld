let blockquotes_map = new Map();

function embed_twitter_reddit() {
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

		let iframe_html = `<iframe class="twitter-embed" credentialless="true" allowfullscreen="true" height="240" src="${iframe_src}" scrolling="no" sandbox="allow-scripts allow-same-origin allow-popups"></iframe>`
		if (twitter != 'x.com') {
			a.classList.add('d-block')
			a.innerHTML = a.href
			iframe_html = a.outerHTML + iframe_html
		}
		blockquotes_map[iframe_src] = blockquote.outerHTML
		blockquote.outerHTML = iframe_html
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

		let iframe_html = `<iframe credentialless="true" sandbox="allow-scripts allow-same-origin allow-popups" scrolling="no" class="substack-embed" src="${iframe_src}" height="500" width="500" style="max-width:100%"></iframe>`
		a.outerHTML = iframe_html
	}
}
embed_twitter_reddit()



addEventListener("message", function(e) {
	if (e.origin == "https://platform.twitter.com") {
		const height = e.data["twttr.embed"]["params"][0]["height"]
		if (height) {
			for (const iframe of document.getElementsByClassName("twitter-embed")) {
				if (e.source === iframe.contentWindow) {
					if (height == 76) //not found
						iframe.outerHTML = blockquotes_map[iframe.src]
					else
						iframe.height = height
					break
				}
			}
		}
	}
	else if (e.origin.endsWith('.substack.com')) {
		const height = e.data.iframeHeight
		if (height) {
			for (const iframe of document.getElementsByClassName("substack-embed")) {
				if (e.source === iframe.contentWindow) {
					iframe.height = e.data.iframeHeight
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
