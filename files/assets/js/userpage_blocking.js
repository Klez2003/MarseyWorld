function unblock_user(t, url) {
	postToast(t, url,
		{
		},
		() => {
			t.parentElement.parentElement.remove();
		}
	);
}
