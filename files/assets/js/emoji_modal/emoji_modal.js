let emojiEngineState = "inactive";

// DOM stuff
const classesSelectorDOM = document.getElementById("emoji-modal-tabs");
const emojiButtonTemplateDOM = document.getElementById("emoji-button-template");
const emojiResultsDOM = document.getElementById("tab-content");

const emojiSelectSuffixDOMs = document.getElementsByClassName("emoji-suffix");
const emojiSelectPostfixDOMs= document.getElementsByClassName("emoji-postfix");

const emojiNotFoundDOM = document.getElementById("no-emojis-found");
const emojiWorkingDOM = document.getElementById("emojis-work");

const emojiSearchBarDOM = document.getElementById('emoji_search');

let emojiInputTargetDOM = undefined;

// Emojis usage stats. I don't really like this format but I'll keep it for backward comp.
const favorite_emojis = JSON.parse(localStorage.getItem("favorite_emojis")) || {};

/** Associative array of all the emojis' DOM */
let emojiDOMs = {};

const EMOIJ_SEARCH_ENGINE_MIN_INTERVAL = 350;
let emojiSearcher = {
	working: false,
	queries: [],

	addQuery: function(query)
	{
		this.queries.push(query);
		if (!this.working)
			this.work();
	},

	work: async function work() {
		this.working = true;

		while(this.queries.length > 0)
		{
			const startTime = Date.now();

			// Get last input
			const query = this.queries[this.queries.length - 1].toLowerCase();
			this.queries = [];

			// To improve perf we avoid showing all emojis at the same time.
			if (query === "")
			{
				await classesSelectorDOM.children[0].children[0].click();
				classesSelectorDOM.children[0].children[0].classList.add("active");
				continue;
			}

			// Search
			const resultSet = emojisSearchDictionary.completeSearch(query);

			// update stuff
			for(const [emojiName, emojiDOM] of Object.entries(emojiDOMs))
				emojiDOM.hidden = !resultSet.has(emojiName);

			emojiNotFoundDOM.hidden = resultSet.size !== 0;

			let sleepTime = EMOIJ_SEARCH_ENGINE_MIN_INTERVAL - (Date.now() - startTime);
			if (sleepTime > 0)
				await new Promise(r => setTimeout(r, sleepTime));
		}

		this.working = false;
	}
};

// get public emojis list
function fetchEmojis() {
	const headers = new Headers({xhr: "xhr"})
	const emoji_params = document.getElementById('emoji_params').value
	return fetch(`/emojis.csv${emoji_params}`, {
		headers,
	})
		.then(res => res.json())
		.then(emojis => {
			if (!(emojis instanceof Array ))
				throw new TypeError("[EMOJI DIALOG] rDrama's server should have sent a JSON-coded Array!");

			let classes = ["Marsey", "Platy", "Wolf", "Donkey Kong", "Tay", "Capy", "Carp", "Marsey Flags", "Marsey Alphabet", "Classic", "Rage", "Wojak", "Misc"]

			const bussyDOM = document.createElement("div");

			for(let i = 0; i < emojis.length; i++)
			{
				const emoji = emojis[i];

				// Create emoji DOM
				const emojiDOM = document.importNode(emojiButtonTemplateDOM.content, true).children[0];

				emojiDOM.title = emoji.name
				emojiDOM.title += "\nauthor\t" + emoji.author_username
				if (emoji.count !== undefined)
					emojiDOM.title += "\nused\t" + emoji.count;
				emojiDOM.dataset.className = emoji.kind;
				emojiDOM.dataset.emojiName = emoji.name;
				emojiDOM.onclick = emojiAddToInput;
				emojiDOM.hidden = true;

				const emojiIMGDOM = emojiDOM.children[0];
				emojiIMGDOM.src = `${SITE_FULL_IMAGES}/e/${emoji.name}.webp`
				emojiIMGDOM.alt = emoji.name;
				/** Disableing lazy loading seems to reduce cpu usage somehow (?)
				 * idk it is difficult to benchmark */
				emojiIMGDOM.loading = "lazy";

				// Save reference
				emojiDOMs[emoji.name] = emojiDOM;

				// Add to the document!
				bussyDOM.appendChild(emojiDOM);
			}

			// Create header
			for(let className of classes)
			{
				let classSelectorDOM = document.createElement("li");
				classSelectorDOM.classList.add("nav-item");

				let classSelectorLinkDOM = document.createElement("button");
				classSelectorLinkDOM.type = "button";
				classSelectorLinkDOM.classList.add("nav-link", "emojitab");
				classSelectorLinkDOM.dataset.bsToggle = "tab";
				classSelectorLinkDOM.dataset.className = className;
				classSelectorLinkDOM.textContent = className;
				classSelectorLinkDOM.addEventListener('click', switchEmojiTab);

				classSelectorDOM.appendChild(classSelectorLinkDOM);
				classesSelectorDOM.appendChild(classSelectorDOM);
			}

			// Show favorite for start.
			classesSelectorDOM.children[0].children[0].click();

			// Send it to the render machine!
			emojiResultsDOM.appendChild(bussyDOM);

			emojiResultsDOM.hidden = false;
			emojiWorkingDOM.hidden = true;
			emojiSearchBarDOM.disabled = false;

			emojiEngineState = "ready";
		})
}

/**
*
* @param {Event} e
*/
function switchEmojiTab(e)
{
	const className = e.currentTarget.dataset.className;

	emojiSearchBarDOM.value = "";
	focusSearchBar(emojiSearchBarDOM);
	emojiNotFoundDOM.hidden = true;

	// Special case: favorites
	if (className === "favorite")
	{
		for(const emojiDOM of Object.values(emojiDOMs))
			emojiDOM.hidden = true;

		const favs = Object.keys(Object.fromEntries(
			Object.entries(favorite_emojis).sort(([,a],[,b]) => b-a)
		)).slice(0, 25);

		for (const emoji of favs)
			if (emojiDOMs[emoji] instanceof HTMLElement)
				emojiDOMs[emoji].hidden = false;

		return;
	}

	for(const emojiDOM of Object.values(emojiDOMs))
		emojiDOM.hidden = emojiDOM.dataset.className !== className;

	document.getElementById('emoji-container').scrollTop = 0;
}

for (const emojitab of document.getElementsByClassName('emojitab')) {
	emojitab.addEventListener('click', (e)=>{switchEmojiTab(e)})
}

async function start_search() {
	emojiSearcher.addQuery(emojiSearchBarDOM.value.trim());

	// Remove any selected tab, now it is meaningless
	for(let i = 0; i < classesSelectorDOM.children.length; i++)
		classesSelectorDOM.children[i].children[0].classList.remove("active");
}

/**
* Add the selected emoji to the targeted text area
* @param {Event} event
*/
function emojiAddToInput(event)
{
	// This should not happen if used properly but whatever
	if (!(emojiInputTargetDOM instanceof HTMLTextAreaElement) && !(emojiInputTargetDOM instanceof HTMLInputElement))
		return;

	let strToInsert = event.currentTarget.dataset.emojiName;

	for(let i = 0; i < emojiSelectPostfixDOMs.length; i++)
		if (emojiSelectPostfixDOMs[i].checked)
			strToInsert = strToInsert + emojiSelectPostfixDOMs[i].value;

	for(let i = 0; i < emojiSelectSuffixDOMs.length; i++)
		if (emojiSelectSuffixDOMs[i].checked)
			strToInsert = emojiSelectSuffixDOMs[i].value + strToInsert;

	strToInsert = ":" + strToInsert + ":"
	insertText(emojiInputTargetDOM, strToInsert)
	insertedAnEmoji = true

	// kick-start the preview
	emojiInputTargetDOM.dispatchEvent(new Event('input'));

	// Update favs. from old code
	if (favorite_emojis[event.currentTarget.dataset.emojiName])
		favorite_emojis[event.currentTarget.dataset.emojiName] += 1;
	else
		favorite_emojis[event.currentTarget.dataset.emojiName] = 1;
	localStorage.setItem("favorite_emojis", JSON.stringify(favorite_emojis));
}

const emojiModal = document.getElementById('emojiModal')
let insertedAnEmoji

function openEmojiModal(t, inputTargetIDName)
{
	selecting = false;
	insertedAnEmoji = false;

	if (inputTargetIDName) {
		emojiInputTargetDOM = document.getElementById(inputTargetIDName);
		emojiModal.addEventListener('hide.bs.modal', () => {
			if (insertedAnEmoji) {
				setTimeout(() => {
					emojiInputTargetDOM.focus();
				}, 50);
			}
		}, {once : true});	
	}

	if (t && t.dataset.previousModal) {
		emojiModal.addEventListener('hide.bs.modal', () => {
			bootstrap.Modal.getOrCreateInstance(document.getElementById(t.dataset.previousModal)).show()
		}, {once : true});	
	}

	switch (emojiEngineState) {
		case "inactive":
			emojiEngineState = "loading"
			if (searchDictionaryState == "inactive")
				makeEmojisSearchDictionary();
			return fetchEmojis();
		case "loading":
			// this works because once the fetch completes, the first keystroke callback will fire and use the current value
			return Promise.reject();
		case "ready":
			return Promise.resolve();
		default:
			throw Error("Unknown emoji engine state");
	}
}

document.getElementById('emojiModal').addEventListener('shown.bs.modal', function () {
	focusSearchBar(emojiSearchBarDOM);
	setTimeout(() => {
		focusSearchBar(emojiSearchBarDOM);
	}, 200);
	setTimeout(() => {
		focusSearchBar(emojiSearchBarDOM);
	}, 1000);
});
