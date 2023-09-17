function approve_hat(t) {
	const name = t.dataset.name
	postToast(t, `/admin/approve/hat/${name}`,
		{
			"description": document.getElementById(`${name}-description`).value,
			"name": document.getElementById(`${name}-name`).value,
			"price": document.getElementById(`${name}-price`).value,
		},
		() => {
			document.getElementById(`${name}-hat`).remove()
		}
	);
}

function remove_hat(t) {
	const name = t.dataset.name
	postToast(t, `/remove/hat/${name}`,
		{
		},
		() => {
			document.getElementById(`${name}-hat`).remove()
		}
	);
}
