let prevScrollpos = window.pageYOffset;
window.onscroll = function () {
	const currentScrollPos = window.pageYOffset;

	const topBar = document.getElementById("fixed-bar-mobile");

	const bottomBar = document.getElementById("mobile-bottom-navigation-bar");

	const dropdown = document.getElementById("mobileSortDropdown");

	const navbar = document.getElementById("navbar");

	const bottomSafeAreaInset = parseInt(getComputedStyle(bottomBar).getPropertyValue("--safe-area-inset-bottom")) || 0;

	if (bottomBar != null) {
		if (prevScrollpos > currentScrollPos && (innerHeight + currentScrollPos) < (document.body.offsetHeight - 65)) {
			bottomBar.style.bottom = "0px";
		}
		else if (currentScrollPos <= 125 && (innerHeight + currentScrollPos) < (document.body.offsetHeight - 65)) {
			bottomBar.style.bottom = "0px";
		}
		else if (prevScrollpos > currentScrollPos && (innerHeight + currentScrollPos) >= (document.body.offsetHeight - 65)) {
			bottomBar.style.bottom = `-${50 + bottomSafeAreaInset}px`;
		}
		else {
			bottomBar.style.bottom = `-${50 + bottomSafeAreaInset}px`;
		}
	}

	if (topBar != null && dropdown != null) {
		if (prevScrollpos > currentScrollPos) {
			topBar.style.top = "48px";
			navbar.classList.remove("shadow");
		}
		else if (currentScrollPos <= 125) {
			topBar.style.top = "48px";
			navbar.classList.remove("shadow");
		}
		else {
			topBar.style.top = "-48px";
			dropdown.classList.remove('show');
			navbar.classList.add("shadow");
		}
	}
	prevScrollpos = currentScrollPos;
}
