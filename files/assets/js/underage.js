const SITE_NAME = document.querySelector("[name='application-name']").content
let audio = new Audio(`/assets/underage_${SITE_NAME}.mp3`);

audio.play();
if (audio.paused) {
	document.addEventListener('click', () => {
		if (audio.paused) audio.play();
	}, {once : true})
}
