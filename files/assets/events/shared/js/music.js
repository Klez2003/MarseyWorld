if (!playing_music() && !document.querySelector('.twitter-embed, .reddit-embed, .substack-embed, .tiktok-embed, .instagram-embed')) {
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
