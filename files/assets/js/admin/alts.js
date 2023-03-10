function submitAddAlt(element, username) {
	element.disabled = true;
	element.classList.add('disabled');
	const form = new FormData();
	form.append('other_username', document.getElementById('link-input-other').value);
	const xhr = createXhrWithFormKey(`/@${username}/alts/`, 'POST', form);
	xhr[0].onload = () => {
		let data;
		try {
			data = JSON.parse(xhr[0].response);
		}
		catch(e) {
			console.log(e);
		}
		if (xhr[0].status >= 200 && xhr[0].status < 300) {
			showToast(true, getMessageFromJsonData(true, data));
			location.reload();
		} else {
			showToast(false, getMessageFromJsonData(false, data));
			element.disabled = false;
			element.classList.remove('disabled');
		}
	}
	xhr[0].send(xhr[1]);
}

function delink(t, url) {
	postToast(t, url,
		{},
		() => {
			t.parentElement.parentElement.remove()
		}
	);
}
