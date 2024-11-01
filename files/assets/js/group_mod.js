const members_tbody = document.getElementById('members_tbody')
const blacklist_tbody = document.getElementById('blacklist_tbody')
const myself_in_table = document.getElementById('myself-in-table')

function approve_membership(t, group, uid) {
	url = `/!${group}/${uid}/approve`
	postToast(t, url,
		{
		},
		() => {
			const mod = document.getElementById(`mod-${uid}`)
			if (mod) mod.classList.remove('d-none')
			document.getElementById(`counter-${uid}`).innerHTML = parseInt(members_tbody.lastElementChild.firstElementChild.innerHTML) + 1
			document.getElementById(`kick-${uid}`).classList.remove('d-none')
			document.getElementById(`time-${uid}`).innerHTML = formatTime(new Date());

			const myself_in_table_cloned = document.createElement('td')
			myself_in_table_cloned.id = `approver-${uid}`
			myself_in_table_cloned.innerHTML = myself_in_table.innerHTML
			document.getElementById(uid).append(myself_in_table_cloned)

			members_tbody.append(document.getElementById(uid));
			t.parentElement.remove()
		}
	);
}

function leave_membership(t, group) {
	url = `/!${group}/leave`
	postToast(t, url,
		{
		},
		() => {
			t.parentElement.parentElement.parentElement.remove();
		}
	);

}
function reject_membership(t, group, uid) {
	url = `/!${group}/${uid}/reject`
	postToast(t, url,
		{
		},
		() => {
			const mod = document.getElementById(`mod-${uid}`)
			if (mod) mod.remove()

			let new_counter = 1
			if (blacklist_tbody.lastElementChild)
				new_counter = parseInt(blacklist_tbody.lastElementChild.firstElementChild.innerHTML) + 1
			document.getElementById(`counter-${uid}`).innerHTML = new_counter
			document.getElementById(`unblacklist-${uid}`).classList.remove('d-none')
			document.getElementById(`time-${uid}`).innerHTML = formatTime(new Date());
			
			if (t.textContent == 'Are you sure?') { //implies kicking
				document.getElementById(`approver-${uid}`).innerHTML = myself_in_table.innerHTML;
			}
			else { //implies rejecting
				const myself_in_table_cloned = document.createElement('td')
				myself_in_table_cloned.innerHTML = myself_in_table.innerHTML
				document.getElementById(uid).append(myself_in_table_cloned)
			}

			const expires_on = document.createElement('td')
			expires_on.innerHTML = formatTime(new Date(Date.now()+2592000000));
			document.getElementById(uid).append(expires_on)

			blacklist_tbody.append(document.getElementById(uid));
			t.parentElement.remove();
		}
	);
}

function unblacklist(t, group, uid) {
	url = `/!${group}/${uid}/unblacklist`
	postToast(t, url,
		{
		},
		() => {
			t.parentElement.parentElement.remove();
		}
	);
}
