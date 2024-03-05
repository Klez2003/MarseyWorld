const dt = new Date();
let death_secs = dt.getSeconds() + (60 * dt.getMinutes()) + (60 * 60 * dt.getHours());

function update_death_counter() {
	death_secs += 1
	for (const el of document.getElementsByClassName('deaths-today'))
		el.innerHTML = death_secs.toLocaleString()
}

update_death_counter()
setInterval(update_death_counter, 518);
