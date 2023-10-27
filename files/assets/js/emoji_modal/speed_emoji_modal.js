let emojiSpeedEngineState = "inactive";
let emoji_typing_state = false;
let globalEmojis;

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

	// Unused, but left incase anyone wants to use this more efficient method for emojis
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
	if (current_word && curr_word_is_emoji() && current_word != ":")
	{
		openSpeedModal().then( () => {
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

function openSpeedModal()
{
	switch (emojiSpeedEngineState) {
		case "inactive":
			emojiSpeedEngineState = "loading"
			return makeEmojisSearchDictionary();
		case "loading":
			// this works because once the fetch completes, the first keystroke callback will fire and use the current value
			return Promise.reject();
		case "ready":
			return Promise.resolve();
		default:
			throw Error("Unknown emoji engine state");
	}
}
