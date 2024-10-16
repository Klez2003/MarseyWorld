const members_tbody = document.getElementById('members_tbody')
const myself_in_table = document.getElementById('myself-in-table')

function approve_membership(t, group, uid) {
	url = `/!${group}/${uid}/approve`
	postToast(t, url,
		{
		},
		() => {
			const mod = document.getElementById(`mod-${uid}`)
			if (mod) mod.classList.remove('d-none')
			document.getElementById(`kick-${uid}`).classList.remove('d-none')
			document.getElementById(`time-${uid}`).innerHTML = formatTime(new Date());
			document.getElementById(`counter-${uid}`).innerHTML = parseInt(members_tbody.lastElementChild.firstElementChild.innerHTML) + 1

			const myself_in_table_cloned = document.createElement('td')
			myself_in_table_cloned.innerHTML = myself_in_table.innerHTML
			document.getElementById(uid).append(myself_in_table_cloned)

			members_tbody.append(document.getElementById(uid));
			t.parentElement.remove()
		}
	);
}

function reject_membership(t, group, uid) {
	url = `/!${group}/${uid}/reject`
	postToast(t, url,
		{
		},
		() => {
			t.parentElement.parentElement.parentElement.remove();
		}
	);
}
