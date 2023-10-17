if (localStorage.getItem("music_playing") != 'true') {
	const audio = document.getElementById('event-song');

	audio.addEventListener('play', () => {
		localStorage.setItem("music_playing", true);
	})

	window.addEventListener('beforeunload', () => {
		localStorage.setItem("music_playing", false);
	})

	audio.play();
	document.addEventListener('click', () => {
		if (audio.paused) audio.play();
	}, {once : true});
	prepare_to_pause(audio)
}
