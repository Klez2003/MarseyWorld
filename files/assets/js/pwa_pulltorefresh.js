const standalone = navigator.standalone || matchMedia("(display-mode: standalone)").matches;
if (standalone) {
	const img = document.getElementById("pulltorefresh-img");
	const defaultImg = "/e/marseythinkorino.webp";
	const thresholdImg = "/e/marseythumbsup.webp";
	const threshold = -100;

	addEventListener("touchend", () => {
		if (scrollY < threshold) {
			location.reload();
		}
	});

	addEventListener("scroll", () => {
		img.setAttribute("src", scrollY < threshold ? thresholdImg : defaultImg);
	});
} else {
	const pulltorefresh = document.getElementById("pulltorefresh")
	if (pulltorefresh) pulltorefresh.remove();
}
