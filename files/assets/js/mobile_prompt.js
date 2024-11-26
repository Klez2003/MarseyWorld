if (!is_pwa) {
	if (innerWidth <= 737) {
		const tt = bootstrap.Tooltip.getOrCreateInstance(document.getElementById('mobile-prompt'))
		tt.show()
		document.getElementsByClassName('tooltip')[0].addEventListener('click', function(e) {
			tt.hide()
			const xhr = new XMLHttpRequest();
			xhr.open("POST", '/dismiss_mobile_tip');
			xhr.setRequestHeader('xhr', 'xhr');
			xhr.send();
			if (!e.target.classList.contains('dismiss-beg'))
				location.href = "/app"
		})
	}
}
