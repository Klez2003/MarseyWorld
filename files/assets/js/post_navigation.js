const post_permalinks = sessionStorage.getItem("post_permalinks").split(', ');
const current_index = post_permalinks.indexOf(`'${location.href}'`)
if (current_index > -1) {
	const id_after = post_permalinks[current_index+1]

	if (id_after) {
		document.getElementById('post_navigation').classList.remove('d-none')
		document.getElementById('post_after').href = id_after.slice(1, -1)
	}
}
