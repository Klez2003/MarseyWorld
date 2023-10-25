const orgy_file = document.getElementById('orgy-file');
const break_file = document.getElementById('break-file');

addEventListener("load", () => {
	orgy_file.play()
});

document.addEventListener('click', () => {
	if (orgy_file.paused) orgy_file.play();
}, {once : true});

function add_playing_listener() {
	orgy_file.addEventListener('playing', () => {
		const now = Date.now() / 1000;
		const created_utc = orgy_file.dataset.created_utc
		orgy_file.currentTime = now - created_utc
		if (screen_width < 768) {
			const chat_window_height = innerHeight - orgy_file.offsetHeight - 186
			document.getElementById('chat-window').setAttribute('style', `max-height: ${chat_window_height}px !important`)
		}
		setTimeout(add_waiting_listener, 5000);
	}, {once : true});
}

add_playing_listener()

orgy_file.addEventListener('pause', () => {
	add_playing_listener()
})

orgy_file.addEventListener("timeupdate", function(){
	if (break_file.dataset.run == "False" && parseInt(orgy_file.currentTime) == 3000) {
		break_file.dataset.run = "True"
		orgy_file.pause();
		orgy_file.classList.add('d-none');
		break_file.classList.remove('d-none');
		break_file.play()
		setTimeout(function () {
			break_file.pause()
			break_file.classList.add('d-none');
			orgy_file.classList.remove('d-none');
			orgy_file.dataset.created_utc = parseInt(orgy_file.dataset.created_utc) + 303
			orgy_file.play()
		}, 300000);
	}
});

orgy_file.addEventListener("ended", function(){
	location.reload()
});

function add_waiting_listener() {
	orgy_file.addEventListener('waiting', add_playing_listener, {once : true});
}
