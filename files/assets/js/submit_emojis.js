function approve_marsey(t, name) {
	postToast(t, `/admin/approve/emoji/${name}`,
		{
			"tags": document.getElementById(`${name}-tags`).value,
			"name": document.getElementById(`${name}-name`).value,
			"kind": document.getElementById(`${name}-kind`).value,
		},
		() => {
			document.getElementById(`${name}-marsey`).remove()
		}
	);
}

function remove_marsey(t, name) {
	postToast(t, `/remove/emoji/${name}`,
		{
		},
		() => {
			document.getElementById(`${name}-marsey`).remove()
		}
	);
}
