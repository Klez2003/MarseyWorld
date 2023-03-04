function approve_marsey(t, name) {
	postToast(t, `/admin/approve/marsey/${name}`,
		{
			"tags": document.getElementById(`${name}-tags`).value,
			"name": document.getElementById(`${name}-name`).value,
		},
		() => {
			document.getElementById(`${name}-marsey`).remove()
		}
	);
}

function remove_marsey(t, name) {
	postToast(t, `/remove/marsey/${name}`,
		{
		},
		() => {
			document.getElementById(`${name}-marsey`).remove()
		}
	);
}
