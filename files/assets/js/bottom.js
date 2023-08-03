
function execute(element, attr) {
	if (element.dataset.nonce != nonce) {
		console.error("Nonce check failed!")
		return
	}
	const funcs = element.getAttribute(`data-${attr}`).split(';')
	for (const func of funcs) {
		if (func) {
			const split = func.split('(')
			const name = split[0]
			const args = split[1].replace(/[')]/g, "").split(',').map(a => a.trim());
			if (args[0] == 'this') args[0] = element
			try {
				window[name](...args);
			}
			catch (e) {
				console.error(e)
				console.error(name)
			}
		}
	}
}

const onsubmit = document.querySelectorAll('[data-onsubmit]');
for (const element of onsubmit) {
	element.addEventListener('submit', (event)=>{
		event.preventDefault();
		execute(element, 'onsubmit')
	});
}

const onfocus = document.querySelectorAll('[data-onfocus]');
for (const element of onfocus) {
	element.addEventListener('focus', () => {execute(element, 'onfocus')});
}

const onclick_submit = document.querySelectorAll('[onclick_submit]');
for (const element of onclick_submit) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.addEventListener('click', () => {element.form.submit()});
}

const onchange_submit = document.querySelectorAll('[onchange_submit]');
for (const element of onchange_submit) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.addEventListener('change', () => {element.form.submit()});
}

const undisable_element = document.querySelectorAll('[data-undisable_element]');
for (const element of undisable_element) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.addEventListener('input', () => {
		document.getElementById(element.dataset.undisable_element).disabled = false;
	});
}

const setting_switchs = document.getElementsByClassName('setting_switch');
for (const element of setting_switchs) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.addEventListener('change', () => {
		postToastSwitch(element,`/settings/personal?${element.name}=${element.checked}`);
	});
}

const setting_selects = document.getElementsByClassName('setting_select');
for (const element of setting_selects) {
	if (element.dataset.nonce != nonce) {
		console.log("Nonce check failed!")
		continue
	}
	element.addEventListener('change', () => {
		if (element.id == "changing-house") {
			if (confirm('Are you sure you want to change houses?')) {
				postToastReload(element,`/settings/personal?${element.name}=${element.value}`);
			}
		}
		else if (element.dataset.reload)
			postToastReload(element,`/settings/personal?${element.name}=${element.value}`);
		else
			postToast(element,`/settings/personal?${element.name}=${element.value}`);
	});
}

const TH = document.getElementsByTagName('th')
for (const element of TH) {
	if (element.classList.contains("disable-sort-click"))
		continue;

	element.addEventListener('click', () => {sort_table(element)});
}

const btns_to_disable = document.querySelectorAll('[type="submit"]')
for (const element of btns_to_disable) {
	if (!element.classList.contains("donotdisable"))
		element.addEventListener('click', () => {disable_btn(element)})
}

function disable_btn(t) {
	if (!t.classList.contains('disabled')) {
		const isShopConfirm = t.id.startsWith('buy-') || t.id.startsWith('giveaward')

		if (!isShopConfirm) {
			t.classList.add('disabled');

			setTimeout(() => {
				t.disabled = true;
			}, 0.1);

			setTimeout(() => {
				t.classList.remove("disabled");
				t.disabled = false;
			}, 2000);	
		}
	}
}

function register_new_elements(e) {
	const oninput = e.querySelectorAll('[data-oninput]');
	for (const element of oninput) {
		element.oninput = () => {execute(element, 'oninput')};
	}

	const onmouseover = e.querySelectorAll('[data-onmouseover]');
	for (const element of onmouseover) {
		element.onmouseover = () => {execute(element, 'onmouseover')};
	}

	const onchange = e.querySelectorAll('[data-onchange]');
	for (const element of onchange) {
		element.onchange = () => {execute(element, 'onchange')};
	}

	const file_inputs = document.querySelectorAll('input[multiple="multiple"]')
	for (const input of file_inputs) {
		input.onchange = () => {handle_files(input, input.files)};
	}

	const onclick = e.querySelectorAll('[data-onclick]');
	for (const element of onclick) {
		element.onclick = () => {execute(element, 'onclick')};
	}

	const textareas = e.getElementsByTagName('textarea')
	for (const element of textareas) {
		autoExpand(element)
		element.addEventListener('input', () => {
			autoExpand(element)
		});
	}

	const popover_triggers = document.getElementsByClassName('user-name');
	for (const element of popover_triggers) {
		element.onclick = (e) => {
			if (!(e.ctrlKey || e.metaKey || e.shiftKey || e.altKey))
				e.preventDefault();
		};
	}
}

register_new_elements(document);
bs_trigger(document);


document.addEventListener("click", function (e) {
	let element = e.target
	if (element.tagName == "I")
		element = element.parentElement

	if (!element) return

	if (element instanceof HTMLImageElement && (element.alt.startsWith('![](') || element.classList.contains('in-comment-image') || element.classList.contains('img'))) {
		expandImage()
	}
	else if (element.classList.contains('showmore')) {
		showmore(element)
	}
	else if (element.dataset.url) {
		if (element.dataset.nonce != nonce) {
			console.log("Nonce check failed!")
			return
		}
		document.getElementById('giveaward').dataset.action = element.dataset.url
	}


	if (element.dataset.toggleelement) {
		if (element.dataset.toggleelement.startsWith('#reply-'))
			close_inline_speed_emoji_modal();

		const toggling = document.querySelector(element.dataset.toggleelement)
		const attr = element.dataset.toggleattr;

		toggling.classList.toggle(attr);
	}

	if (!element.classList.contains("areyousure")) {
		document.querySelectorAll(".areyousure").forEach(i => {
			i.classList.remove("areyousure")

			if (i.dataset.oldvalue)
				i.value = i.dataset.oldvalue
			else
				i.innerHTML = i.dataset.oldhtml

			i.setAttribute("data-onclick", "areyousure(this)");

			if (i.dataset.dismiss)
				i.removeAttribute("data-bs-dismiss")
		});
	}
});

const inputs = document.querySelectorAll('input[type="number"]')
for (const input of inputs) {
	input.onkeyup = () => {
		if (parseInt(input.value) > parseInt(input.max)) input.value = input.max;
	};
}

if (!('serviceWorker' in navigator && 'PushManager' in window) || (gbrowser == 'iphone' && !is_pwa)) {
	let e = document.getElementById("enable-push-nav-item");
	if (e) {
		e.classList.add('d-none')
	}
	e = document.getElementById("enable-push-nav-item-mobile");
	if (e) {
		e.classList.add('d-none')
	}
}

if (gbrowser == 'iphone' && !is_pwa) {
	const e = document.getElementById("enable-push-nav-item-iphone");
	if (e) {
		e.classList.remove('d-none')
	}
}

if (is_pwa) {
	const e = document.getElementById("mobile-app-nav-item");
	e.remove();
}
