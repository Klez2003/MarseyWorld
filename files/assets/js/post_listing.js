function expandText(id) {
	const preview = document.getElementById('post-text-'+id)
	preview.classList.toggle('d-none');
	embed_sites(preview)
	for (const e of document.getElementsByClassName('text-expand-icon-p_'+id))
	{
		e.classList.toggle('fa-expand-alt');
		e.classList.toggle('fa-compress-alt');
	}
};

function togglevideo(pid) {
	const e = this.event
	if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey)
		return;
	e.preventDefault();
	let vid = document.getElementById(`video-${pid}`).classList
	vid.toggle('d-none')
	let vid2 = document.getElementById(`video2-${pid}`)
	if (vid.contains('d-none')) vid2.pause()
	else vid2.play()
}

function toggleyoutube(pid) {
	const e = this.event
	if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey)
		return;
	e.preventDefault();
	const el = document.getElementById(`video-${pid}`)
	el.classList.toggle('d-none')

	const iframe = el.getElementsByTagName('iframe')[0]

	if (el.classList.contains('d-none')) {
		iframe.dataset.src = iframe.src;
		iframe.src = '';
	}
	else {
		if (iframe && iframe.dataset.src)
			iframe.src = iframe.dataset.src;
		const playbtn = el.getElementsByClassName('lty-playbtn')[0]
		playbtn.click()
	}
}
