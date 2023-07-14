const fireflies_num = document.getElementById('fireflies_num').value

new BugController({
	imageSprite: "/i/fireflies.webp",
	canDie: false,
	minBugs: Math.min(MINFLIES + (fireflies_num * 2), ACTUALMAXFILES),
	maxBugs: Math.min(MAXFLIES + (fireflies_num * 2), ACTUALMAXFILES),
	mouseOver: "multiply"
});
