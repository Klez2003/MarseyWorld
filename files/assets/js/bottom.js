
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
		if (element.dataset.reload)
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

function disable_btn(t) {
	if (!t.classList.contains('disabled')) {
		t.classList.add('disabled');

		setTimeout(() => {
			t.disabled = true;
		}, 0.0000000000000000001);
	
		setTimeout(() => {
			t.classList.remove("disabled");
			t.disabled = false;
		}, 2000);
	}
}

function register_new_elements(e) {
	const showmores = document.getElementsByClassName('showmore')
	for (const element of showmores) {
		element.onclick = () => {showmore(element)};
	}

	const onclick = e.querySelectorAll('[data-onclick]');
	for (const element of onclick) {
		element.onclick = () => {
			execute(element, 'onclick')
		};
	}

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

	const popover_triggers = document.getElementsByClassName('user-name');
	for (const element of popover_triggers) {
		element.onclick = (e) => {
			if (!(e.ctrlKey || e.metaKey || e.shiftKey || e.altKey))
				e.preventDefault();
		};
	}

	const expandable = document.querySelectorAll('.in-comment-image, img[alt^="![]("]');
	for (const element of expandable) {
		element.onclick = () => {expandImage()};
	}

	const toggleelement = e.querySelectorAll('[data-toggleelement]');
	for (const element of toggleelement) {
		element.addEventListener('click', () => {
			document.getElementById(element.dataset.toggleelement).classList.toggle(element.dataset.toggleattr);
		});
	}

	const file_inputs = document.querySelectorAll('input[multiple="multiple"]')
	for (const input of file_inputs) {
		input.onchange = () => {handle_files(input, input.files)};
	}

	const remove_files = document.querySelectorAll('button.remove-files')
	for (const element of remove_files) {
		element.onclick = () => {cancel_files(element)};
	}

	const data_url = document.querySelectorAll('[data-url]');
	for (const element of data_url) {
		if (element.dataset.nonce != nonce) {
			console.log("Nonce check failed!")
			continue
		}
		element.addEventListener('click', () => {
			document.getElementById('giveaward').dataset.action = element.dataset.url
		});
	}

	const btns_to_disable = document.querySelectorAll('[type="submit"]')
	for (const btn of btns_to_disable) {
		btn.addEventListener('click', () => {disable_btn(btn)})
	}
}

register_new_elements(document);
bs_trigger(document);
