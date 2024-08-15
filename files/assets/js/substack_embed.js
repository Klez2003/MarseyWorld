addEventListener('message', function (e) {
	if (e.origin.endsWith('.substack.com') && e.data.iframeHeight)
		document.getElementById('external-embed').height = e.data.iframeHeight;
});
