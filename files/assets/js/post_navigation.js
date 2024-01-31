const post_permalinks = sessionStorage.getItem("post_permalinks").split(', ');
const current_index = post_permalinks.indexOf(`'${location.href}'`)
if (current_index > -1) {
	const permalink_after = post_permalinks[current_index+1]

	if (permalink_after) {
		for (const btn of document.getElementsByClassName('post_navigation')) {
			btn.classList.remove('d-none')
			btn.href = permalink_after.slice(1, -1)
		}
	}
}
