const thunder1 = new Audio(`/assets/events/homoween/audio/haunted/thunder1.mp3`)
const thunder2 = new Audio(`/assets/events/homoween/audio/haunted/thunder2.mp3`)
const is_upsidedown = localStorage.getItem('setting_upsidedown')
const div = document.getElementById("haunted-effect")

const stylesheet_haunted = document.createElement("link")
stylesheet_haunted.setAttribute("rel", "stylesheet")
stylesheet_haunted.setAttribute("href", "/assets/events/homoween/css/haunted2.css?x=1")
stylesheet_haunted.disabled = true
document.head.appendChild(stylesheet_haunted)

window.onload = function(){
	thunder2.volume = 0.5
	lightningStrike("normal")
}

setInterval(function(){
	if(Math.floor(Math.random()*3) > 1){
		lightningStrike("haunted")
	} else {
		lightningStrike("normal")
	}
},14000)

function lightningStrike(strike) {
	if(is_upsidedown == 'true'){
		div.style.animation = "haunted-upsidedown 20s"
	} else {
		div.style.animation = "haunted 20s"
	}

	if(strike == "haunted"){
		stylesheet_haunted.disabled = false
		thunder2.play()
		setTimeout(function(){
			stylesheet_haunted.disabled = true
		},700)
	}

	thunder1.play()
	setTimeout(function(){
		div.style.animation = "none"
	},1000)
}
