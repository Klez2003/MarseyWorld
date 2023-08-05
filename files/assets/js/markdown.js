marked.use({
	breaks: true,
	extensions: [
		{
			name: 'mention',
			level: 'inline',
			start: function(src){
				const match = src.match(/@[a-zA-Z0-9_\-]+/);
				return match != null ? match.index : -1;
			},
			tokenizer: function(src) {
				const rule = /^@[a-zA-Z0-9_\-]+/;
				const match = rule.exec(src);
				if(match){
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
				const match = src.match(/![a-zA-Z0-9_\-]+/);
				return match != null ? match.index : -1;
			},
			tokenizer: function(src) {
				const rule = /^![a-zA-Z0-9_\-]+/;
				const match = rule.exec(src);
				if(match){
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
};

function markdown(t) {
	let input = t.value;

	if (!reDisableBeforeUnload.test(location.pathname))
	{
		if (!window.onbeforeunload)
		{
			window.onbeforeunload = function (e) {
				e = e || window.event;
				if (e) {
					e.returnValue = 'Any string';
				}
				return 'Any string';
			};
		}
		else if (!input) {
			window.onbeforeunload = null
		}
	}

	input = input.replace(/\|\|(.*?)\|\|/g, '<spoiler>$1</spoiler>')
	input = input.replace(/(\n|^)>([^ >][^\n]*)/g, '$1<g>\>$2</g>')
	input = input.replace(/((\s|^)[0-9]+)\. /g, '$1\\. ')

	const emojis = Array.from(input.matchAll(/:([a-z0-9_\-!#@]{1,36}):(?![^`]*`)/gi))
	if(emojis != null){
		for(i = 0; i < emojis.length; i++){
			const old = emojis[i][0];
			if (old.includes('marseyrandom')) continue;
						if (old.includes('marseyrandom')) continue
			let emoji = old.replace(/[:]/g,'').toLowerCase();
			
			const modifiers = new Set();
			
			let length = emoji.length
			if(emoji.includes('!!')) modifiers.add(MODIFIERS.REVERSED_MODIFIER);
			emoji = emoji.replaceAll('!', '');
			if(length !== emoji.length) {
				modifiers.add(MODIFIERS.REVERSED);
				length = emoji.length;
			}
			emoji = emoji.replaceAll('#', '');
			if(length !== emoji.length) {
				modifiers.add(MODIFIERS.LARGE);
			}
			const isTalkingFirst = !(emoji.endsWith('pat') && emoji.slice(0, -3).endsWith('talking'));
			if(emoji.endsWith('talking') || (emoji.endsWith('pat') && emoji.slice(0, -3).endsWith('talking'))) {
				modifiers.add(MODIFIERS.TALKING);
				emoji = emoji.endsWith('pat') ? [emoji.slice(0, -10), emoji.slice(-3)].join('') : emoji.slice(0, -7);
			}
			if(emoji.endsWith('pat')) {
				modifiers.add(MODIFIERS.PAT);
				emoji = emoji.slice(0, -3);
			}
			
			if(emoji.startsWith('@')) {
				emoji = emoji.slice(1);
				modifiers.add(MODIFIERS.USER);
			}
			
			
			if(emoji === 'marseyunpettable') {
				modifiers.delete(MODIFIERS.PAT);
				if(!isTalkingFirst) {
					modifiers.delete(MODIFIERS.TALKING);
				}
			}

			const mirroredClass = 'mirrored';
			const emojiClass = modifiers.has(MODIFIERS.LARGE) ? 'emoji-lg' : 'emoji';

			// patted emotes cannot be flipped back easily so they don't support double flipping
			const spanClass = modifiers.has(MODIFIERS.REVERSED) && (modifiers.has(MODIFIERS.PAT) || !modifiers.has(MODIFIERS.REVERSED_MODIFIER)) ? mirroredClass : '';
			const imgClass = modifiers.has(MODIFIERS.REVERSED) && modifiers.has(MODIFIERS.REVERSED_MODIFIER) ? mirroredClass : ''
			
			if (modifiers.has(MODIFIERS.PAT) || modifiers.has(MODIFIERS.TALKING)) {
				const talkingHtml = modifiers.has(MODIFIERS.TALKING) ? `<img loading="lazy" src="${SITE_FULL_IMAGES}/i/talking.webp">` : '';
				const patHtml = modifiers.has(MODIFIERS.PAT) ? `<img loading="lazy" src="${SITE_FULL_IMAGES}/i/hand.webp">` : '';
				const url = modifiers.has(MODIFIERS.USER) ? `/@${emoji}/pic` : `${SITE_FULL_IMAGES}/e/${emoji}.webp`;
				const modifierHtml = isTalkingFirst ? `${talkingHtml}${patHtml}` : `${patHtml}${talkingHtml}`;
				input = input.replace(old, `<span class="pat-preview ${spanClass}" data-bs-toggle="tooltip">${modifierHtml}<img loading="lazy" class="${emojiClass} ${imgClass}" src="${url}"></span>`);
			} else {
				input = input.replace(old, `<img loading="lazy" class="${emojiClass} ${modifiers.has(MODIFIERS.REVERSED) ? mirroredClass : ''}" src="${SITE_FULL_IMAGES}/e/${emoji}.webp">`);
			}
		}
	}

	let options = Array.from(input.matchAll(/\$\$([^\$\n]+)\$\$(?![^`]*`)/gi))
	if(options != null){
		for(i = 0; i < options.length; i++){
			const option = options[i][0];
			const option2 = option.replace(/\$\$/g, '').replace(/\n/g, '')
			input = input.replace(option, `<div class="custom-control mb-3"><input type="checkbox" class="custom-control-input" id="option-${i}"><label class="custom-control-label" for="option-${i}">${option2} - <a>0 votes</a></label></div>`);
		}
	}

	options = Array.from(input.matchAll(/&&([^&\n]+)&&(?![^`]*`)/gi))
	if(options != null){
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

	text.innerText = length + ' / ' + maxLength;
}

function remove_dialog() {
	window.onbeforeunload = null;
}
