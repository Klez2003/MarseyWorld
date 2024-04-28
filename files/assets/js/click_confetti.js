document.addEventListener('click', function(e) {
	
	if (e.target instanceof HTMLTextAreaElement || e.target instanceof HTMLInputElement)
		return;

	function random(max){
		return Math.random() * (max - 0) + 0;
	}

	const c = document.createElement('div');
	c.classList.add('click-confetti')
	c.style.top = e.clientY + 'px';
	c.style.left = e.clientX + 'px';
	for (let i = 0; i < 100; i++) {		
		const e = document.createElement("i");
		e.style.transform = 'translate3d(' + (random(500) - 250) + 'px, ' + (random(200) - 150) + 'px, 0) rotate(' + random(360) + 'deg)'
		e.style.background = `hsla(${random(360)},100%,50%,1)`
		c.appendChild(e);
	}
	document.body.appendChild(c);
	setTimeout(function() {
		document.body.removeChild(c)
	}, 700)
})
