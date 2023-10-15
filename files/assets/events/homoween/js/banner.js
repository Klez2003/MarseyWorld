const el = document.getElementById("banner-homoween-title");

const letters = el.getElementsByTagName("tspan");

for (let i = 0; i < letters.length; i++) {
	letters.item(i).style.transition = `all 600ms ${600 + i * 40}ms`;
}

setTimeout(() => el.classList.add("life"), 1000);
