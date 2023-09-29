marked.use({
	extensions: [
		{
			name: 'mention',
			level: 'inline',
			start: function(src){
				const match = src.match(/@[\w-]{1,30}/);
				return match != null ? match.index : -1;
			},
			tokenizer: function(src) {
				const rule = /^@[\w-]{1,30}/;
				const match = rule.exec(src);
				if (match){
					return {
						type: 'mention',
						raw: match[0],
						text: match[0].trim().slice(1),
						tokens: []
					};
				}
			},
			renderer(token) {
				const u = token.raw;
				return `<a href="/${u}"><img loading="lazy" src="/${u}/pic" class="pp20"> ${u}</a>`;
			}
		},
		{
			name: 'group_mention',
			level: 'inline',
			start: function(src){
				const match = src.match(/![\w-]{3,25}/);
				return match != null ? match.index : -1;
			},
			tokenizer: function(src) {
				const rule = /^![\w-]{3,25}/;
				const match = rule.exec(src);
				if (match){
					return {
						type: 'group_mention',
						raw: match[0],
						text: match[0].trim().slice(1),
						tokens: []
					};
				}
			},
			renderer(token) {
				const g = token.raw;
				return `<a href="/${g}">${g}</a>`;
			}
		},
	]
});

const reDisableBeforeUnload = /^\/submit|^\/h\/[a-zA-Z0-9_\-]{3,20}\/submit/;

const image_regex_extensions = document.getElementById('IMAGE_FORMATS').value.replaceAll(',', '|')
const regex_pattern = String.raw`(^|\s)(https:\/\/[\w\-.#&/=\?@%;+,:]{5,250}(\.|\?format=)(` + image_regex_extensions + String.raw`)((\?|&)[\w\-.#&/=\?@%;+,:]*)?)($|\s)`
const compiled_regex = new RegExp(regex_pattern, "g");

const approved_embed_hosts = document.getElementById('approved_embed_hosts').value.replace("{'", "").replace("'}", "").split("', '")
function replace_image(match, prefix, url) {
	if (approved_embed_hosts.some(x => url.startsWith(`https://${x}/`)))
		return `${prefix}![](${url})`

	return match
}

const MODIFIERS = {
	PAT: 1,
	TALKING: 2,
	LARGE: 3,
	REVERSED: 4,
	USER: 5,
	REVERSED_MODIFIER: 6,
	GENOCIDE: 7,
	LOVE: 8,
};

const findAllEmoteEndings = (word) => {
	let hasReachedNonModifer = false;
	let currWord = word;
	const currEndings = [];
	while(!hasReachedNonModifer) {
		if(currWord.endsWith('pat')) {
			if(currEndings.indexOf(MODIFIERS.PAT) !== -1) {
				hasReachedNonModifer = true;
				continue;
			}
			currWord = currWord.slice(0, -3);
			currEndings.push(MODIFIERS.PAT);
			continue;
		}

		if(currWord.endsWith('talking')) {
			if(currEndings.indexOf(MODIFIERS.TALKING) !== -1) {
				hasReachedNonModifer = true;
				continue;
			}
			currWord = currWord.slice(0, -7);
			currEndings.push(MODIFIERS.TALKING);
			continue;
		}

		if(currWord.endsWith('genocide')) {
			if(currEndings.indexOf(MODIFIERS.GENOCIDE) !== -1) {
				hasReachedNonModifer = true;
				continue;
			}
			currWord = currWord.slice(0, -8);
			currEndings.push(MODIFIERS.GENOCIDE);
			continue;
		}

		if(currWord.endsWith('love')) {
			if(currEndings.indexOf(MODIFIERS.LOVE) !== -1) {
				hasReachedNonModifer = true;
				continue;
			}
			currWord = currWord.slice(0, -4);
			currEndings.push(MODIFIERS.LOVE);
			continue;
		}

		hasReachedNonModifer = true;
	}


	return [currEndings, currWord];
}

function markdown(t) {
	let input = t.value;

	if (!reDisableBeforeUnload.test(location.pathname))
	{
		if (!onbeforeunload)
		{
			onbeforeunload = function (e) {
				e = e || event;
				if (e) {
					e.returnValue = 'Any string';
				}
				return 'Any string';
			};
		}
		else if (!input) {
			onbeforeunload = null
		}
	}

	if (!input.includes('```') && !input.includes('<pre>'))
		input = input.replace(/\n/g, '\n\n')
	input = input.replace(/\|\|(.*?)\|\|/g, '<spoiler>$1</spoiler>')
	input = input.replace(/(\n|^)>([^ >][^\n]*)/g, '$1<g>\>$2</g>')
	input = input.replace(/((\s|^)[0-9]+)\. /g, '$1\\. ')

	const emojis = Array.from(input.matchAll(/:([a-z0-9_\-!#@]{1,72}):(?![^`]*`)/gi))
	if (emojis != null){
		for(i = 0; i < emojis.length; i++){
			const old = emojis[i][0];
			if (old.includes('marseyrandom')) continue;
						if (old.includes('marseyrandom')) continue
			let emoji = old.replace(/[:]/g,'').toLowerCase();

			const modifiers = new Set();

			let length = emoji.length;
			if(emoji.includes('!!')) modifiers.add(MODIFIERS.REVERSED_MODIFIER);
			emoji = emoji.replaceAll('!', '');
			if (length !== emoji.length) {
				modifiers.add(MODIFIERS.REVERSED);
				length = emoji.length;
			}
			emoji = emoji.replaceAll('#', '');
			if (length !== emoji.length) {
				modifiers.add(MODIFIERS.LARGE);
			}
			let endingModifiers;
			[endingModifiers, emoji] = findAllEmoteEndings(emoji);
			const isTalkingFirst = endingModifiers.indexOf(MODIFIERS.PAT) > endingModifiers.indexOf(MODIFIERS.TALKING);

			endingModifiers.forEach(modifiers.add, modifiers)

			if (emoji.startsWith('@')) {
				emoji = emoji.slice(1);
				modifiers.add(MODIFIERS.USER);
			}


			if (emoji === 'marseyunpettable') {
				modifiers.delete(MODIFIERS.PAT);
				if (!isTalkingFirst) {
					modifiers.delete(MODIFIERS.TALKING);
				}
			}

			const mirroredClass = 'mirrored';
			const genocideClass = modifiers.has(MODIFIERS.GENOCIDE) ? 'cide' : '';
			const emojiClass = modifiers.has(MODIFIERS.LARGE) ? 'emoji-lg' : 'emoji';
			const patClass = modifiers.has(MODIFIERS.PAT) ? 'pat-preview' : '';

			// patted emotes cannot be flipped back easily so they don't support double flipping
			const spanClass = modifiers.has(MODIFIERS.REVERSED) && (modifiers.has(MODIFIERS.PAT) || !modifiers.has(MODIFIERS.REVERSED_MODIFIER)) ? mirroredClass : '';
			const imgClass = modifiers.has(MODIFIERS.REVERSED) && modifiers.has(MODIFIERS.REVERSED_MODIFIER) ? mirroredClass : ''
			const lovedClass = modifiers.has(MODIFIERS.LOVE) ? 'love-preview' : '';

			if ([MODIFIERS.TALKING, MODIFIERS.GENOCIDE, MODIFIERS.PAT, MODIFIERS.LOVE].some((modifer) =>  modifiers.has(modifer))) {
				const talkingHtml = modifiers.has(MODIFIERS.TALKING) ? `<img loading="lazy" src="${SITE_FULL_IMAGES}/i/talking.webp">` : '';
				const patHtml = modifiers.has(MODIFIERS.PAT) ? `<img loading="lazy" src="${SITE_FULL_IMAGES}/i/hand.webp">` : '';
				const loveHtml = modifiers.has(MODIFIERS.LOVE) ? `<img loading="lazy" class="${emojiClass}" src="${SITE_FULL_IMAGES}/i/love-foreground.webp"><img loading="lazy" class="${emojiClass}" src="${SITE_FULL_IMAGES}/i/love-background.webp">` : '';
				const url = modifiers.has(MODIFIERS.USER) ? `/@${emoji}/pic` : `${SITE_FULL_IMAGES}/e/${emoji}.webp`;
				const modifierHtml = isTalkingFirst ? `${talkingHtml}${patHtml}${loveHtml}` : `${patHtml}${talkingHtml}${loveHtml}`;
				input = input.replace(old, `<span class="${patClass} ${spanClass} ${genocideClass}" data-bs-toggle="tooltip">${modifierHtml}<img loading="lazy" class="${emojiClass} ${imgClass} ${lovedClass}" src="${url}"></span>`);
			} else {
				input = input.replace(old, `<img loading="lazy" class="${emojiClass} ${modifiers.has(MODIFIERS.REVERSED) ? mirroredClass : ''}" src="${SITE_FULL_IMAGES}/e/${emoji}.webp">`);
			}
		}
	}

	let options = Array.from(input.matchAll(/\$\$([^\$\n]+)\$\$(?![^`]*`)/gi))
	if (options != null){
		for(i = 0; i < options.length; i++){
			const option = options[i][0];
			const option2 = option.replace(/\$\$/g, '').replace(/\n/g, '')
			input = input.replace(option, `<div class="custom-control mb-3"><input type="checkbox" class="custom-control-input" id="option-${i}"><label class="custom-control-label" for="option-${i}">${option2} - <a>0 votes</a></label></div>`);
		}
	}

	options = Array.from(input.matchAll(/&&([^&\n]+)&&(?![^`]*`)/gi))
	if (options != null){
		for(i = 0; i < options.length; i++){
			const option = options[i][0];
			const option2 = option.replace(/&&/g, '').replace(/\n/g, '')
			input = input.replace(option, `<div class="custom-control mb-3"><input type="radio" name="choice" class="custom-control-input" id="option-${i}"><label class="custom-control-label" for="option-${i}">${option2} - <a>0 votes</a></label></div>`);
		}
	}

	input = input.replace(compiled_regex, replace_image)

	input = marked(input)

	const preview = document.getElementById(t.dataset.preview)

	preview.innerHTML = input

	const expandable = preview.querySelectorAll('img[alt]');
	for (const element of expandable) {
		element.onclick = () => {expandImage()};
	}
}

function charLimit(form, text) {

	const input = document.getElementById(form);

	text = document.getElementById(text);

	const length = input.value.length;

	const maxLength = input.getAttribute("maxlength");

	if (length >= maxLength) {
		text.style.color = "#E53E3E";
	}
	else if (length >= maxLength * .72){
		text.style.color = "#FFC107";
	}
	else {
		text.style.color = "#A0AEC0";
	}

	text.textContent = length + ' / ' + maxLength;
}

function remove_dialog() {
	onbeforeunload = null;
}
