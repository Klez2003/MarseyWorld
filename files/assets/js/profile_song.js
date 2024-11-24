const audio = document.getElementById('profile-song')

handle_playing_music(audio)

let u_username = document.getElementById('u_username')
const anthem_button = document.getElementById('toggle-anthem')
const anthem_button_mobile = document.getElementById('toggle-anthem-mobile')

function play_audio(audio) {
	audio.play()
	prepare_to_pause(audio)
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

function play_profile_song() {
	if (playing_music() || document.querySelector('.twitter-embed, .reddit-embed, .substack-embed, .tiktok-embed, .instagram-embed'))
		return

	addEventListener("load", () => {
		play_audio(audio);
		document.addEventListener('click', (e) => {
			if (e.target.id.startsWith("toggle-anthem"))
				return
			if (audio.paused) play_audio(audio);
		}, {once : true});
	})
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

	play_profile_song()
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

		if (!paused)
			play_profile_song()
	}
}
