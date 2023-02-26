document.onpaste = function(event) {
	const files = structuredClone(event.clipboardData.files);

	if (!files.length) return

	const f = document.getElementById('file-upload');
	f.files = files;
	changename('filename', f.id, 'input-message')
}
