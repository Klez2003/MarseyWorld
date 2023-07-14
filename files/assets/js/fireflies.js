const fireflies_num = document.getElementById('fireflies_num').value

new BugController({
	imageSprite: "/i/fireflies.webp",
	canDie: false,
	minBugs: MINFLIES + (fireflies_num * 2),
	maxBugs: MAXFLIES + (fireflies_num * 2),
	mouseOver: "multiply"
});
