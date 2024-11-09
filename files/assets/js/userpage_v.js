let TRANSFER_TAX = document.getElementById('tax').innerHTML

function updateTax(mobile=false) {
	let suf = mobile ? "-mobile" : "";
	let amount = parseInt(document.getElementById("coin-transfer-amount" + suf).value);
	if (amount > 0) document.getElementById("coins-transfer-taxed" + suf).textContent = commas(amount - Math.ceil(amount*TRANSFER_TAX));
}

function updateBux(mobile=false) {
	let suf = mobile ? "-mobile" : "";
	let amount = parseInt(document.getElementById("bux-transfer-amount" + suf).value);
	if (amount > 0) document.getElementById("bux-transfer-taxed" + suf).textContent = commas(amount);
}

function change_currency(id, amount) {
	const el = document.getElementById(id)
	el.textContent = commas(parseInt(el.textContent.replaceAll(',', '')) + amount);
}

function transferCoins(t, mobile=false) {
	close_inline_emoji_modal();

	for (let el of document.getElementsByClassName('toggleable')) {
		el.classList.add('d-none');
	}

	let amount = parseInt(document.getElementById(mobile ? "coin-transfer-amount-mobile" : "coin-transfer-amount").value);
	let username = document.getElementById('username').innerHTML;

	postToast(t, `/@${username}/transfer_coins`,
		{
		"amount": document.getElementById(mobile ? "coin-transfer-amount-mobile" : "coin-transfer-amount").value,
		"reason": document.getElementById(mobile ? "coin-transfer-reason-mobile" : "coin-transfer-reason").value
		},
		() => {
			change_currency("user-coins-amount", -amount)
			change_currency("user-coins-amount-mobile", -amount)
			change_currency("profile-coins-amount", amount)
			change_currency("profile-coins-amount-mobile", amount)
		}
	);
}

function transferBux(t, mobile=false) {
	close_inline_emoji_modal();

	for (let el of document.getElementsByClassName('toggleable')) {
		el.classList.add('d-none');
	}

	let amount = parseInt(document.getElementById(mobile ? "bux-transfer-amount-mobile" : "bux-transfer-amount").value);
	let username = document.getElementById('username').innerHTML

	postToast(t, `/@${username}/transfer_marseybux`,
		{
		"amount": document.getElementById(mobile ? "bux-transfer-amount-mobile" : "bux-transfer-amount").value,
		"reason": document.getElementById(mobile ? "bux-transfer-reason-mobile" : "bux-transfer-reason").value
		},
		() => {
			change_currency("user-bux-amount", -amount)
			change_currency("user-bux-amount-mobile", -amount)
			change_currency("profile-bux-amount", amount)
			change_currency("profile-bux-amount-mobile", amount)
		}
	);
}

function sendMessage(form) {
	document.getElementById('message').classList.add('d-none');
	document.getElementById('message-mobile').classList.add('d-none');
	document.getElementById('message-preview').classList.add('d-none');
	document.getElementById('message-preview-mobile').classList.add('d-none');
	sendFormXHR(form,
		() => {
			for (const substr of ['', '-mobile']) {
				const ta = document.getElementById(`input-message${substr}`);
				ta.value = '';
				const input = ta.parentElement.querySelector('input[type="file"]');
				input.previousElementSibling.innerHTML = '';
				input.value = null;
				oldfiles[ta.id] = new DataTransfer();
			}
		}
	)
}
