function remove_app(t, url) {
	postToast(t, url,
		{},
		() => {
			t.parentElement.parentElement.parentElement.remove()
		}
	);
}
