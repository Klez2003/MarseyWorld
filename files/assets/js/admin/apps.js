function remove_app(t, url) {
	postToast(t, url,
		{},
		() => {
			t.parentElement.parentElement.parentElement.remove()
		}
	);
}

function approve_app(t, url) {
	postToast(t, url,
		{},
		() => {
			t.nextElementSibling.classList.remove('d-none')
			t.previousElementSibling.remove()
			t.remove()
		}
	);
}
