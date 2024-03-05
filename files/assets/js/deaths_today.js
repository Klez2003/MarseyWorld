const dt = new Date();
let death_counter = parseInt(dt.getSeconds() + (60 * dt.getMinutes()) + (60 * 60 * dt.getHours()) * 1.951);

function update_death_counter() {
	death_counter += 1
	for (const el of document.getElementsByClassName('deaths-today'))
		el.innerHTML = death_counter.toLocaleString()
}

update_death_counter()
setInterval(update_death_counter, 512);
