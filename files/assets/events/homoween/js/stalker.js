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

let stalkers = [],
	a = Math.round(size * diameter * 0.2),
	current = offset,
	mouse = {
		x: a + offset,
		y: a + offset
	};

// populate stalkers
for (let i = 0; i < count; i++) {
	stalkers[i] = new stalker(i);
}

function stalker(i) {
	this.x = 0;
	this.y = 0;
	this.X = 0;
	this.Y = 0;
	this.img = document.createElement("img");
	this.img.id = "stalker-" + i;
	this.img.className = "cursor-stalker";
	this.img.src = `${SITE_FULL_IMAGES}/e/${assets[i]}.webp`;
	stalker_container.appendChild(this.img);
}

function placestalker(stalker, x, y) {
	stalker.x = x;
	stalker.y = y;
	const left = stalker.x + "px";
	const top =  stalker.y + "px";
	stalker.img.style.transform = `translate(${left}, ${top})`
}

function makeCircle() {
	let stalker;
	current -= rotation;
	for (let i = count - 1; i > -1; --i) {
		stalker = stalkers[i];
		const top = Math.round(stalker.y + a * Math.sin((current + i) / spacing) - 15) + "px";
		const left = Math.round(stalker.x + a * Math.cos((current + i) / spacing)) + "px";
		stalker.img.style.transform = `translate(${left}, ${top})`
	}
}

addEventListener("mousemove", function(e) {
	mouse.x = e.pageX;
	mouse.y = e.pageY;
});

function getRandom(min, max) {
	return Math.floor(Math.random() * (max - min + 1) + min);
}

function draw_stalker() {
	let stalker = stalkers[0];
	let prevstalker = stalkers[0];
	stalker.x = stalker.X += (mouse.x - stalker.X) * speed;
	if (innerWidth < 768) {
		stalker.x = Math.min(stalker.x, innerWidth * 0.5);
	}
	stalker.y = stalker.Y += (mouse.y - stalker.Y) * speed;
	for (let i = count - 1; i > 0; --i) {
		stalker = stalkers[i];
		prevstalker = stalkers[i - 1];
		stalker.x = stalker.X += (prevstalker.x - stalker.X) * speed;
		stalker.y = stalker.Y += (prevstalker.y - stalker.Y) * speed;
	}
	makeCircle();
	requestAnimationFrame(draw_stalker);
}

draw_stalker();
