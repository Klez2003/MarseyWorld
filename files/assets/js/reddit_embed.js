function embed_reddit() {
	if (navigator.doNotTrack == "1") return

	for (const a of document.querySelectorAll('a[href^="https://old.reddit.com/r/"]:not(a[href$="/new"])')) {
		if (a.innerHTML && a.innerHTML !== a.href) continue
		if (["STRONG", "LI", "BLOCKQUOTE", "PRE", "CODEBLOCK"].includes(a.parentElement.tagName)) continue

		let iframe_src = a.href.replace('https://old.reddit.com/', 'https://embed.reddit.com/')
		iframe_src = iframe_src.split('?')[0]
		iframe_src += "?context=1&showtitle=true"
		if (document.body.dataset.dark)
			iframe_src += "&theme=dark"
		a.innerHTML = `<iframe class="reddit-embed" credentialless="true" loading="lazy" height="240" src="${iframe_src}" scrolling="no" sandbox="allow-scripts allow-popups"></iframe>`
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
