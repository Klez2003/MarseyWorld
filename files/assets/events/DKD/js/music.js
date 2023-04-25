const song = document.getElementById('DKD-song').value;
const audio = new Audio(song);
audio.loop=true;

audio.play();
document.addEventListener('click', () => {
	if (audio.paused) audio.play();
}, {once : true});
prepare_to_pause(audio)
