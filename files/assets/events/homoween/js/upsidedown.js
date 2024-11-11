let st = init("canvas"),
w = (canvas.width = innerWidth),
h = (canvas.height = innerHeight);

class firefly {
	constructor() {
		this.x = Math.random() * w;
		this.y = Math.random() * h;
		this.s = Math.random() * 2;
		this.ang = Math.random() * 2 * Math.PI;
		this.v = (this.s * this.s) / 4;
	}
	move() {
		this.x += this.v * Math.cos(this.ang);
		this.y += this.v * Math.sin(this.ang);
		this.ang += (Math.random() * 20 * Math.PI) / 180 - (10 * Math.PI) / 180;
	}
	show() {
		st.beginPath();
		st.arc(this.x, this.y, this.s, 0, 2 * Math.PI);
		st.fillStyle = "#fff";
		st.fill();
	}
}

let f = [];

let num_fireflies = 10
if (innerWidth >= 768) {
	num_fireflies = 50
}

function draw_upsidedown() {
	if (f.length < num_fireflies) {
		for (let j = 0; j < 10; j++) {
			f.push(new firefly());
		}
	}
	//animation
	for (let i = 0; i < f.length; i++) {
		f[i].move();
		f[i].show();
		if (f[i].x < 0 || f[i].x > w || f[i].y < 0 || f[i].y > h) {
			f.splice(i, 1);
		}
	}
}

function init(elemid) {
	let canvas = document.getElementById(elemid),
		st = canvas.getContext("2d"),
		w = (canvas.width = innerWidth),
		h = (canvas.height = innerHeight);
	st.fillStyle = "rgba(30,30,30,1)";
	st.fillRect(0, 0, w, h);
	return st;
}

function loop() {
	st.clearRect(0, 0, w, h);
	draw_upsidedown();
}

loop();
setInterval(loop, 1000 / 60);
