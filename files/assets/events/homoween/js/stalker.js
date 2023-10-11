const assets = [
	"marseyjason",
	"marseynightmare",
	"marseyhellraiser",
	"marseysaw",
	"marseyzombie2",
	"marseywerewolf",
	"marseysatangoat",
	"marseyskeleton2",
	"marseystabby",
	"marseyface",
	"marseydaemon",
	"marseygrimreaper",
	"marseycheshire4",
	"marseyaugust",
	"marseycerebrus",
	"marseyzombie",
	"marseything",
	"marseytwins",
	"marseymonstrosity",
	"marseykrampus",
	"marseybaphomet",
	"marseyfacepeel",
	"carpwitchtrans",
	"capymummy",
	"marseynotesbardfinn"
];

const stalker_container = document.getElementById("stalkers-container")

const count = parseInt(stalker_container.dataset.stalkersCount),
	size = 25,
	spacing = 4 - 0.05 * count,
	diameter = 20 + 0.5 * count,
	rotation = 0.04 + 0.001 * count,
	speed = 0.03 + 0.002 * count,
	offset = 10;

let ghosts = [],
	a = Math.round(size * diameter * 0.2),
	current = offset,
	mouse = {
		x: a + offset,
		y: a + offset
	};

// populate ghosts
for (let i = 0; i < count; i++) {
	ghosts[i] = new ghost(i);
}

function ghost(i) {
	this.x = 0;
	this.y = 0;
	this.X = 0;
	this.Y = 0;
	this.img = document.createElement("img");
	this.img.id = "ghost-" + i;
	this.img.className = "cursor-stalker";
	this.img.src = `${SITE_FULL_IMAGES}/e/${assets[i]}.webp`;
	stalker_container.appendChild(this.img);
}

function placeghost(ghost, x, y) {
	ghost.x = x;
	ghost.y = y;
	ghost.img.style.left = ghost.x + "px";
	ghost.img.style.top = ghost.y + "px";
}

function makeCircle() {
	let ghost;
	current -= rotation;
	for (let i = count - 1; i > -1; --i) {
		ghost = ghosts[i];
		ghost.img.style.top =
		Math.round(ghost.y + a * Math.sin((current + i) / spacing) - 15) + "px";
		ghost.img.style.left =
		Math.round(ghost.x + a * Math.cos((current + i) / spacing)) + "px";
	}
}

addEventListener("mousemove", function (e) {
	mouse.x = e.pageX;
	mouse.y = e.pageY;
});

addEventListener("touchstart", function (e) {
	event.preventDefault(); // we don't want to scroll
	let touch = event.touches[0];
	mouse.x = touch.clientX;
	mouse.y = touch.clientY;
});

function getRandom(min, max) {
	return Math.floor(Math.random() * (max - min + 1) + min);
}

function draw() {
	let ghost = ghosts[0];
	let prevghost = ghosts[0];
	ghost.x = ghost.X += (mouse.x - ghost.X) * speed;
	ghost.x = Math.min(ghost.x, screen_width * 0.7);
	ghost.y = ghost.Y += (mouse.y - ghost.Y) * speed;
	for (let i = count - 1; i > 0; --i) {
		ghost = ghosts[i];
		prevghost = ghosts[i - 1];
		ghost.x = ghost.X += (prevghost.x - ghost.X) * speed;
		ghost.y = ghost.Y += (prevghost.y - ghost.Y) * speed;
	}
	makeCircle();
	requestAnimationFrame(draw);
}

draw();
