function unchud_or_unban(t, url) {
	postToast(t, url,
	{
	},
	() => {
		t.classList.add('d-none');
		t.nextElementSibling.classList.remove('d-none');
	});
}

function delReport(t, url) {
	postToast(t, url,
		{
		},
		() => {
			t.parentElement.remove()
		}
	);
}
