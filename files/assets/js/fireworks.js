function execute_fireworks(firework) {
	firework.firstElementChild.src = "/i/firework-trail.webp"

	const xpos = Math.floor(Math.random() * 80) + 5
	let ypos = 95
	firework.style.top=ypos+"%"
	firework.style.left=xpos+"%"

	firework.style.display="inline-block"
	const hue = Math.floor(Math.random()*360)+1
	firework.style.filter="hue-rotate("+hue+"deg)"

	let id = null
	const height = Math.floor(Math.random()*60)+15
	clearInterval(id);
	id = setInterval(frame, 20);

	const vnum = Math.floor(Math.random()*1000)

	function frame() {
		if (ypos <= height) {
			clearInterval(id);
			firework.firstElementChild.src = "/i/firework-explosion.webp?v="+vnum
		} else {
			ypos--;
			firework.style.top=ypos+"%"
		}
	}
}

let counter = 0

for (let firework of document.getElementsByClassName("firework")){
	const timeout = 2000 * counter
	counter++
	setTimeout(() => {
		execute_fireworks(firework)
		setInterval(execute_fireworks, 5000, firework)
	}, timeout)
}
