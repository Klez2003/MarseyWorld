addEventListener("message", function(t) {
	if (typeof t.data == "string" && t.data) {
		const data = JSON.parse(t.data)
		let height = data.data
		if (data && "type" in data && data.type == "resize.embed")
			document.getElementById('external-embed').height = height
	}
})
