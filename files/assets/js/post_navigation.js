let post_permalinks = sessionStorage.getItem("post_permalinks")

if (post_permalinks) {
	post_permalinks = post_permalinks.split(', ');
	let current_index = post_permalinks.indexOf(`'${location.href}'`)
	if (current_index > -1) {
		let permalink_after = post_permalinks[current_index+1]

		if (permalink_after) {
			let pid = permalink_after.split('/').slice(-2, -1)[0]
			while (comments[pid]) {
				current_index += 1
				permalink_after = post_permalinks[current_index]
				if (permalink_after) {
					pid = permalink_after.split('/').slice(-2, -1)[0]
				}
				else {
					permalink_after = '+' + sessionStorage.getItem("next_page_url") + '+'
					break
				}
			}

			for (const btn of document.getElementsByClassName('post_navigation')) {
				btn.classList.remove('d-none')
				btn.href = permalink_after.slice(1, -1)
			}

			document.addEventListener('keydown', (e) => {
				if (
					!["TEXTAREA", "INPUT"].includes(document.activeElement.tagName) &&
					!(e.ctrlKey || e.metaKey || e.shiftKey || e.altKey) &&
					!expandImageModal.classList.contains('show')
				) {
					for (const video of document.getElementsByTagName('video'))
						if (!video.paused) return

					if (["ArrowRight", "d"].includes(e.key))
						location.href = permalink_after.slice(1, -1)
					if (["ArrowLeft", "a"].includes(e.key))
						history.back()
				}
			})
		}
		else {
			for (const btn of document.getElementsByClassName('post_navigation')) {
				btn.classList.remove('d-none')
				btn.href = sessionStorage.getItem("next_page_url")
			}
		}
	}
}
