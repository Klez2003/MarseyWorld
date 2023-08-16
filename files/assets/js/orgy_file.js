const orgy_file = document.getElementById('orgy-file');

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
	}, {once : true});
}

add_playing_listener()

orgy_file.addEventListener('pause', () => {
	add_playing_listener()
})
