function embed_twitter_reddit() {
	if (navigator.doNotTrack == "1") return

	for (const a of document.querySelectorAll('a[href^="https://x.com/"][href*="/status/"]')) {
		if (a.innerHTML && a.innerHTML !== a.href) continue
		if (a.parentElement.tagName == "STRONG") continue

		const id = a.href.split('/status/')[1].split('?')[0]
		let iframe_src = `https://platform.twitter.com/embed/Tweet.html?dnt=true&id=${id}`
		if (document.body.dataset.dark)
			iframe_src += "&theme=dark"

		a.innerHTML = `<iframe class="twitter-embed" credentialless="true" sandbox="allow-scripts allow-same-origin allow-popups" allowfullscreen="true" loading="lazy" height="500" src="${iframe_src}" scrolling="no"></iframe>`
	}

	for (const a of document.querySelectorAll('a[href^="https://old.reddit.com/r/"]:not(a[href$="/new"])')) {
		if (a.innerHTML && a.innerHTML !== a.href) continue
		if (a.parentElement.tagName == "STRONG") continue

		let iframe_src = a.href.replace('https://old.reddit.com/', 'https://embed.reddit.com/')
		iframe_src = iframe_src.split('?')[0]
		iframe_src += "?context=1&showtitle=true"
		if (document.body.dataset.dark)
			iframe_src += "&theme=dark"

		a.innerHTML = `<iframe class="reddit-embed" credentialless="true" sandbox="allow-scripts allow-popups" loading="lazy" height="240" src="${iframe_src}" scrolling="no"></iframe>`
	}
}
embed_twitter_reddit()

addEventListener("message", function(e) {
	if (e.origin == "https://platform.twitter.com") {
		const height = e.data["twttr.embed"]["params"][0]["height"]
		if (height) {
			for (const iframe of document.getElementsByClassName("twitter-embed")) {
				if (e.source === iframe.contentWindow)
					iframe.height = height
			}
		}
	}

	if (typeof e.data == "string" && e.data) {
		const data = JSON.parse(e.data)
		const height = data.data
		if (data && "type" in data && data.type == "resize.embed")
			for (const iframe of document.getElementsByClassName("reddit-embed")) {
				if (e.source === iframe.contentWindow)
					iframe.height = height
			}
	}
})
