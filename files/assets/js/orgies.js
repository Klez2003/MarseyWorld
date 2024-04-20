function remove_orgy(t, chat_id, created_utc) {
	postToast(t, `/chat/${chat_id}/remove_orgy/${created_utc}`,
		{},
		() => {
			t.parentElement.parentElement.remove()
		}
	);
}

document.addEventListener('keydown', (e) => {
	if (!((e.ctrlKey || e.metaKey) && e.key === "Enter"))
		return;

	document.getElementById('start-orgy').click();
});


function autoSuggestTitle()	{
	const urlField = document.getElementById("link");
	const titleField = document.getElementById("title");
	const isValidURL = urlField.checkValidity();

	if (isValidURL && urlField.value.length > 0 && titleField.value === "") {
		const x = new XMLHttpRequest();
		x.onreadystatechange = function() {
			if (x.readyState == 4 && x.status == 200 && !titleField.value) {
				title = JSON.parse(x.responseText)["title"];
				titleField.value = title.slice(0, 40);
			}
		}
		x.open('get','/submit/title?url=' + urlField.value);
		x.setRequestHeader('xhr', 'xhr');
		x.send(null);
	};
};
