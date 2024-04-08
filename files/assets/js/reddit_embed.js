addEventListener("message", function(t) {
	if (typeof t.data == "string" && t.data) {
		const data = JSON.parse(t.data)
		if (data && "type" in data && data.type == "resize.embed")
			document.getElementById('reddit-embed').height = data.data
	}
})
