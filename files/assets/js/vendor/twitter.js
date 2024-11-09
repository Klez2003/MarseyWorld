function embed_twitter() {
	if (navigator.doNotTrack == "1") return

	if (document.getElementById('orgy-top-container')) return

	for (const blockquote of document.querySelectorAll('blockquote.twitter-tweet')) {
		const id = blockquote.lastChild.href.split('/status/')[1].split('?ref_src')[0]
		let iframe_src = `https://platform.twitter.com/embed/Tweet.html?dnt=true&hideThread=true&id=${id}`
		if (document.body.dataset.dark)
			iframe_src += "&theme=dark"

		blockquote.outerHTML = `<iframe class="twitter-embed" credentialless="true" allowfullscreen="true" height="240" src="${iframe_src}" scrolling="no" sandbox="allow-scripts allow-same-origin allow-popups"></iframe>`
	}
}
embed_twitter()

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
})
