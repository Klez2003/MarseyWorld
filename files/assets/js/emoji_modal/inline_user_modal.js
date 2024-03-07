let userSearchDictionaryState = "inactive";

let globalUsers = [];

const usersSearchDictionary = {
	dict: [],

	updateTag: function(tag, userName) {
		if (tag === undefined || userName === undefined)
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
			this.dict[target].emojiNames.push(userName);
		else
			this.dict.splice(target, 0, new EmojisDictNode(tag, userName));
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
			if (this.dict[i].tag.toLowerCase().includes(query))
				for (let j = 0; j < this.dict[i].emojiNames.length; j++)
					result.add(this.dict[i].emojiNames[j])

		return result;
	}
};

function makeUsersSearchDictionary() {
	// get public users list
	const headers = new Headers({xhr: "xhr"})
	const user_params = document.getElementById('user_params').value
	return fetch(`/users.csv${user_params}`, {
		headers,
	})
		.then(res => res.json())
		.then(users => {
			for (let i = 0; i < users.length; i++)
			{
				const user = users[i];
				usersSearchDictionary.updateTag(user, user);
				globalUsers.push({
					name: user,
				});
			}

			userSearchDictionaryState = "ready";
		})
}

function curr_word_is_user()
{
	return current_word && current_word.charAt(0) == "@" &&
		current_word.charAt(current_word.length-1) != "@";
}

function openUserSpeedModal()
{
	switch (userSearchDictionaryState) {
		case "inactive":
			userSearchDictionaryState = "loading"
			return makeUsersSearchDictionary();
		case "loading":
			// this works because once the fetch completes, the first keystroke callback will fire and use the current value
			return Promise.reject();
		case "ready":
			return Promise.resolve();
		default:
			throw Error("Unknown user engine state");
	}
}

function populate_inline_user_modal(results, textbox)
{
	selecting = true;

	if (!results || results.size === 0)
	{
		inline_carot_modal.style.display = "none";
		return -1;
	}

	user_index = 0;
	inline_carot_modal.scrollTop = 0;
	inline_carot_modal.innerHTML = "";
	const MAXXX = 50;
	// Not sure why the results is a Set... but oh well
	let i = 0;
	for (let user of results)
	{
		let name = user.name

		if (i++ > MAXXX) return i;
		let user_option = document.createElement("div");
		user_option.className = "inline-modal-option user-option " + (i === 1 ? "selected" : "");
		user_option.tabIndex = 0;
		let user_option_img = document.createElement("img");
		user_option_img.className = "pp20";
		// This is a bit
		user_option_img.src = `/@${name}/pic`

		let user_option_text = document.createElement("span");

		user_option_text.textContent = name;

		user_option.addEventListener('click', () => {
			close_inline_emoji_modal()
			textbox.value = textbox.value.replace(new RegExp(current_word+"(?=\\s|$)", "gi"), `@${name}`)
			textbox.focus()
			if (typeof markdown === "function" && textbox.dataset.preview) {
				markdown(textbox)
			}
		});
		// Pack
		user_option.appendChild(user_option_img);
		user_option.appendChild(user_option_text);
		inline_carot_modal.appendChild(user_option);
	}
	if (i === 0) inline_carot_modal.style.display = "none";
	else inline_carot_modal.style.display = "initial";
	return i;
}
