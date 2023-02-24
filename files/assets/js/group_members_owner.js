function approve_membership(t, url) {
	postToast(t, url,
		{
		},
		() => {
			t.parentElement.nextElementSibling.classList.remove('d-none');
			t.parentElement.innerHTML = formatDate(new Date());
		}
	);
}

function reject_membership(t, url) {
	postToast(t, url,
		{
		},
		() => {
			t.parentElement.parentElement.remove();
		}
	);
}
