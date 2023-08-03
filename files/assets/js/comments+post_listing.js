function pinned_timestamp(id) {
	const el = document.getElementById(id)
	const pintooltip = el.getAttribute("data-bs-original-title")
	if (!pintooltip.includes('until'))
		{
			const time = formatDate(new Date(parseInt(el.dataset.timestamp)*1000))
			el.setAttribute("data-bs-original-title", `${pintooltip} until ${time}`)
		}
}

function post(url) {
	const xhr = createXhrWithFormKey(url);
	xhr[0].send(xhr[1]);
};

function option_vote_0(oid, parentid, kind) {
	for(let el of document.getElementsByClassName('presult-'+parentid)) {
		el.classList.remove('d-none');
	}
	const full_oid = kind + '-' + oid
	const type = document.getElementById(full_oid).checked;
	const scoretext = document.getElementById('score-' + full_oid);
	const score = Number(scoretext.textContent);
	if (type == true) scoretext.textContent = score + 1;
	else scoretext.textContent = score - 1;
	post(`/vote/${kind}/option/${oid}`);
}

function option_vote_1(oid, parentid, kind) {
	for(let el of document.getElementsByClassName('presult-'+parentid)) {
		el.classList.remove('d-none');
	}
	const full_oid = kind + '-' + oid
	let curr = document.getElementById(`current-${kind}-${parentid}`)
	if (curr && curr.value)
	{
		const scoretext = document.getElementById('score-' + curr.value);
		const score = Number(scoretext.textContent);
		scoretext.textContent = score - 1;
	}

	const scoretext = document.getElementById('score-' + full_oid);

	const score = Number(scoretext.textContent);
	scoretext.textContent = score + 1;
	post(`/vote/${kind}/option/${oid}`);
	curr.value = full_oid
}

function option_vote_2(t, oid, kind) {
	postToast(t, `/vote/${kind}/option/${oid}`,
		{
		},
		() => {
			t.disabled = true;
			const parent = t.parentElement.parentElement
			for(let el of parent.getElementsByClassName('bet')) {
				el.disabled = true;
			}
			for(let el of parent.getElementsByClassName('cost')) {
				el.classList.add('d-none')
			}
			const scoretext = document.getElementById('option-' + oid);
			const score = Number(scoretext.textContent);
			scoretext.textContent = score + 1;
		}
	);
}




//POPOVER

const popClickBadgeTemplateDOM = document.createElement("IMG");
popClickBadgeTemplateDOM.classList.add("pop-badge");
popClickBadgeTemplateDOM.loading = "lazy";

const popover = document.getElementById("popover");

let pop_instance
let is_popover_visible = false

document.addEventListener("click", function(e) {

	if (is_popover_visible && document.getSelection().type != 'Range' && !e.target.classList.contains('pop-badge')) {
		pop_instance.hide()
	}

	active = document.activeElement;

	if (active.getAttribute("data-bs-toggle") == "popover") {
		const author = JSON.parse(active.dataset.popInfo);

		if (popover.getElementsByClassName('pop-badges')) {
			const badgesDOM = popover.getElementsByClassName('pop-badges')[0];
			badgesDOM.innerHTML = "";
			for (const badge of author["badges"]) {
				const badgeDOM = popClickBadgeTemplateDOM.cloneNode();
				badgeDOM.src = badge[0];
				badgeDOM.title = badge[1];
				if (badge[2])
					badgeDOM.alt = badge[2]
				badgesDOM.append(badgeDOM);
			}
		}

		popover.getElementsByClassName('pop-banner')[0].src = author["bannerurl"]
		popover.getElementsByClassName('pop-picture')[0].src = author["profile_url"]
		if (author["hat"]) {
			popover.getElementsByClassName('pop-hat')[0].src = author['hat'] + "?h=7"
		}
		else {
			popover.getElementsByClassName('pop-hat')[0].removeAttribute('src');
		}
		popover.getElementsByClassName('pop-username')[0].innerHTML = author["username"]
		if (popover.getElementsByClassName('pop-bio').length > 0) {
			popover.getElementsByClassName('pop-bio')[0].innerHTML = author["bio_html"]
		}
		popover.getElementsByClassName('pop-postcount')[0].innerHTML = author["post_count"]
		popover.getElementsByClassName('pop-commentcount')[0].innerHTML = author["comment_count"]
		popover.getElementsByClassName('pop-coins')[0].innerHTML = author["coins"]
		popover.getElementsByClassName('pop-marseybux')[0].innerHTML = author["marseybux"]
		popover.getElementsByClassName('pop-view_more')[0].href = author["url"]
		popover.getElementsByClassName('pop-created-date')[0].innerHTML = author["created_date"]
		popover.getElementsByClassName('pop-id')[0].innerHTML = author["id"]
		if (author["original_usernames"]) {
			popover.getElementsByClassName('pop-original-usernames')[0].innerHTML = author["original_usernames"]
		}
		else {
			popover.getElementsByClassName('pop-original-usernames')[0].innerHTML = ''
		}

		pop_instance = bootstrap.Popover.getOrCreateInstance(active, {
			content: popover.innerHTML,
			html: true,
		});
		pop_instance.show()
		is_popover_visible = true

		const generated_popovers = document.getElementsByClassName("popover")
		generated_popover = generated_popovers[generated_popovers.length-1]

		const badge_els = generated_popover.getElementsByClassName('pop-badge');
		for (badge_el of badge_els) {
			badge_el.setAttribute("data-bs-toggle", "tooltip");
			badge_el.setAttribute("data-bs-placement", "bottom");
			if (badge_el.alt) {
				const date = formatDate(new Date(badge_el.alt*1000));
				badge_el.title = badge_el.title + ' ' + date.toString();
				badge_el.removeAttribute('alt');
			}
		}

		bs_trigger(generated_popover)
	}
});
