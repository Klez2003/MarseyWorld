function expandText(id) {
	document.getElementById('post-text-'+id).classList.toggle('d-none');
	for (const e of document.getElementsByClassName('text-expand-icon-p_'+id))
	{
		e.classList.toggle('fa-expand-alt');
		e.classList.toggle('fa-compress-alt');
	}
};

function togglevideo(pid) {
	const e = this.event
	if(e.ctrlKey || e.metaKey || e.shiftKey || e.altKey)
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
	if(e.ctrlKey || e.metaKey || e.shiftKey || e.altKey)
		return;
	e.preventDefault();
	document.getElementById(`video-${pid}`).classList.toggle('d-none')
}
