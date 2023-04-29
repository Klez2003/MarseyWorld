const marsekoEl = document.getElementById("marseko");
let marsekoPosX = 32;
let marsekoPosY = 32;
let mousePosX = 0;
let mousePosY = 0;
let frameCount = 0;
let idleTime = 0;
let idleAnimation = null;
let idleAnimationFrame = 0;
const marsekoSpeed = 10;
const spriteSets = {
	idle: [[-3, -3]],
	alert: [[-7, -3]],
	scratchSelf: [
	[-5, 0],
	[-6, 0],
	[-7, 0],
	],
	scratchWallN: [
	[0, 0],
	[0, -1],
	],
	scratchWallS: [
	[-7, -1],
	[-6, -2],
	],
	scratchWallE: [
	[-2, -2],
	[-2, -3],
	],
	scratchWallW: [
	[-4, 0],
	[-4, -1],
	],
	tired: [[-3, -2]],
	sleeping: [
	[-2, 0],
	[-2, -1],
	],
	N: [
	[-1, -2],
	[-1, -3],
	],
	NE: [
	[0, -2],
	[0, -3],
	],
	E: [
	[-3, 0],
	[-3, -1],
	],
	SE: [
	[-5, -1],
	[-5, -2],
	],
	S: [
	[-6, -3],
	[-7, -2],
	],
	SW: [
	[-5, -3],
	[-6, -1],
	],
	W: [
	[-4, -2],
	[-4, -3],
	],
	NW: [
	[-1, 0],
	[-1, -1],
	],
};

function setSprite(name, frame) {
	const sprite = spriteSets[name][frame % spriteSets[name].length];
	marsekoEl.style.backgroundPosition = `${sprite[0] * 32}px ${sprite[1] * 32}px`;
}

function resetIdleAnimation() {
	idleAnimation = null;
	idleAnimationFrame = 0;
}

function idle() {
	idleTime += 1;

	// every ~ 20 seconds
	if (idleTime > 10 && true && idleAnimation == null) {
	let avalibleIdleAnimations = ["sleeping", "scratchSelf"];
	if (marsekoPosX < 32) {
		avalibleIdleAnimations.push("scratchWallW");
	}
	if (marsekoPosY < 32) {
		avalibleIdleAnimations.push("scratchWallN");
	}
	if (marsekoPosX > window.innerWidth - 32) {
		avalibleIdleAnimations.push("scratchWallE");
	}
	if (marsekoPosY > window.innerHeight - 32) {
		avalibleIdleAnimations.push("scratchWallS");
	}
	idleAnimation =
		avalibleIdleAnimations[
		Math.floor(Math.random() * avalibleIdleAnimations.length)
		];
	}

	switch (idleAnimation) {
	case "sleeping":
		if (idleAnimationFrame < 8) {
		setSprite("tired", 0);
		break;
		}
		setSprite("sleeping", Math.floor(idleAnimationFrame / 4));
		if (idleAnimationFrame > 192) {
		resetIdleAnimation();
		}
		break;
	case "scratchWallN":
	case "scratchWallS":
	case "scratchWallE":
	case "scratchWallW":
	case "scratchSelf":
		setSprite(idleAnimation, idleAnimationFrame);
		if (idleAnimationFrame > 9) {
		resetIdleAnimation();
		}
		break;
	default:
		setSprite("idle", 0);
		return;
	}
	idleAnimationFrame += 1;
}

function frame() {
	frameCount += 1;
	const diffX = marsekoPosX - mousePosX;
	const diffY = marsekoPosY - mousePosY;
	const distance = Math.sqrt(diffX ** 2 + diffY ** 2);

	if (distance < marsekoSpeed || distance < 48) {
	idle();
	return;
	}

	idleAnimation = null;
	idleAnimationFrame = 0;

	if (idleTime > 1) {
	setSprite("alert", 0);
	// count down after being alerted before moving
	idleTime = Math.min(idleTime, 7);
	idleTime -= 1;
	return;
	}

	direction = diffY / distance > 0.5 ? "N" : "";
	direction += diffY / distance < -0.5 ? "S" : "";
	direction += diffX / distance > 0.5 ? "W" : "";
	direction += diffX / distance < -0.5 ? "E" : "";
	setSprite(direction, frameCount);

	marsekoPosX -= (diffX / distance) * marsekoSpeed;
	marsekoPosY -= (diffY / distance) * marsekoSpeed;

	marsekoPosX = Math.min(Math.max(16, marsekoPosX), window.innerWidth - 16);
	marsekoPosY = Math.min(Math.max(16, marsekoPosY), window.innerHeight - 16);

	marsekoEl.style.left = `${marsekoPosX - 16}px`;
	marsekoEl.style.top = `${marsekoPosY - 16}px`;
}

document.onmousemove = (event) => {
		mousePosX = event.clientX;
		mousePosY = event.clientY;
	};
window.marseykoInterval = setInterval(frame, 100);

function getRandomInt(max) {
	return Math.floor(Math.random() * max);
}
const random_left = getRandomInt(screen.width)
const random_top = getRandomInt(screen.height)

marsekoEl.style.left = `${random_left}px`;
marsekoEl.style.top = `${random_top}px`;
