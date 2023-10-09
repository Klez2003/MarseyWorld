const socket = io()

socket.on('insert_reply', function(data) {
	const replies = document.getElementById(`replies-of-c_${data[0]}`)
	if (replies) {
		replies.insertAdjacentHTML('beforeend', data[1]);

		notifs = notifs + 1;
		if (notifs == 1) {
			flash();
		}
	}
})
