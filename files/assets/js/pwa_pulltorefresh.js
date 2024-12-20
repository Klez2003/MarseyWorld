const standalone = navigator.standalone || window.matchMedia("(display-mode: standalone)").matches;
if (standalone) {
	const img = document.getElementById("pulltorefresh-img");
	const defaultImg = "/e/marseythinkorino.webp";
	const thresholdImg = "/e/marseythumbsup.webp";
	const threshold = -100;

	addEventListener("touchend", () => {
		if (window.scrollY < threshold) {
			location.reload();
		}
	});

	addEventListener("scroll", () => {
		img.setAttribute("src", window.scrollY < threshold ? thresholdImg : defaultImg);
	});
} else {
	const pulltorefresh = document.getElementById("pulltorefresh")
	if (pulltorefresh) pulltorefresh.remove();
}
