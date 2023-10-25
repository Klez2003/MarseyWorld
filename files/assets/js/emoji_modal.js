// This code isn't for feeble minds, you might not understand it, Dr. Transmisia.
// Lappland, you are an absolute idiot and an embarrassment to the Rhodesian people.
// I have done the very thing that you decried impractical.
// The dainty hands of a trans goddess wrote this code. Watch the way her fingers
// dance across the keyboard and learn.

// MIT License. Written by @transbitch

/**
 * currently unused, the type of each emoji that https://rdrama.net/emojis.json returns.
 * @typedef {object} EmojiDef
 * @property {number} author_id
 * @property {string} author_original_username
 * @property {string} author_username
 * @property {number} count
 * @property {number} created_utc
 * @property {string} kind
 * @property {string} name
 * @property {number | null} submitter_id
 * @property {string[]} tags
 */

/**
 * @typedef {{[index: string]: [string, number][]}} EmojiTags
 * @typedef {{[kind: string]: [string, number][]}} EmojiKinds
 */

class EmojiEngine {
	_res;
	/** @type {Promise<void>} */
	loaded = new Promise(res => this._res = res);
	hasLoaded = false;

	/** @type {EmojiTags} */
	tags = {};

	/** @type {EmojiKinds} */
	kinds = {};

	// Memoize this value so we don't have to recompute it.
	_tag_entries;

	/** @type {{[index: string]: HTMLDivElement}} */
	emojiDom = {};

	/** @type {{[index: string]: number}} */
	emojiNameCount = {};

	/** @type {(name: string) => void} */
	onInsert;

	init = async () => {
		if (this.hasLoaded) {
			return;
		}

		await Promise.all([
			this.loadTags(),
			this.loadKinds(),
		]);

		this._tag_entries = Object.entries(this.tags);

		this._res();
		this.hasLoaded = true;
	}

	loadTags = async () => {
		this.tags = await (await fetch('/emoji_tags.json')).json();
	}

	loadKinds = async () => {
		this.kinds = await (await fetch('/emoji_kinds.json')).json();
	}

	search = async (query, maxLength = Infinity) => {
		await this.loaded;

		const resultsSet = new Set();
		const results = [];
		for (const [tag, entries] of this._tag_entries) {
			if (!tag.includes(query)) {
				continue;
			}

			for (const [name, count] of entries) {
				if (resultsSet.has(name)) {
					continue;
				} else if (count < results[maxLength - 1]?.[1]) {
					// All the other emojis in this tag have less uses. We can stop here.
					break;
				}

				resultsSet.add(name);
				// Insert into the array sorted.
				let i = results.length;
				while (i > 0 && count > results[i - 1][1]) {
					i--;
				}
				results.splice(i, 0, [name, count]);
				if (results.length >= maxLength) {
					const [name] = results.pop();
					resultsSet.delete(name);
				}
			}
		}

		return results.map(([name]) => name);
	}

	/**
	 * Get a dom element for a list of emojis in quick dropdown.
	 * @param {string[]} emojiNames 
	 */
	getQuickDoms = (emojiNames) => {
		return emojiNames.map(this.getQuickDom);
	}

	/**
	 * 
	 * @param {*} emojiName 
	 * @returns DOM element for an emoji quick dropdown.
	 */
	getQuickDom = (emojiName) => {
		if (this.emojiDom[emojiName]) {
			return this.emojiDom[emojiName];
		}

		const emojiEl = document.createElement('button');
		emojiEl.classList.add('speed-modal-option', 'emoji-option');
		emojiEl.addEventListener('click', (e) => {
			this.onInsert(emojiName);
		});

		const emojiImgEl = document.createElement('img');
		emojiImgEl.classList.add('speed-modal-image', 'emoji-option-image');
		emojiImgEl.src = emojiEngine.src(emojiName);
		emojiEl.appendChild(emojiImgEl);

		const emojiNameEl = document.createElement('span');
		emojiNameEl.textContent = emojiName;
		emojiEl.appendChild(emojiNameEl);

		this.emojiDom[emojiName] = emojiEl;
		return emojiEl;
	}

	src = (name) => {
		return `${SITE_FULL_IMAGES}/e/${name}.webp`
	}
}

const emojiEngine = new EmojiEngine();

// Quick emoji dropdown & emoji insertion
{
	const emojiDropdownEl = document.createElement('div');
	emojiDropdownEl.classList.add('speed-carot-modal');
	/** @type {null | HTMLTextAreaElement} */
	let inputEl = null;
	let visible = false;
	let typingEmojiCanceled = false;
	let firstDomEl = null;
	let firstEmojiName = null;
	let caretPos = 0;

	// Used by onclick attrib of the smile button
	window.openEmojiModal = (id) => {
		inputEl = document.getElementById(id);
		initEmojiModal();
	}

	emojiEngine.onInsert = (name) => {
		if (!inputEl) {
			return;
		}
		const match = matchTypingEmoji();
		if (match) {
			// We are inserting an emoji which we are typing.
			inputEl.value = `${inputEl.value.slice(0, match.index)}:${name}:${inputEl.value.slice(match.index + name.length)} `;
			// Draw the focus back to this element.
			inputEl.focus();
		} else {
			// We are inserting a new emoji.
			const start = inputEl.value.slice(0, caretPos);
			const end = inputEl.value.slice(caretPos);
			const insert = `:${name}:${end.length === 0 ? ' ' : ''}`;
			inputEl.value = `${start}${insert}${end}`;
			caretPos += insert.length;
			inputEl.setSelectionRange(caretPos, caretPos);
		}

		typingEmojiCanceled = false;
		update();

		// This updates the preview.
		inputEl.dispatchEvent(new Event('input', { bubbles: true }));

		// Update the favorite count.
		if (name in favoriteEmojis) {
			favoriteEmojis[name]++;
		} else {
			favoriteEmojis[name] = 1;
		}
		localStorage.setItem("favorite_emojis", JSON.stringify(favoriteEmojis));
	}

	const inputCanTakeEmojis = (el = inputEl) => {
		return el?.dataset && 'emojis' in el.dataset;
	}

	const matchTypingEmoji = () => {
		return inputEl?.value.substring(0, inputEl.selectionEnd).match(/:([\w!#]+)$/);
	}

	const getTypingEmoji = () => {
		return matchTypingEmoji()?.[1] ?? null;
	}

	const isTypingEmoji = () => {
		return inputCanTakeEmojis() && getTypingEmoji();
	}

	const endTypingEmoji = () => {
		typingEmojiCanceled = false;
	}

	const update = async () => {
		const typing = isTypingEmoji();
		visible = typing && !typingEmojiCanceled;
		if (!visible) {
			emojiDropdownEl.parentElement?.removeChild(emojiDropdownEl);
			return;
		}
		const oldFirst = firstDomEl;
		document.body.appendChild(emojiDropdownEl);
		const search = await emojiEngine.search(getTypingEmoji(), 15);
		firstEmojiName = search[0];
		const domEls = emojiEngine.getQuickDoms(search);
		firstDomEl = domEls[0];
		if (oldFirst !== firstDomEl) {
			oldFirst?.classList.remove('selected');
			firstDomEl.classList.add('selected');
		}
		emojiDropdownEl.replaceChildren(...domEls);
		const { left, bottom } = getCaretPos(inputEl);
		// Using transform instead of top/left is faster.
		emojiDropdownEl.style.transform = `translate(${left}px, ${bottom}px)`;
	}

	// Add a listener when we start typing.
	/**
	 * @param {FocusEvent} e 
	 */
	const onKeyStart = (e) => {
		if (inputCanTakeEmojis(e.target)) {
			inputEl = e.target;
			emojiEngine.init();
			window.removeEventListener('keydown', onKeyStart);
		}
	}

	window.addEventListener('keydown', onKeyStart);
	window.addEventListener('keydown', (e) => {
		if (!visible) {
			return;
		}
		const isFocused = document.activeElement === inputEl
		if (e.key === 'Escape') {
			typingEmojiCanceled = true;
			update();
		} else if (e.key === 'Enter' && isFocused) {
			emojiEngine.onInsert(firstEmojiName);
			e.preventDefault();
		} else if (e.key === 'Tab' && isFocused) {
			firstDomEl.focus();
			firstDomEl.classList.remove("selected");
			e.preventDefault();
		}
	});

	['input', 'click', 'focus'].forEach((event) => {
		window.addEventListener(event, (e) => {
			if (inputCanTakeEmojis(e.target)) {
				inputEl = e.target;
				caretPos = inputEl.selectionEnd;
			}
			update();
			if (!isTypingEmoji()) {
				endTypingEmoji();
			}
		});
	});
}

/** @type {{ [name: string]: number }} */
const favoriteEmojis = JSON.parse(localStorage.getItem("favorite_emojis")) || {};

const initEmojiModal = (() => {
	let hasInit = false;
	
	return async () => {
		if (hasInit) {
			return;
		}
		hasInit = true;

		await emojiEngine.init();

		document.getElementById('emojis-work').style.display = 'none';

		/** @type {{ [tabName: string]: HTMLDivElement }} */
		const tabContentEls = {}

		/** @type {(kind: string, el: HTMLButtonElement) => void} */
		const addTabClickListener = (kind, el) => {
			el.addEventListener('click', (e) => {
				setTab(kind);
			});
		}

		const favorites = Object.entries(favoriteEmojis).sort((a, b) => b[1] - a[1]);
		/** @type {{ [name: string]: HTMLButtonElement }} */
		const favoriteClones = {};

		const favoriteContentEl = (() => {
			const content = document.createElement('div');
			tabContentEls['favorite'] = content;
			return content;
		})();

		let currentTab = 'favorite';
		const setTab = (kind) => {
			currentTab = kind;
			tabContent.replaceChildren(tabContentEls[kind]);
		}

		const emojiModal = document.getElementById('emojiModal');
		const emojiTabsEl = document.getElementById('emoji-modal-tabs');
		const tabContent = document.getElementById('emoji-tab-content');
		/** @type {HTMLInputElement} */
		const searchInputEl = document.getElementById('emoji_search');
		searchInputEl.disabled = false;
		const searchResultsContainerEl = document.createElement('div');
		let isSearching = false;
		/** @type {{ [index: string ]: HTMLButtonElement }} */
		const searchResultsEl = {};
		const favoriteTabEl = document.getElementById('emoji-modal-tabs-favorite');
		addTabClickListener('favorite', favoriteTabEl);

		window.emojiSearch = async () => {
			if (searchInputEl.value.length === 0 && isSearching) {
				isSearching = false;
				setTab(currentTab);
			} else if (searchInputEl.value.length > 0 && !isSearching) {
				isSearching = true;
				tabContent.replaceChildren(searchResultsContainerEl);
			}

			if (isSearching) {
				const query = searchInputEl.value;
				requestIdleCallback(() => {
					emojiEngine.search(query).then((results) => {
						requestIdleCallback(() => {
							searchResultsContainerEl.replaceChildren(...results.map((name) => searchResultsEl[name]));
						}, { timeout: 100 });
					});
				}, { timeout: 100 });
			}
		}

		const promises = Object.entries(emojiEngine.kinds).map(([kind, emojis]) => new Promise((res) => {
			const tabEl = (() => {
				const tab = document.createElement('li');
				const button = document.createElement('button');
				button.type = 'button';
				button.classList.add('nav-link', 'emojitab');
				button.dataset.bsToggle = 'tab';
				button.textContent = kind;
				tab.appendChild(button);
				emojiTabsEl.appendChild(tab);
				addTabClickListener(kind, tab);
				return tab;
			})();

			const tabContentEl = (() => {
				const tabContent = document.createElement('div');
				return tabContent;
			})();

			tabContentEls[kind] = tabContentEl;

			const tick = () => {
				for (const [name, count] of emojis) {
					const buttonEl = document.createElement('button');
					buttonEl.type = 'button';
					buttonEl.classList.add('btn', 'm-1', 'px-0', 'emoji2');
					buttonEl.title = `${name} (${count})`;

					const imgEl = document.createElement('img');
					imgEl.loading = 'lazy';
					imgEl.src = emojiEngine.src(name);
					imgEl.alt = name;
					buttonEl.appendChild(imgEl);

					const searchClone = buttonEl.cloneNode(true);
					const els = [buttonEl, searchClone];

					if (name in favoriteEmojis) {
						const favoriteClone = buttonEl.cloneNode(true);
						favoriteClone.title = `${name} (${favoriteEmojis[name]})`;
						els.push(favoriteClone);
						favoriteClones[name] = favoriteClone;
					}
					
					els.forEach((el) => {
						el.addEventListener('click', (e) => {
							emojiEngine.onInsert(name);
						});
					});

					tabContentEl.appendChild(buttonEl);
					searchResultsEl[name] = searchClone;
				}

				res();

			}
			requestIdleCallback(tick, { timeout: 250 });
		}));

		Promise.all(promises).then(() => {
			for (const [name] of favorites) {
				if (!(name in favoriteClones)) {
					continue;
				}
	
				favoriteContentEl.appendChild(favoriteClones[name]);
			}
		});

		setTab(currentTab);
	}
})();