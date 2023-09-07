function unmute_notifs(t, url) {
	postToast(t, url,
		{
		},
		() => {
			t.parentElement.parentElement.remove();
		}
	);
}
