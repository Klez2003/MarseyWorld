const socket = io()

socket.on('insert_reply', function(data) {
	const replies = document.getElementById(`replies-of-c_${data[0]}`)
	if (replies) {
		const html = data[1].replace(/data-src/g, 'src').replace(/data-nonce=".*?"/g, `data-nonce="${nonce}"`);

		replies.insertAdjacentHTML('beforeend', html);

		register_new_elements(replies.lastElementChild);
		bs_trigger(replies.lastElementChild);

		notifs = notifs + 1;
		if (notifs == 1) {
			flash();
		}
	}
})
