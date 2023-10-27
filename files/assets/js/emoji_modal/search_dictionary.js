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

function makeEmojisSearchDictionary() {
	// get public emojis list
	const headers = new Headers({xhr: "xhr"})
	const emoji_num = document.getElementById('emoji_num').value
	return fetch(`/emojis.csv?x=${emoji_num}`, {
		headers,
	})
		.then(res => res.json())
		.then(emojis => {
			globalEmojis = emojis.map(({name, author_username, count}) => ({name, author_username, count}));

			for (let i = 0; i < emojis.length; i++)
			{
				const emoji = emojis[i];

				emojisSearchDictionary.updateTag(emoji.name, emoji.name);

				if (!emoji.author_username.endsWith(' user')) {
					emojisSearchDictionary.updateTag(`@${emoji.author_username.toLowerCase()}`, emoji.name);
					if (emoji.author_original_username != emoji.author_username)
						emojisSearchDictionary.updateTag(`@${emoji.author_original_username.toLowerCase()}`, emoji.name);
					if (emoji.author_prelock_username !== undefined)
						emojisSearchDictionary.updateTag(`@${emoji.author_prelock_username.toLowerCase()}`, emoji.name);
				}

				if (emoji.tags instanceof Array)
					for(let i = 0; i < emoji.tags.length; i++)
						emojisSearchDictionary.updateTag(emoji.tags[i], emoji.name);
			}

			emojiSpeedEngineState = "ready";
		})
}
