const cursormarseyEl = document.getElementById("cursormarsey");
const heartEl = document.getElementById("cursormarsey-heart");

function getInitialPosition(max) {
	return Math.max(32, Math.floor(Math.random() * max));
}
let cursormarseyPosX = getInitialPosition(screen.availWidth - 20);
let cursormarseyPosY = getInitialPosition(screen.availHeight - 50);
cursormarseyEl.style.left = `${cursormarseyPosX}px`;
cursormarseyEl.style.top = `${cursormarseyPosY}px`;
heartEl.style.left = `${cursormarseyPosX+16}px`;
heartEl.style.top = `${cursormarseyPosY-16}px`;

let mousePosX = cursormarseyPosX;
let mousePosY = cursormarseyPosY;

let frameCount = 0;
let idleTime = 0;
let idleAnimation = null;
let idleAnimationFrame = 0;
const cursormarseySpeed = 10;
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
	cursormarseyEl.style.backgroundPosition = `${sprite[0] * 32}px ${sprite[1] * 32}px`;
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
	if (cursormarseyPosX < 32) {
		avalibleIdleAnimations.push("scratchWallW");
	}
	if (cursormarseyPosY < 32) {
		avalibleIdleAnimations.push("scratchWallN");
	}
	if (cursormarseyPosX > innerWidth - 32) {
		avalibleIdleAnimations.push("scratchWallE");
	}
	if (cursormarseyPosY > innerHeight - 32) {
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
	const diffX = cursormarseyPosX - mousePosX;
	const diffY = cursormarseyPosY - mousePosY;
	const distance = Math.sqrt(diffX ** 2 + diffY ** 2);

	if (distance < cursormarseySpeed || distance < 100) {
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

	cursormarseyPosX -= (diffX / distance) * cursormarseySpeed;
	cursormarseyPosY -= (diffY / distance) * cursormarseySpeed;

	cursormarseyPosX = Math.min(Math.max(16, cursormarseyPosX), innerWidth - 16);
	cursormarseyPosY = Math.min(Math.max(16, cursormarseyPosY), innerHeight - 16);

	cursormarseyEl.style.left = `${cursormarseyPosX}px`;
	cursormarseyEl.style.top = `${cursormarseyPosY}px`;
	heartEl.style.left = `${cursormarseyPosX+16}px`;
	heartEl.style.top = `${cursormarseyPosY-16}px`;
}

document.onmousemove = (event) => {
		mousePosX = event.clientX;
		mousePosY = event.clientY;
	};
window.marseykoInterval = setInterval(frame, 100);

document.addEventListener('click', (event) => {
	cursormarseyEl.style.removeProperty("pointer-events");
	let elementClicked = document.elementFromPoint(event.clientX,event.clientY);
	if (elementClicked && elementClicked.id === cursormarseyEl.id) {
		heartEl.classList.remove("d-none");
		setTimeout(() => {
			heartEl.classList.add("d-none");
		}, 2000);
	}
	cursormarseyEl.style.pointerEvents = "none";
});
