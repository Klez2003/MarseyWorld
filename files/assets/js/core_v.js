function postToastSwitchAndRemoveFromTable(t, endpoint, username) {
	postToastSwitch(t, endpoint + username);
	t.parentElement.parentElement.remove();
}

function removeFollower(t, username) {
	postToastSwitchAndRemoveFromTable(t,'/remove_follow/', username);
}

function removeFollowing(t, username) {
	postToastSwitchAndRemoveFromTable(t,'/unfollow/', username);
}

function removeMod(e) {
    sendFormXHR(e,
        () => {
            e.target.parentElement.parentElement.remove();
        }
    )
}

function addSearchParam(e) {
	e = e || window.event;
	let paramExample = e.target.innerText;
	let param = paramExample.split(":")[0];
	let searchInput = document.querySelector("#large_searchbar input");
	searchInput.value = `${searchInput.value} ${param}:`;
	searchInput.focus();
}
