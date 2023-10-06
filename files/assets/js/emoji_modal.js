/*
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.

Copyright (C) 2022 Dr Steven Transmisia, anti-evil engineer,
				2022 Nekobit, king autist
*/

// Status
/**
 * inactive - user has not tried using an emoji
 * loading - user has tried to use an emoji, and the engine is initializing itself
 * ready - engine can handle all emoji usage
 * @type {"inactive"|"loading"|"ready"}
 */
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

let globalEmojis;

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

// tags dictionary. KEEP IT SORT
class EmoijsDictNode
{
	constructor(tag, name) {
		this.tag = tag;
		this.emojiNames = [name];
	}
}
const emojisSearchDictionary = {
	dict: [],

	updateTag: function(tag, emojiName) {
		if (tag === undefined || emojiName === undefined)
			return;

		let low = 0;
		let high = this.dict.length;

		while (low < high) {
			let mid = (low + high) >>> 1;
			if (this.dict[mid].tag < tag)
				low = mid + 1;
			else
				high = mid;
		}

		let target = low;
		if (this.dict[target] !== undefined && this.dict[target].tag === tag)
			this.dict[target].emojiNames.push(emojiName);
		else
			this.dict.splice(target ,0,new EmoijsDictNode(tag, emojiName));
	},

	/**
	 * We also check for substrings! (sigh)
	 * @param {String} tag
	 * @returns {Set}
	 */
	completeSearch: function(query) {
		query = query.toLowerCase()
		const result = new Set();

		for(let i = 0; i < this.dict.length; i++)
			if (this.dict[i].tag.startsWith('@'))
			{
				if (this.dict[i].tag == query)
					for(let j = 0; j < this.dict[i].emojiNames.length; j++)
						result.add(this.dict[i].emojiNames[j])
			}
			else if(this.dict[i].tag.includes(query))
				for(let j = 0; j < this.dict[i].emojiNames.length; j++)
					result.add(this.dict[i].emojiNames[j])

		return result;
	}
};

// get public emojis list
function fetchEmojis() {
	const headers = new Headers({xhr: "xhr"})
	return fetch("/emojis_json", {
		headers,
	})
		.then(res => res.json())
		.then(emojis => {
			if (! (emojis instanceof Array ))
				throw new TypeError("[EMOJI DIALOG] rDrama's server should have sent a JSON-coded Array!");

			globalEmojis = emojis.map(({name, author, count}) => ({name, author, count}));

			let classes = ["Marsey", "Platy", "Wolf", "Donkey Kong", "Tay", "Capy", "Carp", "Marsey Flags", "Marsey Alphabet", "Classic", "Rage", "Wojak", "Misc"]

			const bussyDOM = document.createElement("div");

			for(let i = 0; i < emojis.length; i++)
			{
				const emoji = emojis[i];

				emojisSearchDictionary.updateTag(emoji.name, emoji.name);

				if (emoji.author_username !== undefined && emoji.author_username !== null)
					emojisSearchDictionary.updateTag(`@${emoji.author_username.toLowerCase()}`, emoji.name);

				if (emoji.author_original_username !== undefined && emoji.author_original_username !== null)
					emojisSearchDictionary.updateTag(`@${emoji.author_original_username.toLowerCase()}`, emoji.name);

				if (emoji.author_prelock_username !== undefined && emoji.author_prelock_username !== null)
					emojisSearchDictionary.updateTag(`@${emoji.author_prelock_username.toLowerCase()}`, emoji.name);

				if (emoji.tags instanceof Array)
					for(let i = 0; i < emoji.tags.length; i++)
						emojisSearchDictionary.updateTag(emoji.tags[i], emoji.name);

				// Create emoji DOM
				const emojiDOM = document.importNode(emojiButtonTemplateDOM.content, true).children[0];

				emojiDOM.title = emoji.name
				if (emoji.author_username !== undefined && emoji.author_username !== null)
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

	// kick-start the preview
	emojiInputTargetDOM.dispatchEvent(new Event('input'));

	// Update favs. from old code
	if (favorite_emojis[event.currentTarget.dataset.emojiName])
		favorite_emojis[event.currentTarget.dataset.emojiName] += 1;
	else
		favorite_emojis[event.currentTarget.dataset.emojiName] = 1;
	localStorage.setItem("favorite_emojis", JSON.stringify(favorite_emojis));
}

let emoji_typing_state = false;

function update_ghost_div_textarea(text)
{
	let ghostdiv

	if (location.pathname == '/chat') 
		ghostdiv = document.getElementById("ghostdiv-chat");
	else
		ghostdiv = text.parentNode.getElementsByClassName("ghostdiv")[0];

	if (!ghostdiv) return;

	ghostdiv.textContent = text.value.substring(0, text.selectionStart);

	ghostdiv.insertAdjacentHTML('beforeend', "<span></span>");

	// Now lets get coordinates

	ghostdiv.style.display = "block";
	let end = ghostdiv.querySelector("span");
	const carot_coords = end.getBoundingClientRect();
	const ghostdiv_coords = ghostdiv.getBoundingClientRect();
	ghostdiv.style.display = "none";
	return { pos: text.selectionStart, x: carot_coords.x, y: carot_coords.y - ghostdiv_coords.y };
}

// Used for anything where a user is typing, specifically for the emoji modal
// Just leave it global, I don't care
let speed_carot_modal = document.createElement("div");
speed_carot_modal.id = "speed-carot-modal";
speed_carot_modal.style.position = "absolute";
speed_carot_modal.style.left = "0px";
speed_carot_modal.style.top = "0px";
speed_carot_modal.style.display = "none";
document.body.appendChild(speed_carot_modal);

let e

let current_word = "";
let selecting;
let emoji_index = 0;

function curr_word_is_emoji()
{
	return current_word && current_word.charAt(0) == ":" &&
		current_word.charAt(current_word.length-1) != ":";
}

function close_inline_speed_emoji_modal() {
	selecting = false;
	speed_carot_modal.style.display = "none";
}

function populate_speed_emoji_modal(results, textbox)
{
	selecting = true;

	if (!results || results.size === 0)
	{
		speed_carot_modal.style.display = "none";
		return -1;
	}

	emoji_index = 0;
	speed_carot_modal.scrollTop = 0;
	speed_carot_modal.innerHTML = "";
	const MAXXX = 50;
	// Not sure why the results is a Set... but oh well
	let i = 0;
	for (let emoji of results)
	{
		let name = emoji.name

		if (i++ > MAXXX) return i;
		let emoji_option = document.createElement("div");
		emoji_option.className = "speed-modal-option emoji-option " + (i === 1 ? "selected" : "");
		emoji_option.tabIndex = 0;
		let emoji_option_img = document.createElement("img");
		emoji_option_img.className = "speed-modal-image emoji-option-image";
		// This is a bit
		emoji_option_img.src = `${SITE_FULL_IMAGES}/e/${name}.webp`
		let emoji_option_text = document.createElement("span");

		emoji_option_text.title = name;

		if (emoji.author_username !== undefined && emoji.author_username !== null)
			emoji_option_text.title += "\nauthor\t" + emoji.author_username

		if (emoji.count !== undefined)
			emoji_option_text.title += "\nused\t" + emoji.count;

		emoji_option_text.textContent = name;

		if (current_word.includes("#")) name = `#${name}`
		if (current_word.includes("!")) name = `!${name}`

		emoji_option.addEventListener('click', () => {
			close_inline_speed_emoji_modal()
			textbox.value = textbox.value.replace(new RegExp(current_word+"(?=\\s|$)", "gi"), `:${name}: `)
			textbox.focus()
			if (typeof markdown === "function" && textbox.dataset.preview) {
				markdown(textbox)
			}
		});
		// Pack
		emoji_option.appendChild(emoji_option_img);
		emoji_option.appendChild(emoji_option_text);
		speed_carot_modal.appendChild(emoji_option);
	}
	if (i === 0) speed_carot_modal.style.display = "none";
	else speed_carot_modal.style.display = "initial";
	return i;
}

function update_speed_emoji_modal(event)
{
	const box_coords = update_ghost_div_textarea(event.target);

	box_coords.x = Math.min(box_coords.x, screen_width - 150)

	let text = event.target.value;

	// Unused, but left incase anyone wants to use this more efficient method for emojos
	switch (event.data)
	{
		case ':':
		emoji_typing_state = true;
		break;
		case ' ':
		emoji_typing_state = false;
		break;
		default:
		break;
	}

	// Get current word at string, such as ":marse" or "word"
	let coords = text.indexOf(' ',box_coords.pos);
	current_word = /:[!#a-zA-Z0-9_]+(?=\n|$)/.exec(text.slice(0, coords === -1 ? text.length : coords));
	if (current_word) current_word = current_word[0].toLowerCase();

	/* We could also check emoji_typing_state here, which is less accurate but more efficient. I've
		* kept it unless someone wants to provide an option to toggle it for performance */
	if (curr_word_is_emoji() && current_word != ":")
	{
		loadEmojis().then( () => {
			let modal_pos = event.target.getBoundingClientRect();
			modal_pos.x += window.scrollX;
			modal_pos.y += window.scrollY;

			speed_carot_modal.style.display = "initial";
			speed_carot_modal.style.left = box_coords.x - 30 + "px";
			speed_carot_modal.style.top = modal_pos.y + box_coords.y + 14 + "px";

			// Do the search (and do something with it)
			const resultSet = emojisSearchDictionary.completeSearch(current_word.substring(1).replace(/[#!]/g, ""));

			const found = globalEmojis.filter(i => resultSet.has(i.name));

			populate_speed_emoji_modal(found, event.target);
		});
	}
	else {
		speed_carot_modal.style.display = "none";
	}
}

function speed_carot_navigate(event)
{
	if (!selecting) return;

	let select_items = speed_carot_modal.querySelectorAll(".speed-modal-option");
	if (!select_items || !curr_word_is_emoji()) return;

	const modal_keybinds = {
		// go up one, wrapping around to the bottom if pressed at the top
		ArrowUp: () => emoji_index = ((emoji_index - 1) + select_items.length) % select_items.length,
		// go down one, wrapping around to the top if pressed at the bottom
		ArrowDown: () => emoji_index = ((emoji_index + 1) + select_items.length) % select_items.length,
		// select the emoji
		Enter: () => select_items[emoji_index].click(),
	}
	if (event.key in modal_keybinds)
	{
		select_items[emoji_index].classList.remove("selected");
		modal_keybinds[event.key]();
		select_items[emoji_index].classList.add("selected");
		select_items[emoji_index].scrollIntoView({inline: "end", block: "nearest"});
		event.preventDefault();
	}
}

function insertGhostDivs(element) {
	let forms = element.querySelectorAll("textarea, .allow-emojis");
	forms.forEach(i => {
		let ghostdiv
		if (i.id == 'input-text-chat') {
			ghostdiv = document.getElementsByClassName("ghostdiv")[0];
		}
		else {
			ghostdiv = document.createElement("div");
			ghostdiv.className = "ghostdiv";
			ghostdiv.style.display = "none";
			i.after(ghostdiv);
		}
		i.addEventListener('input', update_speed_emoji_modal, false);
		i.addEventListener('keydown', speed_carot_navigate, false);
	});
}

const emojiModal = document.getElementById('emojiModal')

function loadEmojis(t, inputTargetIDName)
{
	selecting = false;
	speed_carot_modal.style.display = "none";

	emojiInputTargetDOM = document.getElementById(inputTargetIDName);

	if (t.dataset.previousModal) {
		emojiModal.addEventListener('hide.bs.modal', () => {
			bootstrap.Modal.getOrCreateInstance(document.getElementById(t.dataset.previousModal)).show()
		}, {once : true});	
	}

	emojiModal.addEventListener('hide.bs.modal', () => {
		setTimeout(() => {
			emojiInputTargetDOM.focus();
		}, 200);
	}, {once : true});	

	switch (emojiEngineState) {
		case "inactive":
			emojiEngineState = "loading"
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
