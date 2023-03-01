function getMessageFromJsonData(success, json) {
	let message = success ? "Success!" : "Error, please try again later";
	let key = success ? "message" : "error";
	if (!json || !json[key]) return message;
	message = json[key];
	if (!success && json["details"]) {
		message = json["details"];
	}
	return message;
}

function showToast(success, message, isToastTwo=false) {
	let element = success ? "toast-post-success" : "toast-post-error";
	let textElement = element + "-text";
	if (isToastTwo) {
		element = element + "2";
		textElement = textElement + "2";
	}
	if (!message) {
		message = success ? "Success" : "Error, please try again later";
	}
	document.getElementById(textElement).innerText = message;
	bootstrap.Toast.getOrCreateInstance(document.getElementById(element)).show();
}

function createXhrWithFormKey(url, method="POST", form=new FormData()) {
	const xhr = new XMLHttpRequest();
	xhr.open(method, url);
	xhr.setRequestHeader('xhr', 'xhr');
	if (!form) form = new FormData();
	form.append("formkey", formkey());
	return [xhr, form]; // hacky but less stupid than what we were doing before
}

function postToast(t, url, data, extraActionsOnSuccess, method="POST") {
	const isShopConfirm = t.id.startsWith('buy1-') || t.id.startsWith('buy2-') || t.id.startsWith('giveaward')

	if (!isShopConfirm)
	{
		t.disabled = true;
		t.classList.add("disabled");
	}

	let form = new FormData();
	if(typeof data === 'object' && data !== null) {
		for(let k of Object.keys(data)) {
			form.append(k, data[k]);
		}
	}
	const xhr = createXhrWithFormKey(url, method, form);
	xhr[0].onload = function() {
		let result
		let message;
		let success = xhr[0].status >= 200 && xhr[0].status < 300;
		if (success && extraActionsOnSuccess) result = extraActionsOnSuccess(xhr[0]);
		if (typeof result == "string") {
			message = result;
		} else {
			message = getMessageFromJsonData(success, JSON.parse(xhr[0].response));
		}
		let oldToast = bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-' + (success ? 'error': 'success'))); // intentionally reversed here: this is the old toast
		oldToast.hide();
		showToast(success, message);
		if (!isShopConfirm) {
			t.disabled = false;
			t.classList.remove("disabled");
		}
		return success;
	};
	xhr[0].send(xhr[1]);

	if (!isShopConfirm)
	{
		setTimeout(() => {
			t.disabled = false;
			t.classList.remove("disabled");
		}, 2000);
	}
}

function postToastReload(t, url, method="POST") {
	postToast(t, url,
		{
		},
		() => {
			location.reload()
		}
	, method);
}

function postToastSwitch(t, url, button1, button2, cls, extraActionsOnSuccess, method="POST") {
	postToast(t, url,
		{
		},
		(xhr) => {
			if (button1)
			{
				if (typeof(button1) == 'boolean') {
					location.reload()
				} else {
					try {
						document.getElementById(button1).classList.toggle(cls);
					}
					catch (e) {}
					try {
						document.getElementById(button2).classList.toggle(cls);
					}
					catch (e) {}
				}
			}
			if (typeof extraActionsOnSuccess == 'function')
			extraActionsOnSuccess(xhr);
		}
	, method);
}

if (!location.pathname.endsWith('/submit'))
{
	document.addEventListener('keydown', (e) => {
		if(!((e.ctrlKey || e.metaKey) && e.key === "Enter")) return;

		const targetDOM = document.activeElement;
		if(!(targetDOM instanceof HTMLTextAreaElement || targetDOM instanceof HTMLInputElement)) return;

		const formDOM = targetDOM.parentElement;

		const submitButtonDOMs = formDOM.querySelectorAll('input[type=submit], .btn-primary');
		if(submitButtonDOMs.length === 0)
			throw new TypeError("I am unable to find the submit button :(. Contact the head custodian immediately.")

		const btn = submitButtonDOMs[0]
		btn.click();
	});
}

function disable(t) {
	t.classList.add('disabled');
	setTimeout(() => {
		t.classList.remove("disabled");
	}, 2000);
}

function autoExpand(field) {
	xpos=window.scrollX;
	ypos=window.scrollY;

	field.style.height = 'inherit';

	let computed = window.getComputedStyle(field);

	let height = parseInt(computed.getPropertyValue('border-top-width'), 10)
	+ parseInt(computed.getPropertyValue('padding-top'), 10)
	+ field.scrollHeight
	+ parseInt(computed.getPropertyValue('padding-bottom'), 10)
	+ parseInt(computed.getPropertyValue('border-bottom-width'), 10);

	field.style.height = height + 'px';
	if (Math.abs(window.scrollX - xpos) < 1 && Math.abs(window.scrollY - ypos) < 1) return;
	window.scrollTo(xpos,ypos);
};

const textareas = document.getElementsByTagName('textarea')
for (const element of textareas) {
	element.addEventListener('input', () => {
		autoExpand(element)
	});
}

function smoothScrollTop()
{
	window.scrollTo({ top: 0, behavior: 'smooth' });
}

// Click navbar to scroll back to top
const nav = document.getElementsByTagName('nav')

if (nav.length) {
	nav[0].addEventListener('click', (e) => {
		if (e.target.id === "navbar" ||
			e.target.classList.contains("container-fluid") ||
			e.target.id == "navbarResponsive" ||
			e.target.id == "logo-container" ||
			e.target.classList.contains("srd"))
			smoothScrollTop();
	}, false);
}

function formkey() {
	let formkey = document.getElementById("formkey")
	if (formkey) return formkey.innerHTML;
	else return null;
}

function expandImage(url) {
	const e = this.event
	if(e.ctrlKey || e.metaKey || e.shiftKey || e.altKey)
		return;
	e.preventDefault();
	if (!url)
	{
		url = e.target.dataset.src
		if (!url) url = e.target.src
	}
	document.getElementById("desktop-expanded-image").src = url.replace("200w.webp", "giphy.webp");
	document.getElementById("desktop-expanded-image-wrap-link").href = url.replace("200w.webp", "giphy.webp");

	bootstrap.Modal.getOrCreateInstance(document.getElementById('expandImageModal')).show();
};

function bs_trigger(e) {
	let tooltipTriggerList = [].slice.call(e.querySelectorAll('[data-bs-toggle="tooltip"]'));
	tooltipTriggerList.map(function(element){
		return bootstrap.Tooltip.getOrCreateInstance(element);
	});

	const popoverTriggerList = [].slice.call(e.querySelectorAll('[data-bs-toggle="popover"]'));
	popoverTriggerList.map(function(popoverTriggerEl) {
		const popoverId = popoverTriggerEl.getAttribute('data-content-id');
		let contentEl;
		try {contentEl = e.getElementById(popoverId);}
		catch(t) {contentEl = document.getElementById(popoverId);}
		if (contentEl) {
			return bootstrap.Popover.getOrCreateInstance(popoverTriggerEl, {
				content: contentEl.innerHTML,
				html: true,
			});
		}
	})

	if (typeof update_speed_emoji_modal == 'function') {
		let forms = e.querySelectorAll("textarea, .allow-emojis");
		forms.forEach(i => {
			let pseudo_div = document.createElement("div");
			pseudo_div.className = "ghostdiv";
			pseudo_div.style.display = "none";
			i.after(pseudo_div);
			i.addEventListener('input', update_speed_emoji_modal, false);
			i.addEventListener('keydown', speed_carot_navigate, false);
		});
	}
}

function escapeHTML(unsafe) {
	return unsafe.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

function showmore(t) {
	let div = t
	while (!(div.id && (div.id.startsWith('comment-text-') || div.id == 'post-text'))){
		div = div.parentElement
	}
	div = div.parentElement

	let text = div.getElementsByTagName('d')[0]
	if (!text) text = div.getElementsByClassName('showmore-text')[0]
	if (!text) text = div.getElementsByClassName('d-none')[0]

	text.classList.add('showmore-text')

	text.classList.toggle('d-none')
	if (text.classList.contains('d-none'))
		t.innerHTML = 'SHOW MORE'
	else
		t.innerHTML = 'SHOW LESS'
}

function formatDate(d) {
	let year = d.getFullYear();
	let monthAbbr = d.toLocaleDateString('en-us', {month: 'short'});
	let day = d.getDate();
	let hour = ("0" + d.getHours()).slice(-2);
	let minute = ("0" + d.getMinutes()).slice(-2);
	let second = ("0" + d.getSeconds()).slice(-2);
	let tzAbbr = d.toLocaleTimeString('en-us', {timeZoneName: 'short'}).split(' ')[2];

	return (day + " " + monthAbbr + " " + year + " "
			 + hour + ":" + minute + ":" + second + " " + tzAbbr);
}

const timestamps = document.querySelectorAll('[data-time]');

for (const e of timestamps) {
	e.innerHTML = formatDate(new Date(e.dataset.time*1000));
};

function timestamp(t, ti) {
	const date = formatDate(new Date(ti*1000));
	t.setAttribute("data-bs-original-title", date);
};

function areyousure(t) {
	if (t.value)
		t.value = 'Are you sure?'
	else
		t.innerHTML = t.innerHTML.replace(t.textContent, 'Are you sure?')

	t.setAttribute("data-onclick", t.dataset.areyousure);

	if (t.dataset.dismiss)
		t.setAttribute("data-bs-dismiss", t.dataset.dismiss);
}

function prepare_to_pause(audio) {
	for (const e of document.querySelectorAll('video,audio'))
	{
		e.addEventListener('play', () => {
			if (!audio.paused) audio.pause();
		});
	}

	document.addEventListener('click', (e) => {
		if ((e.target.tagName.toLowerCase() == "lite-youtube" || e.target.classList.contains('lty-playbtn')) && !audio.paused) {
			audio.pause();
		}
	});
}

function sendFormXHR(form, extraActionsOnSuccess) {
	const xhr = new XMLHttpRequest();

	formData = new FormData(form);

	formData.append("formkey", formkey());
	actionPath = form.getAttribute("action");

	xhr.open("POST", actionPath);
	xhr.setRequestHeader('xhr', 'xhr');

	xhr.onload = function() {
		if (xhr.status >= 200 && xhr.status < 300) {
			let data = JSON.parse(xhr.response);
			showToast(true, getMessageFromJsonData(true, data));
			if (extraActionsOnSuccess) extraActionsOnSuccess(xhr);
		} else {
			document.getElementById('toast-post-error-text').innerText = "Error, please try again later."
			try {
				let data=JSON.parse(xhr.response);
				bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-error')).show();
				document.getElementById('toast-post-error-text').innerText = data["error"];
				if (data && data["details"]) document.getElementById('toast-post-error-text').innerText = data["details"];
			} catch(e) {
				bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-success')).hide();
				bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-error')).show();
			}
		}
	};

	xhr.send(formData);
}

function sendFormXHRSwitch(form, donthideself) {
	sendFormXHR(form,
		() => {
			form.previousElementSibling.classList.remove('d-none');
			if (!donthideself)
				form.classList.add('d-none');
		}
	)
}

let sortAscending = {};

function sort_table(t) {
	const n = Array.prototype.indexOf.call(t.parentElement.children, t);
	const table = this.event.target.parentElement.parentElement.parentElement
	const rows = table.rows;
	let items = [];
	for (let i = 1; i < rows.length; i++) {
		const ele = rows[i];
		let x = rows[i].getElementsByTagName("TD")[n];
		if (!('sortKey' in x.dataset)) {
			x = x.getElementsByTagName('a')[0] || x;
		}
		let attr;
		if ('sortKey' in x.dataset) {
			attr = x.dataset.sortKey;
		} else if ('time' in x.dataset) {
			attr = parseInt(x.dataset.time);
		} else {
			attr = x.innerText
			if (/^[\d-,]+$/.test(x.innerHTML)) {
				attr = parseInt(attr.replace(/,/g, ''))
			}
		}
		items.push({ele, attr});
	}
	if (sortAscending[n]) {
		items.sort((a, b) => a.attr > b.attr ? 1 : -1);
		sortAscending[n] = false;
	} else {
		items.sort((a, b) => a.attr < b.attr ? 1 : -1);
		sortAscending[n] = true;
	}

	for (let i = items.length - 1; i--;) {
		items[i].ele.parentNode.insertBefore(items[i].ele, items[i + 1].ele);
	}
}

if (window.matchMedia('(display-mode: minimal-ui)')['matches']) {
	const links = document.querySelectorAll('a[data-target="t"]');
	for (const link of links) {
		link.removeAttribute("target");
	}
}

if (document.getElementById('gbrowser').value == 'apple') {
	const videos = document.querySelectorAll('video')

	for (const video of videos) {
		const link = video.src
		const htmlString = `
			<a rel="nofollow noopener" href="${link}" target="_blank">
				<div class="d-flex justify-content-between align-items-center border rounded p-2 mb-3 download-video">
					<span>${link}</span>
					<i class="fas fa-external-link-alt text-small"></i>
				</div>
			</a>`
		const div = document.createElement('div');
		div.innerHTML = htmlString;
		video.after(div)
	}
}

function logout(t) {
	postToast(t, '/logout',
		{
		},
		() => {
			location.href = '/'
		});
}

const width = (window.innerWidth > 0) ? window.innerWidth : screen.width;
function focusSearchBar(element)
{
	if (width >= 768) {
		element.focus();
	}
}





//FILE SHIT



let oldfiles = {};

function handle_files(input, newfiles) {
	if (!newfiles) return;
	
	const ta = input.parentElement.parentElement.parentElement.parentElement.querySelector('textarea.file-ta');

	if (oldfiles[ta.id]) {
		let list = new DataTransfer();
		for (const file of oldfiles[ta.id]) {
			 list.items.add(file);
		}
		for (const file of newfiles) {
			list.items.add(file);
		}
		input.files = list.files;
	}
	else {
		input.files = newfiles;
		oldfiles[ta.id] = []
	}

	const span = input.previousElementSibling
	if (input.files.length > 20)
	{
		alert("You can't upload more than 20 files at one time!")
		input.value = null
		input.parentElement.nextElementSibling.classList.add('d-none');
		span.innerHTML = ''
		oldfiles[ta.id] = []
		return
	}

	if (!span.innerHTML) span.innerHTML = ' '

	if (ta.value && !ta.value.endsWith('\n')) {
		ta.value += '\n'
	}

	for (const file of newfiles) {
		oldfiles[ta.id].push(file)
		if (span.innerHTML != ' ') span.innerHTML += ', '
		span.innerHTML += file.name.substr(0, 30);
		if (location.pathname != '/chat')
			ta.setRangeText(`[${file.name}]\n`);
	}

	autoExpand(ta)

	input.parentElement.nextElementSibling.classList.remove('d-none')

	if (typeof checkForRequired === "function") checkForRequired();
}


document.onpaste = function(event) {
	const files = structuredClone(event.clipboardData.files);
	if (!files.length) return

	const focused = document.activeElement;
	let input;

	if (location.pathname.endsWith('/submit')) {
		if (focused) {
			input = document.getElementById('file-upload-submit')
		}
		else {
			f=document.getElementById('file-upload');
			f.files += files;
	
			if (f.files.length > 20)
			{
				alert("You can't upload more than 20 files at one time!")
				return
			}
	
			document.getElementById('filename-show').textContent = filename;
			document.getElementById('urlblock').classList.add('d-none');
			if (IMAGE_FORMATS.some(s => filename.endsWith(s)))
			{
				const fileReader = new FileReader();
				fileReader.readAsDataURL(f.files[0]);
				fileReader.addEventListener("load", function () {document.getElementById('image-preview').setAttribute('src', this.result);});
			}
			document.getElementById('post-url').value = null;
			localStorage.setItem("post-url", "")
			document.getElementById('image-upload-block').classList.remove('d-none')
			checkForRequired();
			return;
		}
	}
	else if (focused) {
		input = focused.parentElement.querySelector('input[type="file"]')
	}
	else {
		input = document.querySelector('input[type="file"]')
	}

	handle_files(input, files);
}

function cancel_files(element) {
	const input = element.previousElementSibling.querySelector('input[type="file"]');
	const span = input.previousElementSibling;
	const ta = input.parentElement.parentElement.parentElement.parentElement.querySelector('textarea.file-ta');

	for (const file of input.files) {
		ta.value = ta.value.replaceAll(`[${file.name}]`, "");
	}
	ta.value = ta.value.trim();

	span.innerHTML = '';

	input.value = null;

	input.parentElement.nextElementSibling.classList.add('d-none');

	oldfiles[ta.id] = [];

	element.classList.add('d-none');

	ta.focus();

	if (typeof checkForRequired === "function") checkForRequired();
}

function handleUploadProgress(e, upload_prog) {
	const bar = upload_prog.firstElementChild;
	const percentIndicator = upload_prog.lastElementChild;
		
	upload_prog.classList.remove("d-none")
	if (e.lengthComputable) {
		const progressPercent = Math.floor((e.loaded / e.total) * 100);
		bar.value = progressPercent;
		percentIndicator.textContent = progressPercent + '%';
	}
}
