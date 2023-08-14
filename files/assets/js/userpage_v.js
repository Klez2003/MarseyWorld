function toggleElement(id, id2) {
	for(let el of document.getElementsByClassName('toggleable')) {
		if (el.id != id) {
			el.classList.add('d-none');
		}
	}

	document.getElementById(id).classList.toggle('d-none');
	document.getElementById(id2).focus()
}

let TRANSFER_TAX = document.getElementById('tax').innerHTML

function updateTax(mobile=false) {
	let suf = mobile ? "-mobile" : "";
	let amount = parseInt(document.getElementById("coin-transfer-amount" + suf).value);
	if (amount > 0) document.getElementById("coins-transfer-taxed" + suf).textContent = amount - Math.ceil(amount*TRANSFER_TAX);
}

function updateBux(mobile=false) {
	let suf = mobile ? "-mobile" : "";
	let amount = parseInt(document.getElementById("bux-transfer-amount" + suf).value);
	if (amount > 0) document.getElementById("bux-transfer-taxed" + suf).textContent = amount;
}

function transferCoins(t, mobile=false) {

	for(let el of document.getElementsByClassName('toggleable')) {
		el.classList.add('d-none');
	}

	let amount = parseInt(document.getElementById(mobile ? "coin-transfer-amount-mobile" : "coin-transfer-amount").value);
	let transferred = amount - Math.ceil(amount*TRANSFER_TAX);
	let username = document.getElementById('username').innerHTML;

	postToast(t, `/@${username}/transfer_coins`,
		{
		"amount": document.getElementById(mobile ? "coin-transfer-amount-mobile" : "coin-transfer-amount").value,
		"reason": document.getElementById(mobile ? "coin-transfer-reason-mobile" : "coin-transfer-reason").value
		},
		() => {
			document.getElementById("user-coins-amount").textContent = parseInt(document.getElementById("user-coins-amount").textContent) - amount;
			document.getElementById("profile-coins-amount-mobile").textContent = parseInt(document.getElementById("profile-coins-amount-mobile").textContent) + transferred;
			document.getElementById("profile-coins-amount").textContent = parseInt(document.getElementById("profile-coins-amount").textContent) + transferred;
		}
	);
}

function transferBux(t, mobile=false) {
	for(let el of document.getElementsByClassName('toggleable')) {
		el.classList.add('d-none');
	}

	let amount = parseInt(document.getElementById(mobile ? "bux-transfer-amount-mobile" : "bux-transfer-amount").value);
	let username = document.getElementById('username').innerHTML

	postToast(t, `/@${username}/transfer_bux`,
		{
		"amount": document.getElementById(mobile ? "bux-transfer-amount-mobile" : "bux-transfer-amount").value,
		"reason": document.getElementById(mobile ? "bux-transfer-reason-mobile" : "bux-transfer-reason").value
		},
		() => {
			document.getElementById("user-bux-amount").textContent = parseInt(document.getElementById("user-bux-amount").textContent) - amount;
			document.getElementById("profile-bux-amount-mobile").textContent = parseInt(document.getElementById("profile-bux-amount-mobile").textContent) + amount;
			document.getElementById("profile-bux-amount").textContent = parseInt(document.getElementById("profile-bux-amount").textContent) + amount;
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
