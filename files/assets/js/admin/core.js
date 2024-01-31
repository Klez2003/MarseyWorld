function unchud_or_unban(t, url) {
	postToast(t, url,
	{
	},
	() => {
		t.classList.add('d-none');
		t.previousElementSibling.classList.remove('d-none');
	});
}
