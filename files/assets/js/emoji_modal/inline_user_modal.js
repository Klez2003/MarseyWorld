let userSearchDictionaryState = "inactive";

let globalUsers = [];

const userMAXXX = 50;

const usersSearchDictionary = {
	array: [],

	updateTag: function(userName) {
		if (userName === undefined)
			return;

		let low = 0;
		let high = this.array.length;

		while (low < high) {
			let mid = (low + high) >>> 1;
			if (this.array[mid] < userName)
				low = mid + 1;
			else
				high = mid;
		}

		let target = low;
		this.array.splice(target, 0, userName);
	},

	completeSearch: function(query) {
		query = query.toLowerCase()
		const result = new Set();

		for (let i = 0; i < this.array.length; i++) {
			if (result.size > userMAXXX) break;
			if (this.array[i].toLowerCase().includes(query))
				result.add(this.array[i])
		}

		return result;
	}
};

function makeUsersSearchDictionary() {
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
				usersSearchDictionary.updateTag(user);
				globalUsers.push(user);
			}

			userSearchDictionaryState = "ready";
		})
}

function curr_word_is_user()
{
	return current_word && current_word.charAt(0) == "@" && current_word.charAt(current_word.length-1) != "@";
}

function openUserSpeedModal()
{
	switch (userSearchDictionaryState) {
		case "inactive":
			userSearchDictionaryState = "loading"
			return makeUsersSearchDictionary();
		case "loading":
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
		return;
	}

	user_index = 0;
	inline_carot_modal.scrollTop = 0;
	inline_carot_modal.innerHTML = "";
	let i = 0;
	for (let name of results)
	{
		name = name.split(',')[0]
		i++;
		let user_option = document.createElement("div");
		user_option.className = "inline-modal-option user-option " + (i === 1 ? "selected" : "");
		user_option.tabIndex = 0;
		let user_option_img = document.createElement("img");
		user_option_img.className = "pp20";
		user_option_img.src = `/@${name}/pic`

		let user_option_text = document.createElement("span");

		user_option_text.textContent = name;

		user_option.addEventListener('click', () => {
			replaceText(textbox, `@${name} `)
		});
		user_option.appendChild(user_option_img);
		user_option.appendChild(user_option_text);
		inline_carot_modal.appendChild(user_option);
	}
	if (i === 0) inline_carot_modal.style.display = "none";
	else inline_carot_modal.style.display = "initial";
}
