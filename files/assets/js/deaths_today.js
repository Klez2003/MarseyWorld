const dt = new Date();
let secs = dt.getSeconds() + (60 * dt.getMinutes()) + (60 * 60 * dt.getHours());

function update_death_counter() {
	secs += 1
	for (const el of document.getElementsByClassName('deaths-today'))
		el.innerHTML = secs.toLocaleString()
}

update_death_counter()
setInterval(update_death_counter, 518);
