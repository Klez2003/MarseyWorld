let audio = new Audio(`/i/6.webp`);

audio.play();
if (audio.paused) {
	document.addEventListener('click', () => {
		if (audio.paused) audio.play();
	}, {once : true})
}
