function post(url) {
	const xhr = new XMLHttpRequest();
	xhr.open("POST", url);
	xhr.setRequestHeader('xhr', 'xhr');
	const form = new FormData()
	form.append("formkey", formkey());
	xhr.onload = function() {location.reload();};
	xhr.send(form);
};

function updatebgselection() {
	const bgselector = document.getElementById("backgroundSelector");
	const backgrounds = [
		{
			folder: "glitter",
			backgrounds:
			[
				"1.webp",
				"2.webp",
				"3.webp",
				"4.webp",
				"5.webp",
			]
		},
		{
			folder: "anime",
			backgrounds:
			[
				"1.webp",
				"2.webp",
				"3.webp",
				"4.webp",
				"5.webp",
				"6.webp",
			]
		},
		{
			folder: "fantasy",
			backgrounds:
			[
				"1.webp",
				"2.webp",
				"3.webp",
				"4.webp",
				"5.webp",
				"6.webp",
			]
		},
		{
			folder: "solarpunk",
			backgrounds:
			[
				"1.webp",
				"2.webp",
				"3.webp",
				"4.webp",
				"5.webp",
				"6.webp",
				"7.webp",
				"8.webp",
				"9.webp",
				"10.webp",
				"11.webp",
				"12.webp",
				"13.webp",
				"14.webp",
				"15.webp",
				"16.webp",
				"17.webp",
				"18.webp",
				"19.webp",
			]
		},
		{
			folder: "pixelart",
			backgrounds:
			[
				"1.webp",
				"2.webp",
				"3.webp",
				"4.webp",
				"5.webp",
			]
		},
	]
	let bgContainer = document.getElementById(`bgcontainer`);
	let str = '';
	let bgsToDisplay = backgrounds[bgselector.selectedIndex].backgrounds;
	let bgsDir = backgrounds[bgselector.selectedIndex].folder;
	for (i=0; i < bgsToDisplay.length; i++) {
		let onclickPost = bgsDir + "/" + bgsToDisplay[i];
		str += `<button class="btn btn-secondary bg-button"><img loading="lazy" class='bg-image' src="${SITE_FULL_IMAGES}/i/backgrounds/${bgsDir}/${bgsToDisplay[i]}?x=18" alt="${bgsToDisplay[i]}-background" data-nonce="${nonce}" data-onclick="post('/settings/personal?background=${onclickPost}')"></button>`;
	}
	bgContainer.innerHTML = str;

	if (typeof register_new_elements === "function") {
		register_new_elements(bgContainer)
	}
}
updatebgselection();

function submit(t) {
	sendFormXHRReload(t.form)
}