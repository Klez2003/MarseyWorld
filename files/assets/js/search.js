function addParam(t, bool) {
	let text = t.innerText;
	if (bool)
		text = text + ' '
	else
		text = text.split(":")[0] + ':';
	let searchInput = document.querySelector("#large_searchbar input");
	searchInput.value = `${searchInput.value} ${text}`;
	searchInput.focus();
}
