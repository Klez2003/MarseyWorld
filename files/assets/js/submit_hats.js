function approve_hat(t) {
	const name = t.dataset.name
	postToast(t, `/admin/approve/hat/${name}`,
		{
			"comment": document.getElementById(`${name}-comment`).value,
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
			"comment": document.getElementById(`${name}-comment`).value,
		},
		() => {
			document.getElementById(`${name}-hat`).remove()
		}
	);
}
