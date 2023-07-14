const shit_num = document.getElementById('shit_num').value

new BugController({
	imageSprite: "/i/fly-sprite.webp",
	canDie: false,
	minBugs: Math.min(MINFLIES + (shit_num * 2), 50),
	maxBugs: Math.min(MAXFLIES + (shit_num * 2), 100),
	mouseOver: "multiply"
});
