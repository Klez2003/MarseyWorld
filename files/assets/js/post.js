function highlight_unread(localstoragevar) {
	const comments = JSON.parse(localStorage.getItem(localstoragevar)) || {}

	lastCount = comments[pid]
	if (lastCount)
	{
		const comms = document.getElementById("comms").value.slice(0, -1).split(',')
		for (let c of comms) {
			c = c.split(':')
			if (c[1]*1000 > lastCount.t) {
				try {document.getElementById(`comment-${c[0]}-only`).classList.add('unread')}
				catch(e) {}
			}
		}
	}
}

highlight_unread("comment-counts")

if (!location.href.includes("#context")) {
	localStorage.setItem("old-comment-counts", localStorage.getItem("comment-counts"))

	const comments = JSON.parse(localStorage.getItem("comment-counts")) || {}
	const newTotal = pcc || ((comments[pid] || {c: 0}).c + 1)
	comments[pid] = {c: newTotal, t: Date.now()}
	localStorage.setItem("comment-counts", JSON.stringify(comments))
}

const fake_textarea = document.querySelector('[data-href]')
if (fake_textarea) {
	fake_textarea.addEventListener('click', () => {
		location.href = fake_textarea.dataset.href;
	});
}


//POST NAVIGATION

const post_ids = localStorage.getItem("post_ids").split(', ');
const current_index = post_ids.indexOf(`'${location.href}'`)
if (current_index > -1) {
	const id_after = post_ids[current_index+1]
	const id_before = post_ids[current_index-1]

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
