let bones_container = document.getElementById('bones-container');
let number = parseInt(bones_container.dataset.bones)
const sources = ['skeleton1.webp','skeleton2.webp','skeleton3.webp','skeleton4.webp','skeleton5.webp','skeleton6.webp'];

const pw = screen.availWidth / 3.2

let circles = [];

for (let i = 0; i < number; i++) {
	addCircle(i * 150, [10 + 0, pw]);
	addCircle(i * 150, [10 + 0, -pw]);
	addCircle(i * 150, [10 - (0.5*pw), -pw]);
	addCircle(i * 150, [10 + (0.5*pw), pw]);
	addCircle(i * 150, [10 - (1.5*pw), -pw]);
	addCircle(i * 150, [10 + (1.5*pw), pw]);
}


function addCircle(delay, range) {
	setTimeout(function() {
		let c = new Circle(range[0] + Math.random() * range[1], 80 + Math.random() * 4, {
			x: -0.15 + Math.random() * 0.3,
			y: 1 + Math.random() * 1
		}, range);
		circles.push(c);
	}, delay);
}

function random_emoji() {
	return sources[Math.floor(Math.random() * sources.length)]
}

function Circle(x, y, v, range) {
	let _this = this;
	this.x = x;
	this.y = y;
	this.v = v;
	this.range = range;
	this.element = document.createElement('img');
	this.element.style.opacity = 0;
	this.element.style.position = 'absolute';
	this.element.style.height = '3rem';
	this.element.src = `${SITE_FULL_IMAGES}/assets/events/homoween/images/skeletons/${random_emoji()}`;
	bones_container.appendChild(this.element);

	this.update = function() {
		if (_this.y > innerHeight) {
			_this.y = 80 + Math.random() * 4;
			_this.x = _this.range[0] + Math.random() * _this.range[1];
		}
		_this.y += _this.v.y;
		_this.x += _this.v.x;
		this.element.style.opacity = 1;
		this.element.style.transform = 'translate3d(' + _this.x + 'px, ' + _this.y + 'px, 0px)';
		this.element.style.mozTransform = 'translate3d(' + _this.x + 'px, ' + _this.y + 'px, 0px)';
	};
}

function animate() {
	for (let i in circles) {
		circles[i].update();
	}
	requestAnimationFrame(animate);
}

animate();
