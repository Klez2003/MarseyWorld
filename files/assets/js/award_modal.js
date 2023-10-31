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

const note_section = document.getElementById('note_section')
const gif_button = note_section.querySelector('[title="Add GIF"]')
const giveaward_button = document.getElementById('giveaward')

function pick(kind, price, coins, marseybux) {
	global_price = price;

	price = parseInt(price)
	coins = parseInt(coins)
	marseybux = parseInt(marseybux)

	document.getElementById('kind').value=kind;
	if (document.getElementsByClassName('picked').length > 0) {
		document.getElementsByClassName('picked')[0].classList.toggle('picked');
	}
	document.getElementById(kind).classList.toggle('picked')

	if (kind == "chud") {
		document.getElementById('phrase_section').classList.remove("d-none")
		note_section.classList.add("d-none")
	}
	else {
		document.getElementById('phrase_section').classList.add("d-none")
		note_section.classList.remove("d-none")
	}

	if (kind == "emoji") {
		if (giveaward_button.dataset.action.startsWith('/award/post/'))
			document.getElementById('emoji_behavior_section').classList.remove("d-none")
		document.getElementById('note').setAttribute("style", "min-height:35px;max-height:35px;height:35px;min-width:min(300px,80vw)")
		gif_button.classList.add('d-none')
	}
	else {
		document.getElementById('emoji_behavior_section').classList.add("d-none")
		document.getElementById('note').removeAttribute("style")
		gif_button.classList.remove('d-none')
	}

	if (kind == "flairlock") {
		document.getElementById('notelabel').innerHTML = "New flair:";
		document.getElementById('note').placeholder = "Insert new flair here, or leave empty to add 1 day to the duration of the current flair.";
		document.getElementById('note').maxLength = 100;
	}
	else if (kind == "namelock") {
		document.getElementById('notelabel').innerHTML = "New username:";
		document.getElementById('note').placeholder = "Insert new username here, or leave empty to add 1 day to the duration of the current username.";
		document.getElementById('note').maxLength = 25;
	}
	else if (kind == "emoji") {
		document.getElementById('notelabel').innerHTML = "Emoji name:";
		document.getElementById('note').placeholder = "Insert one site emoji here.";
		document.getElementById('note').maxLength = 33;
	}
	else {
		document.getElementById('notelabel').innerHTML = "Note (optional):";
		document.getElementById('note').placeholder = "Note to include in award notification";
		document.getElementById('note').maxLength = 200;
	}

	const ownednum = Number(document.getElementById(`${kind}-owned`).textContent);

	if (ownednum > 0) {
		document.getElementById('award_price').textContent = `${ownednum} owned`;
		giveaward_button.classList.remove('d-none');
		document.getElementById('buyandgiveaward').classList.add('d-none');
	}
	else {
		document.getElementById('award_price').textContent = `Price: ${price} coins/marseybux`;
		giveaward_button.classList.add('d-none');
		document.getElementById('buyandgiveaward').classList.remove('d-none');
	}
}

function giveaward(t) {
	const kind = document.getElementById('kind').value;

	const note_id = (kind == "chud" ? "chud_phrase" : "note")

	postToast(t, t.dataset.action,
		{
			"kind": kind,
			"note": document.getElementById(note_id).value,
			"emoji_behavior": document.getElementById("emoji_behavior").value
		},
		() => {
			let owned = document.getElementById(`${kind}-owned`)
			let ownednum = Number(owned.textContent) - 1;
			owned.textContent = ownednum

			let ownedblock = document.getElementById(`${kind}-owned-block`)
			if (ownednum > 0) {
				ownedblock.textContent = `${ownednum} owned`;
				document.getElementById('award_price').textContent = `${ownednum} owned`;
			}
			else {
				ownedblock.textContent = `Price: ${global_price}`
				document.getElementById('award_price').textContent = `Price: ${global_price} coins/marseybux`;
			}
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
