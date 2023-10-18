const music_playing = localStorage.getItem("music_playing") == 'true'

const audio = document.getElementById('profile-song')

audio.addEventListener('play', () => {
	localStorage.setItem("music_playing", true);
})

window.addEventListener('beforeunload', () => {
	localStorage.setItem("music_playing", false);
})

let u_username = document.getElementById('u_username')
const anthem_button = document.getElementById('toggle-anthem')
const anthem_button_mobile = document.getElementById('toggle-anthem-mobile')

function play_audio(audio) {
	audio.play()
	if (anthem_button && !audio.paused) {
		anthem_button.classList.add('text-primary')
		anthem_button_mobile.classList.add('text-primary')
	}
}

function pause_audio(audio) {
	audio.pause()
	if (anthem_button && audio.paused) {
		anthem_button.classList.remove('text-primary')
		anthem_button_mobile.classList.remove('text-primary')
	}
}

if (u_username)
{
	function toggle() {
		if (audio.paused) {
			play_audio(audio);
		}
		else {
			pause_audio(audio);
		}
	}

	if (!music_playing) {
		play_audio(audio);
		document.addEventListener('click', (e) => {
			if (e.target.id.startsWith("toggle-anthem"))
				return
			if (audio.paused) play_audio(audio);
		}, {once : true});

		prepare_to_pause(audio)
	}
}
else
{
	let v_username = document.getElementById('v_username')
	if (v_username)
	{
		v_username = v_username.innerHTML

		const paused = localStorage.getItem("paused")

		function toggle() {
			if (audio.paused)
			{
				play_audio(audio)
				localStorage.setItem("paused", "")
			}
			else
			{
				pause_audio(audio)
				localStorage.setItem("paused", "1")
			}
		}

		if (!paused && !music_playing)
		{
			play_audio(audio);
			document.addEventListener('click', (e) => {
				if (e.target.id.startsWith("toggle-anthem"))
					return
				if (audio.paused) play_audio(audio);
			}, {once : true});

			prepare_to_pause(audio)
		}
	}
}
