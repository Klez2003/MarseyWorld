const thunder1 = document.getElementById("thunder1")
const thunder2 = document.getElementById("thunder2")

const div = document.getElementById("haunted-effect")

const stylesheet_haunted = document.createElement("link")
stylesheet_haunted.setAttribute("rel", "stylesheet")
stylesheet_haunted.setAttribute("href", "/assets/events/homoween/css/haunted2.css?x=1")
stylesheet_haunted.disabled = true
document.head.appendChild(stylesheet_haunted)

window.onload = function(){
	if (thunder1)
		thunder2.volume = 0.5
	lightningStrike("normal")
}

setInterval(function(){
	if(Math.floor(Math.random()*3) > 1){
		lightningStrike("haunted")
	} else {
		lightningStrike("normal")
	}
}, 14000)

function lightningStrike(strike) {
	div.style.animation = "haunted 20s"

	if(strike == "haunted"){
		stylesheet_haunted.disabled = false
		if (thunder1)
			thunder2.play()
		setTimeout(function(){
			stylesheet_haunted.disabled = true
		}, 700)
	}

	if (thunder1)
		thunder1.play()
	setTimeout(function(){
		div.style.animation = "none"
	}, 1000)
}
