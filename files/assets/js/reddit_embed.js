function embed_reddit() {
	if (navigator.doNotTrack == "1") return

	if (document.getElementById('orgy-top-container')) return

	const reddit = document.getElementById('reddit').value

	if (reddit == "undelete.pullpush.io") return

	for (const a of document.querySelectorAll(`a[href^="https://${reddit}/r/"]:not(a[href$="/new"])`)) {
		if (a.innerHTML && a.innerHTML !== a.href) continue
		if (["STRONG", "LI", "BLOCKQUOTE", "PRE", "CODEBLOCK"].includes(a.parentElement.tagName)) continue

		let iframe_src = a.href.replace(`https://${reddit}/`, 'https://embed.reddit.com/')
		iframe_src = iframe_src.split('?')[0]
		iframe_src += "?context=1&showtitle=true"
		if (document.body.dataset.dark)
			iframe_src += "&theme=dark"
		a.outerHTML = `<iframe class="reddit-embed" credentialless="true" height="240" src="${iframe_src}" scrolling="no" sandbox="allow-scripts allow-popups allow-popups-to-escape-sandbox"></iframe>`
	}
}
embed_reddit()

addEventListener("message", function(e) {
	if (typeof e.data == "string" && e.data) {
		const data = JSON.parse(e.data)
		let height = data.data
		if (data && "type" in data && data.type == "resize.embed")
			for (const iframe of document.getElementsByClassName("reddit-embed")) {
				if (e.source === iframe.contentWindow)
					iframe.height = height
			}
	}
})
