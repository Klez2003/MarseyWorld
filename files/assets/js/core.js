const SITE_FULL_IMAGES = document.getElementById('SITE_FULL_IMAGES').value

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

function showToast(success, message) {
	const oldToast = bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-' + (success ? 'error': 'success'))); // intentionally reversed here: this is the old toast
	oldToast.hide();
	let element = success ? "toast-post-success" : "toast-post-error";
	let textElement = element + "-text";
	if (!message) {
		message = success ? "Action successful!" : "Error, please try again later";
	}
	document.getElementById(textElement).textContent = message;
	bootstrap.Toast.getOrCreateInstance(document.getElementById(element)).show();
}

function createXhrWithFormKey(url, form=new FormData(), method='POST') {
	const xhr = new XMLHttpRequest();
	xhr.open(method, url);
	xhr.setRequestHeader('xhr', 'xhr');
	if (!form) form = new FormData();
	form.append("formkey", formkey());
	return [xhr, form]; // hacky but less stupid than what we were doing before
}

function postToast(t, url, data, extraActionsOnSuccess, extraActionsOnFailure) {
	t.disabled = true;
	t.classList.add("disabled");

	let form = new FormData();
	if (typeof data === 'object' && data !== null) {
		for(let k of Object.keys(data)) {
			form.append(k, data[k]);
		}
	}
	const xhr = createXhrWithFormKey(url, form);
	xhr[0].onload = function() {
		const success = xhr[0].status >= 200 && xhr[0].status < 300;

		if (!(extraActionsOnSuccess == reload && success)) {
			t.disabled = false;
			t.classList.remove("disabled");
		}

		let result
		let message;
		if (typeof result == "string") {
			message = result;
		} else {
			message = getMessageFromJsonData(success, JSON.parse(xhr[0].response));
		}
		showToast(success, message);
		if (success && extraActionsOnSuccess) extraActionsOnSuccess(xhr[0]);
		if (!success && extraActionsOnFailure) extraActionsOnFailure(xhr[0]);
		return success;
	};
	xhr[0].send(xhr[1]);
}

function handle_disabled(t) {
	btn = t.parentElement.getElementsByClassName('handle_disabled')[0]
	if (!btn) return
	if (t.value) {
		btn.disabled = false;
		btn.classList.remove('disabled')
	}
	else {
		btn.disabled = true;
		btn.classList.add('disabled')
	}
}

function postToastReload(t, url) {
	postToast(t, url, {}, reload);
}

function postToastSwitch(t, url, button1, button2, cls, extraActionsOnSuccess) {
	postToast(t, url,
		{
		},
		(xhr) => {
			if (button1)
			{
				if (typeof button1 == 'boolean') {
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
		});
}

if (!location.pathname.endsWith('/submit'))
{
	document.addEventListener('keydown', (e) => {
		if (!((e.ctrlKey || e.metaKey) && e.key === "Enter")) return;

		const targetDOM = document.activeElement;
		if (!(targetDOM instanceof HTMLTextAreaElement || targetDOM instanceof HTMLInputElement)) return;

		const formDOM = targetDOM.parentElement;

		if (formDOM.id == 'note_section') {
			document.getElementById('giveaward').click();
			return
		}

		if (location.pathname == '/admin/orgy') {
			document.getElementById('start-orgy').click();
			return
		}

		const submitButtonDOMs = formDOM.querySelectorAll('input[type=submit], .btn-primary');
		if (submitButtonDOMs) {
			const btn = submitButtonDOMs[0]
			btn.click();
		}
	});
}


function autoExpand(field) {
	xpos = window.scrollX;
	ypos = window.scrollY;

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
	if (e.ctrlKey || e.metaKey || e.shiftKey || e.altKey)
		return;
	e.preventDefault();

	document.getElementById("desktop-expanded-image").src = '';
	document.getElementById("desktop-expanded-image-wrap-link").href = '';

	if (!url)
	{
		url = e.target.dataset.src
		if (!url) url = e.target.src
	}
	document.getElementById("desktop-expanded-image").src = url.replace("200w.webp", "giphy.webp");
	document.getElementById("desktop-expanded-image-wrap-link").href = url.replace("200w.webp", "giphy.webp");

	location.hash = 'm-expandImage'
};

function bs_trigger(e) {
	let tooltipTriggerList = [].slice.call(e.querySelectorAll('[data-bs-toggle="tooltip"]'));
	tooltipTriggerList.map(function(element){
		return bootstrap.Tooltip.getOrCreateInstance(element);
	});

	if (typeof update_speed_emoji_modal == 'function') {
		insertGhostDivs(e)
	}
}

function escapeHTML(unsafe) {
	return unsafe.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
}

function showmore(t) {
	div = t.parentElement.parentElement.parentElement

	let text = div.getElementsByTagName('d')[0]
	if (!text) text = div.getElementsByClassName('showmore-text')[0]
	if (!text) text = div.querySelector('div.d-none')

	text.classList.remove('d-none')
	t.remove()
}

function formatDate(d) {
	const options = {year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit', timeZoneName: 'short'};
	return d.toLocaleTimeString([], options)
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
	if (t.value) {
		t.dataset.oldvalue = t.value
		t.value = 'Are you sure?'
	}
	else {
		t.dataset.oldhtml = t.innerHTML
		t.innerHTML = t.innerHTML.replace(t.textContent, 'Are you sure?')
	}

	t.setAttribute("data-onclick", t.dataset.areyousure);

	if (t.dataset.dismiss)
		t.setAttribute("data-bs-dismiss", t.dataset.dismiss);

	t.classList.add('areyousure')
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

function reload() {
	location.reload();
}

function sendFormXHR(form, extraActionsOnSuccess) {
	const t = form.querySelector('[type="submit"]')
	t.disabled = true;
	t.classList.add("disabled");

	const xhr = new XMLHttpRequest();

	formData = new FormData(form);

	formData.append("formkey", formkey());
	actionPath = form.getAttribute("action");

	xhr.open("POST", actionPath);
	xhr.setRequestHeader('xhr', 'xhr');

	xhr.onload = function() {
		const success = xhr.status >= 200 && xhr.status < 300;

		if (!(extraActionsOnSuccess == reload && success)) {
			t.disabled = false;
			t.classList.remove("disabled");
		}

		if (xhr.status != 204) {
			const data = JSON.parse(xhr.response);
			showToast(success, getMessageFromJsonData(success, data));
		}
		if (success && extraActionsOnSuccess) extraActionsOnSuccess(xhr);
	};

	xhr.send(formData);
}

function sendFormXHRSwitch(form) {
	sendFormXHR(form,
		() => {
			form.nextElementSibling.classList.remove('d-none');
			const days = form.querySelector("input[name=days]")
			if (!days || !days.value)
				form.classList.add('d-none');
		}
	)
}

function sendFormXHRReload(form) {
	sendFormXHR(form, reload)
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
			if (/^[\d-,]+$/.test(attr)) {
				attr = parseInt(attr.replace(/,/g, ''))
			}
		} else if ('time' in x.dataset) {
			attr = parseInt(x.dataset.time);
		} else {
			attr = x.textContent
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

const is_pwa = window.matchMedia('(display-mode: standalone)')['matches'] || window.matchMedia('(display-mode: minimal-ui)')['matches']
if (is_pwa) {
	const links = document.querySelectorAll('a[data-target="t"]');
	for (const link of links) {
		link.removeAttribute("target");
	}
}

const gbrowser = document.getElementById('gbrowser').value
if (location.pathname != '/chat' && (gbrowser == 'iphone' || gbrowser == 'mac')) {
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

const screen_width = (innerWidth > 0) ? innerWidth : screen.width;
function focusSearchBar(element)
{
	if (screen_width >= 768) {
		element.focus();
		setTimeout(() => {
			element.focus();
		}, 200);
		setTimeout(() => {
			element.focus();
		}, 1000);
	}
}

let MINFLIES;
let MAXFLIES;
let ACTUALMAXFILES;

if (screen_width < 768) {
	MINFLIES = 5;
	MAXFLIES = 10;
	ACTUALMAXFILES = 50;
}
else {
	MINFLIES = 10;
	MAXFLIES = 20;
	ACTUALMAXFILES = 150;
}

function insertText(input, text) {
	const newPos = input.selectionStart + text.length;
	input.setRangeText(text);

	if (window.chrome !== undefined)
		setTimeout(function(){
			input.focus();
			for(let i = 0; i < 2; i++)
				input.setSelectionRange(newPos, newPos);

			input.focus();
			for(let i = 0; i < 2; i++)
				input.setSelectionRange(newPos, newPos);
		}, 1);
	else
		input.setSelectionRange(newPos, newPos);

	input.selectionStart = newPos;

	handle_disabled(input)
}



//FILE SHIT



let oldfiles = {};
let MAX_IMAGE_AUDIO_SIZE_MB
let MAX_IMAGE_AUDIO_SIZE_MB_PATRON
let MAX_VIDEO_SIZE_MB
let MAX_VIDEO_SIZE_MB_PATRON

if (document.getElementById("MAX_IMAGE_AUDIO_SIZE_MB")) {
	MAX_IMAGE_AUDIO_SIZE_MB = parseInt(document.getElementById("MAX_IMAGE_AUDIO_SIZE_MB").value)
	MAX_IMAGE_AUDIO_SIZE_MB_PATRON = parseInt(document.getElementById("MAX_IMAGE_AUDIO_SIZE_MB_PATRON").value)
	MAX_VIDEO_SIZE_MB = parseInt(document.getElementById("MAX_VIDEO_SIZE_MB").value)
	MAX_VIDEO_SIZE_MB_PATRON = parseInt(document.getElementById("MAX_VIDEO_SIZE_MB_PATRON").value)
}

let patron
if (location.host == 'rdrama.net') patron = 'paypig'
else patron = 'patron'

function handle_files(input, newfiles) {
	if (!newfiles) return;

	for (const file of newfiles) {
		if (file.type.startsWith('image/'))
			continue

		let max_size
		let max_size_patron
		let type

		if (file.type.startsWith('video/')) {
			max_size = MAX_VIDEO_SIZE_MB
			max_size_patron = MAX_VIDEO_SIZE_MB_PATRON
			type = 'video'
		}
		else {
			max_size = MAX_IMAGE_AUDIO_SIZE_MB
			max_size_patron = MAX_IMAGE_AUDIO_SIZE_MB_PATRON
			type = 'image/audio'
		}

		if (file.size > max_size * 1024 * 1024) {
			const msg = `Max ${type} size is ${max_size} MB (${max_size_patron} MB for ${patron}s)`
			showToast(false, msg);
			input.value = null;
			return
		}
	}

	const ta = input.parentElement.parentElement.parentElement.parentElement.querySelector('textarea.file-ta');

	if (!oldfiles[ta.id]) {
		oldfiles[ta.id] = new DataTransfer();
	}

	for (let file of newfiles) {
		if (file.name == 'image.png') {
			const blob = file.slice(0, file.size, 'image/png');
			const new_name = Math.random().toString(32).substring(2,10) + '.png'
			file = new File([blob], new_name, {type: 'image/png'});
		}
		oldfiles[ta.id].items.add(file);
		insertText(ta, `[${file.name}]`);
	}

	input.files = oldfiles[ta.id].files;

	if (input.files.length > 20)
	{
		window.alert("You can't upload more than 20 files at one time!")
		input.value = null
		oldfiles[ta.id] = new DataTransfer();
		return
	}

	markdown(ta)

	autoExpand(ta)

	if (typeof checkForRequired === "function")
		checkForRequired();
	if (typeof savetext === "function")
		savetext();
	if (typeof submit_save_files === "function") {
		const array = []
		for (const x of input.files) {
			array.push(x)
		}
		submit_save_files("textarea", array);
	}
}


file_upload = document.getElementById('file-upload');

if (file_upload) {
	function display_url_image() {
		if (file_upload.files)
		{
			const file = file_upload.files[0]
			file_upload.previousElementSibling.textContent = file.name.substr(0, 50);
			if (file.type.startsWith('image/')) {
				const fileReader = new FileReader();
				fileReader.readAsDataURL(file_upload.files[0]);
				fileReader.onload = function () {
					document.getElementById('image-preview').setAttribute('src', this.result);
					document.getElementById('image-preview').classList.remove('d-none');
					document.getElementById('image-preview').classList.add('mr-2');
				};
			}
			else {
				document.getElementById('image-preview').classList.add('d-none');
				document.getElementById('image-preview').classList.remove('mr-2');
			}

			if (typeof checkForRequired === "function") {
				document.getElementById('urlblock').classList.add('d-none');
				document.getElementById('remove-attachment').classList.remove('d-none');
				checkForRequired();
			}
			else {
				document.getElementById('submit-btn').disabled = false;
			}
		}
	}
	file_upload.onchange = () => {
		display_url_image()
		if (typeof submit_save_files === "function") {
			const array = []
			for (const x of file_upload.files) {
				array.push(x)
			}
			submit_save_files("attachment", array);
		}
	}

}

document.onpaste = function(event) {
	const files = structuredClone(event.clipboardData.files);
	if (!files.length) return

	const focused = document.activeElement;
	let input;

	if (file_upload) {
		if (location.pathname.endsWith('/submit') && focused && focused.id == 'post-text') {
			input = document.getElementById('file-upload-submit')
		}
		else {
			file_upload.files = files;
			display_url_image();
			if (typeof submit_save_files === "function") {
				const array = []
				for (const x of file_upload.files) {
					array.push(x)
				}
				submit_save_files("attachment", array);
			}
			return;
		}
	}
	else if (focused) {
		input = focused.parentElement.querySelector('input[type="file"]')
	}
	else {
		input = document.querySelector('input[type="file"]')
	}

	event.preventDefault();
	handle_files(input, files);
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

document.querySelectorAll('form').forEach(form => {
	form.addEventListener('submit', (e) => {
		if (form.classList.contains('is-submitting')) {
			e.preventDefault();
		}

		form.classList.add('is-submitting');
	});
});

function urlB64ToUint8Array(base64String) {
	const padding = '='.repeat((4 - base64String.length % 4) % 4);
	const base64 = (base64String + padding)
		.replace(/\-/g, '+')
		.replace(/_/g, '/');

	const rawData = window.atob(base64);
	const outputArray = new Uint8Array(rawData.length);

	for (let i = 0; i < rawData.length; ++i) {
		outputArray[i] = rawData.charCodeAt(i);
	}
	return outputArray;
}

function updateSubscriptionOnServer(subscription, apiEndpoint) {
	const formData = new FormData();
	formData.append("subscription_json", JSON.stringify(subscription));

	const xhr = createXhrWithFormKey(
		apiEndpoint,
		formData
	);

	xhr[0].send(xhr[1]);
}

function enablePushNotifications() {
	if (!('serviceWorker' in navigator && 'PushManager' in window)) return;
	let publicKeyElement = document.getElementById('VAPID_PUBLIC_KEY');
	if (!publicKeyElement) return;

	let publicKey = urlB64ToUint8Array(publicKeyElement.value);
	navigator.serviceWorker.getRegistration("/assets/js/service_worker.js").then((reg) => {
		return reg.pushManager.subscribe({
			userVisibleOnly: true,
			applicationServerKey: publicKey,
		})
	}).then((subscription) => {
		updateSubscriptionOnServer(subscription, "/push_subscribe")
		window.alert("Push notifications are enabled!")
	}).catch((e) => {
		window.alert("Please give the site access to notifications!")
		console.error(e)
	})
}

const body = document.getElementsByTagName('body')[0]
addEventListener('hashchange', () => {
	if (location.hash.startsWith("#m-"))
		body.classList.add('modal-open')
	else
		body.classList.remove('modal-open')
})

if (location.hash.startsWith("#m-")) {
	history.replaceState({}, '', location.href.split('#')[0])
}
