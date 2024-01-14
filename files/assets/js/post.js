function highlight_unread(localstoragevar) {
	const comments = JSON.parse(localStorage.getItem(localstoragevar)) || {}

	lastCount = comments[pid]
	if (lastCount)
	{
		const comms = document.getElementById("comms").value.slice(0, -1).split(',')
		for (let c of comms) {
			c = c.split(':')
			if (c[1]*1000 > lastCount.t) {
				try {document.getElementById(`comment-${c[0]}-only`).classList.add('unread')}
				catch(e) {}
			}
		}
	}
}

highlight_unread("comment-counts")

if (!location.href.includes("#context")) {
	localStorage.setItem("old-comment-counts", localStorage.getItem("comment-counts"))

	const comments = JSON.parse(localStorage.getItem("comment-counts")) || {}
	const newTotal = pcc || ((comments[pid] || {c: 0}).c + 1)
	comments[pid] = {c: newTotal, t: Date.now()}
	localStorage.setItem("comment-counts", JSON.stringify(comments))
}

const fake_textarea = document.querySelector('[data-href]')
if (fake_textarea) {
	fake_textarea.addEventListener('click', () => {
		location.href = fake_textarea.dataset.href;
	});
}











//SWIPING


const post_ids = localStorage.getItem("post_ids").split(', ');
const current_index = post_ids.indexOf(pid)
const id_after = post_ids[current_index+1]
const id_before = post_ids[current_index-1]

const _C = document.querySelector('.container')
const N = _C.children.length
const NF = 30

let i = 0, x0 = null, y0 = null, locked = false, w, ini, fin, rID = null, anf, n;

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

		if (!getSelection().toString() && (f > 0.04 || f < -0.04) && (fy < 0.02 && fy > -0.02)) {
			if (id_before && (f > 0.15 || (screen_width > 768 && f > 0.1))) {
				location.href = `/post/${id_before}`
			}
			if (id_after && (f < -0.15 || (screen_width > 768 && f < -0.1))) {
				location.href = `/post/${id_after}`
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
_C.style.setProperty('--n', N);

addEventListener('resize', size, false);

_C.addEventListener('mousedown', lock, false);
_C.addEventListener('touchstart', lock, false);

_C.addEventListener('mousemove', drag, false);
_C.addEventListener('touchmove', drag, false);

_C.addEventListener('mouseup', move, false);
_C.addEventListener('touchend', move, false);
