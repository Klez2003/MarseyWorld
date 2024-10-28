// Jump scare function
function scare() {
	const jumpscare_audio = document.getElementById('jumpscare-audio')
	jumpscare_audio.play();

	const image = document.getElementById("jumpscare-img");
	image.style.display = "block";

	// Hide image and reset sound
	setTimeout(function() {
		image.style.display = "none";
		jumpscare_audio.pause()
		jumpscare_audio.currentTime = 0;
	}, 3000);
}

if (Math.random() <= 0.1) {
	setTimeout(function() {
		const xhr = new XMLHttpRequest();
		xhr.open("POST", "/jumpscare");
		xhr.setRequestHeader('xhr', 'xhr');
		form = new FormData();
		form.append("formkey", formkey());
		xhr.send(form)
		scare()
	}, 3000);
}
