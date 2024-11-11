const icon = document.querySelector("link[rel~='icon']")
const page_title = document.getElementsByTagName('title')[0].innerHTML

let notifs = 0
let focused = true
let alert = true;

addEventListener('blur', function() {
	focused = false
})
addEventListener('focus', function() {
	focused = true
})

function flash() {
	let title = document.getElementsByTagName('title')[0]
	if (notifs >= 1 && !focused) {
		title.innerHTML = `[+${notifs}] ${page_title}`
		if (alert) {
			icon.href = `${SITE_FULL_IMAGES}/i/${SITE_NAME}/alert.ico?x=3010`
			alert = false
		}
		else {
			icon.href = `${SITE_FULL_IMAGES}/i/${SITE_NAME}/icon.webp?x=14`
			alert = true
		}
		setTimeout(flash, 500)
	}
	else {
		icon.href = `${SITE_FULL_IMAGES}/i/${SITE_NAME}/icon.webp?x=14`
		notifs = 0
		title.innerHTML = page_title
	}
}
