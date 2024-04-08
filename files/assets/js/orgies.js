function remove_orgy(t, chat_id, created_utc) {
	postToast(t, `/chat/${chat_id}/remove_orgy/${created_utc}`,
		{},
		() => {
			t.parentElement.parentElement.remove()
		}
	);
}
