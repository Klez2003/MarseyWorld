function makeBlackjackRequest(action, split = false) {
	const xhr = new XMLHttpRequest();
	xhr.open("post", `/casino/twentyone/${action}?hand=${split ? 'split' : 'player'}`);
	xhr.setRequestHeader('xhr', 'xhr');
	xhr.onload = handleBlackjackResponse.bind(null, xhr);
	xhr.blackjackAction = action;
	return xhr;
}

function handleBlackjackResponse(xhr) {
	let status;
	try {
		const response = JSON.parse(xhr.response);
		const succeeded = xhr.status >= 200 &&
			xhr.status < 300 &&
			response &&
			!response.details;

		clearResult();
		status = xhr.status;

		if (status == 429) {
			throw new Error(response["details"]);
		}

		if (succeeded) {
			updateBlackjackTable(response.state);
			updateFeed(response.feed);
			updatePlayerCurrencies(response.gambler);
		} else {
			console.error("Error: ", response.details);
			throw new Error("Error")
		}
	} catch (error) {
		const results = {
			deal: "Unable to deal a new hand. Is one in progress?",
			hit: "Unable to hit.",
			stay: "Unable to stay.",
			"double-down": "Unable to double down.",
			"buy-insurance": "Unable to buy insurance.",
			"split": "Unable to split"
		};
		result = results[xhr.blackjackAction];

		if (status == 429) {
			result = error.message;
		}

		updateResult(result, "danger");
	}
}

function updateBlackjackActions(state) {
	const actions = Array.from(document.querySelectorAll('.twentyone-btn'));
	document.getElementById(`twentyone-SPLIT_ACTIONS`).style.display = 'none'

	// Hide all actions.
	actions.forEach(action => action.style.display = 'none');

	if (state) {
		if(state.actions.some((action) => action === 'HIT_SPLIT')) state.actions.push('SPLIT_ACTIONS');

		// Show the correct ones.
		state.actions.forEach(action => document.getElementById(`twentyone-${action}`).style.display = 'inline-block');
	} else {
		const dealButton = document.getElementById(`twentyone-DEAL`);

		if (dealButton) {
			dealButton.style.display = 'inline-block'
		}
	}
}

function updateBlackjackTable(state) {
	const table = document.getElementById('blackjack-table');
	const charactersToRanks = {
		X: "10"
	};
	const charactersToSuits = {
		S: "♠️",
		H: "♥️",
		C: "♣️",
		D: "♦️",
	};
	const makeCardset = (from, who, value) => `
		<div class="blackjack-cardset">
			<div class="blackjack-cardset-value">
				${value === -1 ? `${who} went bust` : `${who} has ${value}`}
			</div>
			${from
			.filter(card => card !== "?")
			.map(([rankCharacter, suitCharacter]) => {
				const rank = charactersToRanks[rankCharacter] || rankCharacter;
				const suit = charactersToSuits[suitCharacter] || suitCharacter;
				return buildPlayingCard(rank, suit);
			})
			.join('')}
		</div>
	`;
	const dealerCards = makeCardset(state.dealer, 'Dealer', state.dealer_value);
	const playerCards = makeCardset(state.player, 'Player', state.player_value);
	const playerSplitCards = state.has_player_split ? makeCardset(state.player_split, 'Player', state.player_split_value) : '';

	updateBlackjackActions(state);

	table.innerHTML = `
		<div style="position: relative;">
			${dealerCards}
		</div>
		${playerCards}
		${playerSplitCards}
	`;

	const currency = state.wager.currency === 'coins' ? 'coins' : 'marseybux';

	const gameCompleted = ['BLACKJACK', 'WON', 'PUSHED', 'LOST'].indexOf(state.status) !== -1 && (!state.has_player_split || ['WON', 'PUSHED', 'LOST'].indexOf(state.status_split) !== -1);
 
	if(gameCompleted) {
		switch (state.status) {
			case 'BLACKJACK':
				updateResult(`Blackjack: Received ${state.payout} ${currency}`, "warning");
				break;
			case 'WON':
				if(state.status_split === 'LOST') {
					updateResult(`Won and Lost: Received 0 ${currency}`, "success");
				}
				else if(state.status_split === 'PUSHED') {
					updateResult(`Won and PUSHED: Received ${state.payout} ${currency}`, "success");
				}
				else {
					updateResult(`Won: Received ${state.payout} ${currency}`, "success");
				}
				break;
			case 'PUSHED':
				if(state.status_split === 'WON') {
					updateResult(`Won and PUSHED: Received ${state.payout} ${currency}`, "success");
				}
				else if(state.status_split === 'LOST') {
					updateResult(`Lost and Pushed: Lost ${state.wager.amount} ${currency}`, "danger");
				}
				else {
					updateResult(`Pushed: Received ${state.wager.amount} ${currency}`, "success");
				}
				
				break;
			case 'LOST':
				if(state.status_split === 'WON') {
					updateResult(`Won and Lost: Received 0 ${currency}`, "success");
				}
				else if(state.status_split === 'PUSHED') {
					updateResult(`Lost and Pushed: Lost ${state.wager.amount} ${currency}`, "danger");
				}
				else {
					let lost = state.wager.amount;
					if (state.player_doubled_down || state.has_player_split) {
						lost *= 2;
					}
					updateResult(`Lost ${lost} ${currency}`, "danger");
				}
				
				break;
			default:
				break;
		}

		updateCardsetBackgrounds(state, true);
	}
	else {
		updateCardsetBackgrounds(state);
	}


	if (state.status === 'PLAYING' || (state.has_player_split && state.status_split === 'PLAYING')) {
		updateResult(`${state.has_player_split ? state.wager.amount * 2 : state.wager.amount} ${currency} are at stake`, "success");
	} else {
		enableWager();
	}
}

function updateCardsetBackgrounds(state, complete = false) {
	const cardsets = Array.from(document.querySelectorAll('.blackjack-cardset'));

	for (const cardset of cardsets) {
		['PLAYING', 'LOST', 'PUSHED', 'WON', 'BLACKJACK'].forEach(status => cardset.classList.remove(`blackjack-cardset__${status}`));
	}
	if(complete){
		const wager = state.has_player_split ? state?.wager?.amount * 2 : state?.wager?.amount;
		let dealerShows = state.payout > wager ? 'WON': 'LOST';
		if(state.payout === wager) dealerShows = 'PUSHED'
		cardsets[0]?.classList.add(`blackjack-cardset__${dealerShows}`)
	}
	else {
		cardsets[0]?.classList.add(`blackjack-cardset__PLAYING`)
	}
	cardsets[1]?.classList.add(`blackjack-cardset__${state.status}`)
	cardsets[2]?.classList.add(`blackjack-cardset__${state.status_split}`)
}

function deal() {
	const request = makeBlackjackRequest('deal');
	const { amount, currency } = getWager();
	const form = new FormData();

	form.append("formkey", formkey());
	form.append("wager", amount);
	form.append("currency", currency);

	request.send(form);

	clearResult();
	disableWager();
	drawFromDeck();
}

function hit(split = false) {
	const request = makeBlackjackRequest('hit', split);
	const form = new FormData();
	form.append("formkey", formkey());
	request.send(form);

	drawFromDeck();
}

function hitSplit() {
	hit(true);
}

function stay(split = false) {
	const request = makeBlackjackRequest('stay', split);
	const form = new FormData();
	form.append("formkey", formkey());
	request.send(form);
}

function staySplit() {
	stay(true);
}

function doubleDown() {
	const request = makeBlackjackRequest('double-down');
	const form = new FormData();
	form.append("formkey", formkey());
	request.send(form);

	drawFromDeck();
}

function buyInsurance() {
	const request = makeBlackjackRequest('buy-insurance');
	const form = new FormData();
	form.append("formkey", formkey());
	request.send(form);
}

function split() {
	const request = makeBlackjackRequest('split');
	const form = new FormData();
	form.append("formkey", formkey());
	request.send(form);
}

function buildBlackjackDeck() {
	document.getElementById('blackjack-table-deck').innerHTML = `
		<div style="position: absolute; top: 150px; left: -100px;">
			${buildPlayingCardDeck()}
		</div>
	`;
}

function initializeBlackjack() {
	buildBlackjackDeck();

	try {
		const passed = document.getElementById('blackjack-table').dataset.state;
		const state = JSON.parse(passed);
		updateBlackjackTable(state);
	} catch (error) {
		updateBlackjackActions();
	}
}

initializeBlackjack();
