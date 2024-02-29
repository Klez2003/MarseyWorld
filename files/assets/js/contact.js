function contact(form) {
	sendFormXHR(form,
		() => {
			document.getElementById('input-message').value = null;
		}
	)
}
