const shit_num = document.getElementById('shit_num').value

new BugController({
	imageSprite: "/i/fly-sprite.webp",
	canDie: false,
	minBugs: MINFLIES + (shit_num * 2),
	maxBugs: MAXFLIES + (shit_num * 2),
	mouseOver: "multiply"
});
