function approve_emoji(t, name) {
	postToast(t, `/admin/approve/emoji/${name}`,
		{
			"tags": document.getElementById(`${name}-tags`).value,
			"name": document.getElementById(`${name}-name`).value,
			"kind": document.getElementById(`${name}-kind`).value,
			"over_18": document.getElementById(`${name}-over-18`).value,
		},
		() => {
			document.getElementById(`${name}-emoji`).remove()
		}
	);
}

function remove_emoji(t, name) {
	postToast(t, `/remove/emoji/${name}`,
		{
		},
		() => {
			document.getElementById(`${name}-emoji`).remove()
		}
	);
}
