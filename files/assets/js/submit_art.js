function approve_art(t, id) {
	postToast(t, `/admin/approve/art/${id}`,
		{
			"comment": document.getElementById(`${id}-comment`).value,
			"author": document.getElementById(`${id}-author`).value,
		},
		() => {
			document.getElementById(`${id}-art`).remove()
		}
	);
}

function remove_art(t, id) {
	postToast(t, `/remove/art/${id}`,
		{
			"comment": document.getElementById(`${id}-comment`).value,
		},
		() => {
			document.getElementById(`${id}-art`).remove()
		}
	);
}
