const autoresizable = document.querySelector('#other-embed.autoresizable')
if (autoresizable) {
	addEventListener('message', function (e) {
		if (e.origin == "https://www.teamblind.com" && e.data.height)
			autoresizable.height = e.data.height;
		if (e.origin == "https://www.instagram.com") {
			const height = JSON.parse(e.data).details.height
			if (height)
				autoresizable.height = height;
		}
		if (e.origin.endsWith('.substack.com') && e.data.iframeHeight)
			autoresizable.height = e.data.iframeHeight;
	});
}

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