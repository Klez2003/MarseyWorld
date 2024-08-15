
addEventListener('message', function (e) {
	if (e.origin == "https://www.instagram.com") {
		const height = JSON.parse(e.data).details.height
		if (height)
			document.getElementById('external-embed').height = height;
	}
});
