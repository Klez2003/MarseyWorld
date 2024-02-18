let all_images
let position
let last_img_index

const imgnav_next = document.getElementById('imgnav-next')
const imgnav_prev = document.getElementById('imgnav-prev')

document.addEventListener('keydown', (e) => {
	if (['ArrowRight', 'd'].includes(e.key)  && imgnav_next && !imgnav_next.classList.contains('d-none')) {
		imgnav_next.click()
	}
	else if (['ArrowLeft', 'a'].includes(e.key)  && imgnav_prev && !imgnav_prev.classList.contains('d-none')) {
		imgnav_prev.click()
	}
})

function handle_navigation(delta) {
	position += delta
	if (position < last_img_index) {
		imgnav_next.classList.remove('d-none')
		imgnav_next.href = all_images[position+1].dataset.src
	}
	if (position > 0) {
		imgnav_prev.classList.remove('d-none')
		imgnav_prev.href = all_images[position-1].dataset.src
	}
}

const expandImageModal = document.getElementById('expandImageModal')

function expandImage(url) {
	document.getElementById('imgnav-next').classList.add('d-none')
	document.getElementById('imgnav-prev').classList.add('d-none')

	const e = this.event
	if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey)
		return;
	e.preventDefault();

	document.getElementById("expanded-image").src = '';
	document.getElementById("expanded-image-wrap-link").href = '';

	if (!url)
	{
		url = e.target.dataset.src
		if (!url) url = e.target.src
	}
	document.getElementById("expanded-image").src = url.replace("200w.webp", "giphy.webp");
	document.getElementById("expanded-image-wrap-link").href = url.replace("200w.webp", "giphy.webp");

	bootstrap.Modal.getOrCreateInstance(expandImageModal).show();
};


imgnav_next.onclick = () => {
	expandImage(imgnav_next.href)
	handle_navigation(1)
}

imgnav_prev.onclick = () => {
	expandImage(imgnav_prev.href)
	handle_navigation(-1)
}
