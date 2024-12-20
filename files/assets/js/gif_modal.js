const gifSearchBar = document.getElementById('gifSearch')
const noGIFs = document.getElementById('no-gifs-found');
const container = document.getElementById('GIFs');

let commentFormID;

function insertGif (url) {
	const commentBox = document.getElementById(commentFormID);
	insertText(commentBox, url)
	markdown(commentBox)
}

const gifModal = document.getElementById('gifModal')

gifModal.addEventListener('shown.bs.modal', function() {
	focusSearchBar(gifSearchBar);
	setTimeout(() => {
		focusSearchBar(gifSearchBar);
	}, 200);
	setTimeout(() => {
		focusSearchBar(gifSearchBar);
	}, 1000);
});

async function show_gif_categories(t, form) {
	if (form) commentFormID = form;

	gifSearchBar.value = null;
	noGIFs.classList.add("d-none");

	container.innerHTML = `
	<div class="card">
		<div class="gif-cat-overlay"><div>Trending</div></div>
		<img loading="lazy" src="https://media.tenor.com/C84XvrdyLswAAAAx/spongebob-patrick-star.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Agree</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/wGhYz3FHaRJgk/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Laugh</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/O5NyCibf93upy/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Confused</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/3o7btPCcdNniyf0ArS/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Sad</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/ISOckXUybVfQ4/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Happy</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/XR9Dp54ZC4dji/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Awesome</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/3ohzdIuqJoo8QdKlnW/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Yes</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/J336VCs1JC42zGRhjH/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>No</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/1zSz5MVw4zKg0/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Love</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/4N1wOi78ZGzSB6H7vK/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Please</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/qUIm5wu6LAAog/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Scared</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/bEVKYB487Lqxy/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Angry</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/12Pb87uq0Vwq2c/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Awkward</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/unFLKoAV3TkXe/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Cringe</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/1jDvQyhGd3L2g/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>OMG</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/3o72F8t9TDi2xVnxOE/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Why</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/1M9fmo1WAFVK0/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Gross</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/pVAMI8QYM42n6/200w.webp">
	</div>
	<div class="card">
		<div class="gif-cat-overlay"><div>Meh</div></div>
		<img loading="lazy" src="https://media.giphy.com/media/xT77XTpyEzJ4OJO06c/200w.webp">
	</div>`

	const overlays = document.getElementsByClassName('gif-cat-overlay')
	for (const element of overlays) {
		let searchTerm = element.firstElementChild.innerHTML
		if (searchTerm == 'Trending')
			searchTerm = ''
		element.addEventListener('click', () => {searchGifs(searchTerm)});
	}

	if (t) {
		if (t.dataset.previousModal) {
			gifModal.addEventListener('hide.bs.modal', () => {
				bootstrap.Modal.getOrCreateInstance(document.getElementById(t.dataset.previousModal)).show()
			}, {once : true});	
		}
	}
}

document.getElementById('gifs-back-btn').addEventListener('click', () => show_gif_categories(null, null));

async function searchGifs(searchTerm) {
	gifSearchBar.value = searchTerm;
	noGIFs.classList.add("d-none");

	container.innerHTML = '';

	let response = await fetch("/tenor?searchTerm=" + searchTerm);
	let data = await response.json()
	data = data.results

	if (data) {
		for (const e of data) {
			const url = e.media_formats.webp.url
			const insert = `<img class="tenor" loading="lazy" data-bs-dismiss="modal" src="${url}"></div>`
			container.insertAdjacentHTML('beforeend', insert);
		}

		const tenor = document.getElementsByClassName('tenor')
		for (const element of tenor) {
			element.addEventListener('click', () => {insertGif (element.src)});
		}
	}
	else {
		noGIFs.classList.remove('d-none')
	}
}

gifSearchBar.addEventListener("keydown", function(e) {
	if (e.key === 'Enter')
		searchGifs(gifSearchBar.value)
})
