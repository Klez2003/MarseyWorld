const submitButton = document.getElementById('submit-btn')

const save_value = ['post-title', 'post-text', 'post-url', 'sub']
for (const id of save_value) {
	const value =  localStorage.getItem(id)
	if (value)
		document.getElementById(id).value = value
}

autoExpand(document.getElementById('post-text'))
markdown(document.getElementById("post-text"));

const save_checked = ['post-notify', 'post-new', 'post-nsfw', 'post-private', 'post-ghost']
for (const key of save_checked) {
	const value =  localStorage.getItem(key)
	if (value) {
		const element = document.getElementById(key)
		if (element) element.checked = (value == 'true')
	}
		
}

function savetext() {
	for (const id of save_value)
	{
		const value = document.getElementById(id).value
		if (value) localStorage.setItem(id, value)
	}

	for (const id of save_checked) {
		const element = document.getElementById(id)
		if (element) {
			localStorage.setItem(id, element.checked)
		}
	}
}


function checkForRequired() {
	const title = document.getElementById("post-title");
	const url = document.getElementById("post-url");
	const text = document.getElementById("post-text");
	const image = document.getElementById("file-upload");
	const image2 = document.getElementById("file-upload-submit");

	if (url.value.length > 0 || image.files.length > 0 || image2.files.length > 0) {
		text.required = false;
		url.required=false;
	} else if (text.value.length > 0 || image.files.length > 0 || image2.files.length > 0) {
		url.required = false;
	} else {
		text.required = true;
		url.required = true;
	}

	const isValidTitle = title.checkValidity();
	const isValidURL = url.checkValidity();
	const isValidText = text.checkValidity();

	if (isValidTitle && (isValidURL || image.files.length > 0 || image2.files.length > 0)) {
		submitButton.disabled = false;
	} else if (isValidTitle && isValidText) {
		submitButton.disabled = false;
	} else {
		submitButton.disabled = true;
	}
}
checkForRequired();

function hide_image() {
	x=document.getElementById('image-upload-block');
	url=document.getElementById('post-url').value;
	if (url.length>=1){
		x.classList.add('d-none');
	}
	else {
		x.classList.remove('d-none');
	}
}

function autoSuggestTitle()	{

	const urlField = document.getElementById("post-url");

	const titleField = document.getElementById("post-title");

	const isValidURL = urlField.checkValidity();

	if (isValidURL && urlField.value.length > 0 && titleField.value === "") {

		const x = new XMLHttpRequest();
		x.withCredentials=true;
		x.onreadystatechange = function() {
			if (x.readyState == 4 && x.status == 200 && !titleField.value) {

				title=JSON.parse(x.responseText)["title"];
				titleField.value=title;
				checkForRequired()
			}
		}
		x.open('get','/submit/title?url=' + urlField.value);
		x.setRequestHeader('xhr', 'xhr');
		x.send(null);

	};

};

function ghost_toggle(t) {
	const followers = document.getElementById("post-notify")
	if (t.checked == true) {
		followers.checked = false;
		followers.disabled = true;
	} else {
		followers.disabled = false;
	}
}

function checkRepost() {
	const system = document.getElementById('system')
	system.innerHTML = "";
	const url = document.getElementById('post-url').value
	const min_repost_check = 9;

	if (url && url.length >= min_repost_check) {
		const xhr = new XMLHttpRequest();
		xhr.open("post", "/is_repost");
		xhr.setRequestHeader('xhr', 'xhr');
		const form = new FormData()
		form.append("url", url);

		xhr.onload=function(){
			try {data = JSON.parse(xhr.response)}
			catch(e) {console.error(e)}

			if (data && data["permalink"]) {
				const permalinkText = escapeHTML(data["permalink"]);
				const permalinkURI = encodeURI(data["permalink"]);
				if (permalinkText) {
					system.innerHTML = `This is a repost of <a href="${permalinkURI}">${permalinkText}</a>`;
				}
			}
		}
		xhr.send(form)
	}
}

document.addEventListener('keydown', (e) => {
	if(!((e.ctrlKey || e.metaKey) && e.key === "Enter"))
		return;

	submitButton.click();
});

checkRepost();

function submit(form) {
	submitButton.disabled = true;

	const xhr = new XMLHttpRequest();
	xhr.withCredentials=true;

	formData = new FormData(form);

	formData.append("formkey", formkey());
	actionPath = form.getAttribute("action");

	xhr.open("POST", actionPath);

	const upload_prog = document.getElementById('upload-prog');
	xhr.upload.onprogress = (e) => {handleUploadProgress(e, upload_prog)};

	xhr.setRequestHeader('xhr', 'xhr');

	xhr.onload = function() {
		upload_prog.classList.add("d-none")

		if (xhr.status >= 200 && xhr.status < 300) {
			const res = JSON.parse(xhr.response)
			const post_id = res['post_id'];

			if (res['success']) {
				for (const id of save_value) {
					localStorage.setItem(id, "")
				}

				for (const id of save_checked) {
					const value = (id == "post-notify")
					localStorage.setItem(id, value)
				}
			}

			location.href = "/post/" + post_id
		} else {
			submitButton.disabled = false;
			document.getElementById('toast-post-error-text').innerText = "Error, please try again later."
			try {
				let data=JSON.parse(xhr.response);
				bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-error')).show();
				document.getElementById('toast-post-error-text').innerText = data["error"];
				if (data && data["details"]) document.getElementById('toast-post-error-text').innerText = data["details"];
			} catch(e) {
				bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-success')).hide();
				bootstrap.Toast.getOrCreateInstance(document.getElementById('toast-post-error')).show();
			}
		}
	};

	xhr.send(formData);
}
