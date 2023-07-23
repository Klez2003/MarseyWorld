function deltaRgb (rgb1, rgb2) {
	const [ r1, g1, b1 ] = rgb1,
		[ r2, g2, b2 ] = rgb2,
		drp2 = Math.pow(r1 - r2, 2),
		dgp2 = Math.pow(g1 - g2, 2),
		dbp2 = Math.pow(b1 - b2, 2),
		t = (r1 + r2) / 2

	return Math.sqrt(2 * drp2 + 4 * dgp2 + 3 * dbp2 + t * (drp2 - dbp2) / 256)
}

function toRGBArray(rgbStr) {
	console.log(rgbStr)
	return rgbStr.match(/\d+/g).map(Number);
}

const background_color = toRGBArray(getComputedStyle(document.documentElement).getPropertyValue('--background'));

for (const line of document.getElementsByClassName('comment-collapse-desktop')) {
	const line_color = toRGBArray(line.style.borderColor)
	if (deltaRgb(line_color, background_color) < 100) {
		const R = Math.abs(background_color[0] - 255)
		const G = Math.abs(background_color[1] - 255)
		const B = Math.abs(background_color[2] - 255)
		line.style.borderColor = `rgb(${R}, ${G}, ${B})`
	}
}
