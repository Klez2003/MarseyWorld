const dt = new Date();
const secs = dt.getSeconds() + (60 * dt.getMinutes()) + (60 * 60 * dt.getHours());
for (const el of document.getElementsByClassName('deaths-today'))
	el.innerHTML = secs;

function update_death_counter() {
	for (const el of document.getElementsByClassName('deaths-today'))
		el.innerHTML = parseInt(el.innerHTML) + 1;
}

setInterval(update_death_counter, 518);
