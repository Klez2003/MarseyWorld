addEventListener('message', function (e) {
	if (e.origin == "https://www.teamblind.com" && e.data.height)
		document.getElementById('external-embed').height = e.data.height;
});
