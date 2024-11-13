if (!playing_music() && !document.getElementsByClassName('twitter-embed') && !document.getElementsByClassName('reddit-embed')) {
	addEventListener("load", () => {
		const audio = document.getElementById('event-song');

		handle_playing_music(audio)

		audio.play();
		document.addEventListener('click', () => {
			if (audio.paused) audio.play();
		}, {once : true});
		prepare_to_pause(audio)
	})
}
