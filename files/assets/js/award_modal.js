// TODO: Refactor this ugly shit who wrote this lmao
function vote(type, id, dir) {
	const upvotes = document.getElementsByClassName(type + '-' + id + '-up');
	const downvotes = document.getElementsByClassName(type + '-' + id + '-down');
	const scoretexts = document.getElementsByClassName(type + '-score-' + id);

	for (let i=0; i<upvotes.length; i++) {

		const upvote = upvotes[i]
		const downvote = downvotes[i]
		const scoretext = scoretexts[i]
		const score = Number(scoretext.textContent);

		if (dir == "1") {
			if (upvote.classList.contains('active')) {
				upvote.classList.remove('active')
				upvote.classList.remove('active-anim')
				scoretext.textContent = score - 1
				votedirection = "0"
			} else if (downvote.classList.contains('active')) {
				upvote.classList.add('active')
				upvote.classList.add('active-anim')
				downvote.classList.remove('active')
				downvote.classList.remove('active-anim')
				scoretext.textContent = score + 2
				votedirection = "1"
			} else {
				upvote.classList.add('active')
				upvote.classList.add('active-anim')
				scoretext.textContent = score + 1
				votedirection = "1"
			}

			if (upvote.classList.contains('active')) {
				scoretext.classList.add('score-up')
				scoretext.classList.add('score-up-anim')
				scoretext.classList.remove('score-down')
				scoretext.classList.remove('score')
			} else if (downvote.classList.contains('active')) {
				scoretext.classList.add('score-down')
				scoretext.classList.remove('score-up')
				scoretext.classList.remove('score-up-anim');
				scoretext.classList.remove('score')
			} else {
				scoretext.classList.add('score')
				scoretext.classList.remove('score-up')
				scoretext.classList.remove('score-up-anim');
				scoretext.classList.remove('score-down')
			}
		}
		else {
			if (downvote.classList.contains('active')) {
				downvote.classList.remove('active')
				downvote.classList.remove('active-anim')
				scoretext.textContent = score + 1
				votedirection = "0"
			} else if (upvote.classList.contains('active')) {
				downvote.classList.add('active')
				downvote.classList.add('active-anim')
				upvote.classList.remove('active')
				upvote.classList.remove('active-anim')
				scoretext.textContent = score - 2
				votedirection = "-1"
			} else {
				downvote.classList.add('active')
				downvote.classList.add('active-anim')
				scoretext.textContent = score - 1
				votedirection = "-1"
			}

			if (upvote.classList.contains('active')) {
				scoretext.classList.add('score-up')
				scoretext.classList.add('score-up-anim')
				scoretext.classList.remove('score-down')
				scoretext.classList.remove('score')
			} else if (downvote.classList.contains('active')) {
				scoretext.classList.add('score-down')
				scoretext.classList.remove('score-up-anim')
				scoretext.classList.remove('score-up')
				scoretext.classList.remove('score')
			} else {
				scoretext.classList.add('score')
				scoretext.classList.remove('score-up')
				scoretext.classList.remove('score-down')
				scoretext.classList.remove('score-up-anim')
			}
		}
	}

	const xhr = createXhrWithFormKey("/vote/" + type.replace('-mobile','') + "/" + id + "/" + votedirection);
	xhr[0].send(xhr[1]);
}

let global_price;

function pick(kind, price, coins, marseybux) {
	global_price = price;

	price = parseInt(price)
	coins = parseInt(coins)
	marseybux = parseInt(marseybux)

	const buy = document.getElementById('buy')

	if (kind == "grass" && coins < price)
		buy.disabled = true;
	else if (kind == "benefactor" && marseybux < price)
		buy.disabled = true;
	else if (coins+marseybux < price)
		buy.disabled = true;
	else
		buy.disabled = false;

	let ownednum = Number(document.getElementById(`${kind}-owned`).textContent);
	document.getElementById('giveaward').disabled = (ownednum == 0);
	document.getElementById('kind').value=kind;
	if (document.getElementsByClassName('picked').length > 0) {
		document.getElementsByClassName('picked')[0].classList.toggle('picked');
	}
	document.getElementById(kind).classList.toggle('picked')

	if (kind == "agendaposter") {
		document.getElementById('phrase_section').classList.remove("d-none")
		document.getElementById('note_section').classList.add("d-none")
	}
	else {
		document.getElementById('phrase_section').classList.add("d-none")
		document.getElementById('note_section').classList.remove("d-none")
	}

	if (kind == "flairlock") {
		document.getElementById('notelabel').innerHTML = "New flair:";
		document.getElementById('note').placeholder = "Insert new flair here, or leave empty to add 1 day to the duration of the current flair. 100 characters max.";
		document.getElementById('note').maxLength = 100;
	}
	else {
		document.getElementById('notelabel').innerHTML = "Note (optional):";
		document.getElementById('note').placeholder = "Note to include in award notification";
		document.getElementById('note').maxLength = 200;
	}

	document.getElementById('award_price_block').classList.remove('d-none');
	document.getElementById('award_price').textContent = price;
}

function buy() {
	const kind = document.getElementById('kind').value;
	url = `/buy/${kind}`
	const xhr = createXhrWithFormKey(url);
	xhr[0].onload = function() {
		let data
		try {data = JSON.parse(xhr[0].response)}
		catch(e) {console.error(e)}
		success = xhr[0].status >= 200 && xhr[0].status < 300;
		showToast(success, getMessageFromJsonData(success, data), true);
		if (success) {
			if (kind != "lootbox")
			{
				document.getElementById('giveaward').disabled=false;
				let owned = document.getElementById(`${kind}-owned`)
				let ownednum = Number(owned.textContent) + 1;
				owned.textContent = ownednum
			}
		}
	};

	xhr[0].send(xhr[1]);

}

function giveaward(t) {
	const kind = document.getElementById('kind').value;

	const note_id = (kind == "agendaposter" ? "agendaposter_phrase" : "note")

	postToast(t, t.dataset.action,
		{
			"kind": kind,
			"note": document.getElementById(note_id).value
		},
		() => {
			let owned = document.getElementById(`${kind}-owned`)
			let ownednum = Number(owned.textContent) - 1;
			owned.textContent = ownednum
			if (ownednum == 0)
				document.getElementById('giveaward').disabled=true;
		}
	);
}

const awardtabs = document.getElementsByClassName('award-tab');
const awardsections = document.getElementsByClassName('award-section');

function switchAwardTab() {
	for (const element of awardtabs)
		element.classList.toggle('active')
	for (const element of awardsections)
		element.classList.toggle('d-none')
}
