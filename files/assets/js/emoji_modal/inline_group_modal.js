let groupSearchDictionaryState = "inactive";

let globalGroups = [];

const groupsSearchDictionary = {
	dict: [],

	updateTag: function(tag, groupName) {
		if (tag === undefined || groupName === undefined)
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
			this.dict[target].emojiNames.push(groupName);
		else
			this.dict.splice(target, 0, new EmojisDictNode(tag, groupName));
	},

	/**
	 * We also check for substrings! (sigh)
	 * @param {String} tag
	 * @returns {Set}
	 */
	completeSearch: function(query) {
		query = query.toLowerCase()
		const result = new Set();

		for (let i = 0; i < this.dict.length; i++)
			if (this.dict[i].tag.includes(query))
				for (let j = 0; j < this.dict[i].emojiNames.length; j++)
					result.add(this.dict[i].emojiNames[j])

		return result;
	}
};

function makeGroupsSearchDictionary() {
	// get public groups list
	const headers = new Headers({xhr: "xhr"})
	const group_params = document.getElementById('group_params').value
	return fetch(`/groups.csv${group_params}`, {
		headers,
	})
		.then(res => res.json())
		.then(groups => {
			for (let i = 0; i < groups.length; i++)
			{
				const group = groups[i];
				groupsSearchDictionary.updateTag(group, group);
				globalGroups.push(group);
			}

			groupSearchDictionaryState = "ready";
		})
}

function curr_word_is_group()
{
	return current_word && current_word.charAt(0) == "!" &&
		current_word.charAt(current_word.length-1) != "!";
}

function openGroupSpeedModal()
{
	switch (groupSearchDictionaryState) {
		case "inactive":
			groupSearchDictionaryState = "loading"
			return makeGroupsSearchDictionary();
		case "loading":
			// this works because once the fetch completes, the first keystroke callback will fire and use the current value
			return Promise.reject();
		case "ready":
			return Promise.resolve();
		default:
			throw Error("Unknown group engine state");
	}
}

function populate_inline_group_modal(results, textbox)
{
	selecting = true;

	if (!results || results.size === 0)
	{
		inline_carot_modal.style.display = "none";
		return -1;
	}

	group_index = 0;
	inline_carot_modal.scrollTop = 0;
	inline_carot_modal.innerHTML = "";
	const MAXXX = 50;
	// Not sure why the results is a Set... but oh well
	let i = 0;
	for (let name of results)
	{
		if (i++ > MAXXX) return i;
		let group_option = document.createElement("div");
		group_option.className = "inline-modal-option group-option " + (i === 1 ? "selected" : "");
		group_option.tabIndex = 0;
		let group_option_text = document.createElement("span");

		group_option_text.textContent = name;

		group_option.addEventListener('click', () => {
			close_inline_emoji_modal()
			textbox.value = textbox.value.replace(new RegExp(current_word+"(?=\\s|$)", "gi"), `!${name}`)
			textbox.focus()
			if (typeof markdown === "function" && textbox.dataset.preview) {
				markdown(textbox)
			}
		});
		// Pack
		group_option.appendChild(group_option_text);
		inline_carot_modal.appendChild(group_option);
	}
	if (i === 0) inline_carot_modal.style.display = "none";
	else inline_carot_modal.style.display = "initial";
	return i;
}
