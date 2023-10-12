const audio = document.getElementById('event-song');

audio.play();
document.addEventListener('click', () => {
	if (audio.paused) audio.play();
}, {once : true});
prepare_to_pause(audio)
