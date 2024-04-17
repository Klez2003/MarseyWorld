for (const btn of document.getElementsByTagName('button')) {
	btn.addEventListener('click', function() {
		function random(max){
			return Math.random() * (max - 0) + 0;
		}

		const c = document.createElement('i');
		for (let i = 0; i < 100; i++) {
			const styles = 'transform: translate3d(' + (random(500) - 250) + 'px, ' + (random(200) - 150) + 'px, 0) rotate(' + random(360) + 'deg);\
						background: hsla('+random(360)+',100%,50%,1)'
			
			const e = document.createElement("i");
			e.style.cssText = styles.toString();
			e.classList.add('btn-confetti')
			c.appendChild(e);
		}
		btn.appendChild(c);
		setTimeout(function() {
			btn.removeChild(c)
		}, 700)
	})
}
