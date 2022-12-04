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

function blockUser() {
	var usernameField = document.getElementById("block-username");
	var isValidUsername = usernameField.checkValidity();
	username = usernameField.value;
	if (isValidUsername) {
		const xhr = new XMLHttpRequest();
		xhr.open("post", "/settings/block");
		xhr.setRequestHeader('xhr', 'xhr');
		f=new FormData();
		f.append("username", username);
		f.append("formkey", formkey());
		xhr.onload=function(){
			if (xhr.status<300) {
				location.reload();
			}
			else {
				showToast(false, "Error, please try again later.");
			}
		}
		xhr.send(f)
	}
}

function unblockUser(t, url) {
	postToast(t, url, null,
		() => {
			t.parentElement.parentElement.remove();
		}	
	);
}
