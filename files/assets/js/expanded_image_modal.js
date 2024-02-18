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

//swiping
if (screen_width < 768) {
	let active = true
	const _C = document.querySelector('#expandImageModal')
	const N = _C.children.length
	const NF = 30

	let i = 0, x0 = null, y0 = null, locked = false, w, ini, fin, anf, n;

	function unify(e) {	return e.changedTouches ? e.changedTouches[0] : e };

	function lock(e) {
		x0 = unify(e).clientX;
		y0 = unify(e).clientY;
		locked = true
	};

	function drag(e) {
		if(locked) {
			let dx = unify(e).clientX - x0
			let f = +(dx/w).toFixed(2);

			let dy = unify(e).clientY - y0
			let fy = +(dy/y).toFixed(2);

			if (active && (f > 0.04 || f < -0.04) && (fy < 0.03 && fy > -0.03)) {
				if (f > 0.2) {
					active = false;
					imgnav_prev.click()
					setTimeout(() => {
						active = true;
					}, 200);
				}
				if (f < -0.2) {
					active = false;
					imgnav_next.click()
					setTimeout(() => {
						active = true;
					}, 200);
				}
			}
		}
	};

	function move(e) {
	if(locked) {
		let dx = unify(e).clientX - x0, 
			s = Math.sign(dx), 
			f = +(s*dx/w).toFixed(2);

		ini = i - s*f;

		if((i > 0 || s < 0) && (i < N - 1 || s > 0) && f > .2) {
		i -= s;
		f = 1 - f
		}

		fin = i;
			anf = Math.round(f*NF);
			n = 2 + Math.round(f)
		x0 = null;
		y0 = null;
		locked = false;
	}
	};

	function size() {
		w = window.innerWidth
		y = window.innerHeight
	};

	size();

	addEventListener('resize', size, false);

	_C.addEventListener('mousedown', lock, false);
	_C.addEventListener('touchstart', lock, false);

	_C.addEventListener('mousemove', drag, false);
	_C.addEventListener('touchmove', drag, false);

	_C.addEventListener('mouseup', move, false);
	_C.addEventListener('touchend', move, false);
}
