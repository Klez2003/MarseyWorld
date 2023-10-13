function remove_orgy(t, created_utc) {
	postToast(t, `/admin/remove_orgy/${created_utc}`,
		{},
		() => {
			t.parentElement.parentElement.remove()
		}
	);
}
