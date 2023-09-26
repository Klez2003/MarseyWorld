//youtube
const playbtn = document.querySelector('#orgy-file-container > lite-youtube > .lty-playbtn')
if (playbtn) playbtn.click()


//file
const orgy_file = document.getElementById('orgy-file');
if (orgy_file) {
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
		}, {once : true});
	}

	add_playing_listener()

	orgy_file.addEventListener('pause', () => {
		add_playing_listener()
	})

	orgy_file.addEventListener("timeupdate", function(){
		if (break_file.dataset.run == "0" && parseInt(orgy_file.currentTime) == 3000) {
			break_file.dataset.run = "1"
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
}
