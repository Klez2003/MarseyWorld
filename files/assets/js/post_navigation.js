const post_permalinks = sessionStorage.getItem("post_permalinks").split(', ');
const current_index = post_permalinks.indexOf(`'${location.href}'`)
if (current_index > -1) {
	const id_after = post_permalinks[current_index+1]
	const id_before = post_permalinks[current_index-1]

	if (id_before || id_after) {
		document.getElementById('post_navigation').classList.remove('d-none')
	}

	if (id_before) {
		document.getElementById('post_before').classList.remove('disabled')
		document.getElementById('post_before').href = id_before.slice(1, -1)
	}

	if (id_after) {
		document.getElementById('post_after').classList.remove('disabled')
		document.getElementById('post_after').href = id_after.slice(1, -1)
	}

	document.addEventListener('keydown', (e) => {
		if (document.activeElement.tagName != 'TEXTAREA' && document.activeElement.tagName != 'INPUT') {
			if (id_before && e.key == 'ArrowLeft') {
				location.href = id_before.slice(1, -1)
			}
			else if (id_after && e.key == 'ArrowRight') {
				location.href = id_after.slice(1, -1)
			}
		}
	})
}
