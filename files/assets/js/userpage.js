function badge_timestamp(t) {
	const date = formatTime(new Date(t.dataset.until*1000));
	const text = t.getAttribute("data-bs-original-title")
	t.setAttribute("data-bs-original-title", `${text} ${date.toString()}`);
	t.removeAttribute("data-onmouseover")
}

addEventListener("load", () => {
	const el = document.getElementById("desktopUserBanner")
	const style = el.getAttribute("data-style")
	el.setAttribute("style", style)
}, {once : true});
