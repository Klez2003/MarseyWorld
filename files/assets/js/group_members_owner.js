const members_tbody = document.getElementById('members_tbody')

function approve_membership(t, group, uid) {
	url = `/!${group}/${uid}/approve`
	postToast(t, url,
		{
		},
		() => {
			document.getElementById(`kick-${uid}`).classList.remove('d-none')
			document.getElementById(`time-${uid}`).innerHTML = formatDate(new Date());
			document.getElementById(`counter-${uid}`).innerHTML = parseInt(members_tbody.lastElementChild.firstElementChild.innerHTML) + 1

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
