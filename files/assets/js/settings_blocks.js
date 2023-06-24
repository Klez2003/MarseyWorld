function block_user(t) {
	const usernameField = document.getElementById("block-username");
	const isValidUsername = usernameField.checkValidity();
	username = usernameField.value;
	if (isValidUsername) {
		postToastReload(t,`/settings/block?username=${username}`);
	}
}

function unblock_user(t, url) {
	postToast(t, url,
		{
		},
		() => {
			t.parentElement.parentElement.remove();
		}
	);
}
