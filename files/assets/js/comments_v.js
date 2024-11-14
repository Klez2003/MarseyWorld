const reason_comment = document.getElementById("reason_comment")
const reportCommentButton = document.getElementById("reportCommentButton");

reason_comment.addEventListener('keydown', (e) => {
	if (!((e.ctrlKey || e.metaKey) && e.key === "Enter")) return;

	const targetDOM = document.activeElement;
	if (!(targetDOM instanceof HTMLInputElement)) return;

	reportCommentButton.click()
	bootstrap.Modal.getOrCreateInstance(document.getElementById('reportCommentModal')).hide()
});


function report_commentModal(id, author) {
	document.getElementById("comment-author").textContent = author;

	reportCommentButton.innerHTML='Report comment';
	reportCommentButton.disabled = false;
	reportCommentButton.classList.remove('disabled');
	reportCommentButton.blur();
	reportCommentButton.dataset.id = id

	reason_comment.value = ""
	setTimeout(() => {
		reason_comment.focus()
	}, 500);
};

reportCommentButton.onclick = function() {
	this.innerHTML='Reporting comment';
	this.disabled = true;
	this.classList.add('disabled');

	postToast(this, '/report/comment/' + reportCommentButton.dataset.id,
		{
			"reason": reason_comment.value
		},
		() => {}
	);
}

// Returns the selection text based on the range with the HTML
function getSelectionTextHtml() {
	let html = "";
	let sel = getSelection();
	if (sel.rangeCount) {
		let container = document.createElement("div");
		container.appendChild(sel.getRangeAt(0).cloneContents());
		html += container.innerHTML;
	}
	return html;
}

let oldtext = {};
function toggleReplyBox(t, id) {
	const element = document.getElementById(id);
	const ta = element.getElementsByTagName('textarea')[0]
	element.classList.remove('d-none')
	const cid = id.replace('reply-to-c_','')
	oldtext[cid] = ta.value;

	let text = getSelection().toString().trim()
	if (text)
	{
		text = '> ' + text
		text = text.replace(/\n/g,"\n> ")
		text = text.replace(/\n> \n/g,"\n \n")
		text = text.split('> Reply')[0]
		text = text.replace(/\*/g,"\\*")

		if (ta.value && !ta.value.endsWith('\n')) ta.value += '\n'
		ta.value += text
		if (!ta.value.endsWith('\n')) ta.value += '\n'
		markdown(ta);
		handle_disabled(ta)
	}
	ta.focus()

	autoExpand(ta);

	let newHTML = ''
	if (t.innerHTML.includes('<i class="fas fa-'))
		newHTML += '<i class="fas fa-quotes"></i>'
	if (t.textContent)
		newHTML += 'Quote selection'
	t.innerHTML = newHTML
}

function toggleEdit(id) {
	const comment = document.getElementById("comment-text-"+id);
	const form = document.getElementById("comment-edit-"+id);
	const box = document.getElementById('comment-edit-body-'+id);
	const actions = document.getElementById('comment-' + id +'-actions');

	comment.classList.toggle("d-none");
	form.classList.toggle("d-none");
	actions.classList.toggle("d-none");

	if (comment.classList.contains('d-none')) {
		oldtext[id] = box.value;
		autoExpand(box);
		markdown(box);
		charLimit(box.id, 'charcount-edit-' + id)
	}
	else {
		box.value = oldtext[id];
	}		

	close_inline_emoji_modal();
};


const deleteCommentModal = document.getElementById('deleteCommentModal');
const deleteCommentButton = document.getElementById("deleteCommentButton");

function delete_commentModal(id) {
	deleteCommentButton.dataset.id = id
}

deleteCommentButton.onclick = () => {
	const id = deleteCommentButton.dataset.id
	postToast(deleteCommentButton, `/delete/comment/${id}`,
		{},
		() => {
			if (location.pathname == '/admin/reported/comments')
			{
				document.getElementById("post-info-"+id).remove()
				document.getElementById("comment-"+id).remove()
			}
			else
			{
				document.getElementsByClassName(`comment-${id}-only`)[0].classList.add('deleted');
				document.getElementById(`delete-${id}`).classList.add('d-none');
				document.getElementById(`undelete-${id}`).classList.remove('d-none');
				document.getElementById(`delete2-${id}`).classList.add('d-none');
				document.getElementById(`undelete2-${id}`).classList.remove('d-none');
			}
		}
	);
};

deleteCommentModal.addEventListener('keydown', (e) => {
	if (e.key === "Enter" && deleteCommentModal.classList.value == 'modal fade show')
		deleteCommentButton.click()
})

function post_reply(id) {
	close_inline_emoji_modal();

	const btn = document.getElementById(`save-reply-to-${id}`)
	btn.disabled = true;
	btn.classList.add('disabled');

	const form = new FormData();
	form.append('parent_id', id);

	const ta = document.getElementById('reply-form-body-'+id)
	form.append('body', ta.value);
	try {
		for (const e of document.getElementById(`file-upload-reply-c_${id}`).files)
			form.append('file', e);
	}
	catch(e) {}

	const xhr = createXhrWithFormKey("/reply", form);

	const upload_prog = document.getElementById(`upload-prog-c_${id}`);
	xhr[0].upload.onprogress = (e) => {handleUploadProgress(e, upload_prog)};

	xhr[0].onload=function() {
		upload_prog.classList.add("d-none")

		let data
		try {data = JSON.parse(xhr[0].response)}
		catch(e) {console.error(e)}
		if (data && data["comment"]) {
			const comments = document.getElementById('replies-of-c_' + id);
			const comment = data["comment"].replace(/data-src/g, 'src').replace(/data-cfsrc/g, 'src').replace(/style="display:none;visibility:hidden;"/g, '').replace(/data-nonce=".*?"/g, `data-nonce="${nonce}"`).replace(/ loading="lazy"/g, '');

			comments.insertAdjacentHTML('beforeend', comment);

			register_new_elements(comments);
			bs_trigger(comments);

			btn.disabled = false;
			btn.classList.remove('disabled');
			btn.blur();

			ta.value = ''
			document.getElementById('message-reply-'+id).innerHTML = ''
			document.getElementById('reply-to-c_'+id).classList.add('d-none')

			const input = ta.parentElement.querySelector('input[type="file"]')
			input.previousElementSibling.innerHTML = '';
			input.value = null;
			oldfiles[ta.id] = new DataTransfer();

			remove_dialog();
			restore_reply_buttons(`c_${id}`)

			embed_twitter_reddit()
		} else {
			showToast(false, getMessageFromJsonData(false, data));
		}
		btn.disabled = false;
		btn.classList.remove('disabled');
		btn.blur();
	}
	xhr[0].send(xhr[1]);
}

function comment_edit(id) {
	const btn = document.getElementById(`edit-btn-${id}`)
	btn.disabled = true
	btn.classList.add('disabled');

	const ta = document.getElementById('comment-edit-body-'+id)

	const form = new FormData();
	form.append('body', ta.value);

	try {
		for (const e of document.getElementById('file-edit-reply-'+id).files)
			form.append('file', e);
	}
	catch(e) {}
	const xhr = createXhrWithFormKey("/edit_comment/"+id, form);

	const upload_prog = document.getElementById(`upload-prog-edit-c_${id}`);
	xhr[0].upload.onprogress = (e) => {handleUploadProgress(e, upload_prog)};

	xhr[0].onload=function() {
		upload_prog.classList.add("d-none")

		let data
		try {data = JSON.parse(xhr[0].response)}
		catch(e) {console.error(e)}
		if (data && data["comment"]) {
			commentForm=document.getElementById('comment-text-'+id);
			commentForm.innerHTML = data["comment"].replace(/data-src/g, 'src').replace(/data-cfsrc/g, 'src').replace(/style="display:none;visibility:hidden;"/g, '').replace(/data-nonce=".*?"/g, `data-nonce="${nonce}"`).replace(/ loading="lazy"/g, '');

			document.getElementById('cancel-edit-'+id).click()

			register_new_elements(commentForm);
			bs_trigger(commentForm);

			document.getElementById('comment-edit-body-' + id).value = data["body"];

			if (data["ping_cost"]) {
				const ping_cost = document.getElementById('comment-ping-cost-' + id)
				ping_cost.textContent = commas(data["ping_cost"])
				ping_cost.parentElement.classList.remove('d-none')
			}

			if (data["edited_string"]) {
				const edited_string = document.getElementById('comment-edited_string-' + id)
				edited_string.textContent = data["edited_string"]
				edited_string.parentElement.classList.remove('d-none')
				edited_string.parentElement.onmouseover = () => {
					timestamp(edited_string.parentElement, Math.floor(Date.now() / 1000))
				};
			}

			const input = ta.parentElement.querySelector('input[type="file"]')
			input.previousElementSibling.innerHTML = '';
			input.value = null;
			oldfiles[ta.id] = new DataTransfer();

			remove_dialog();

			embed_twitter_reddit()
		}
		else {
			showToast(false, getMessageFromJsonData(false, data));
		}
		btn.disabled = false;
		btn.classList.remove('disabled');
		btn.blur();
	}
	xhr[0].send(xhr[1]);
}

function distinguished_toggle(t, fullname) {
	const ta = document.getElementById('reply-form-body-'+fullname)

	if (t.checked == true) {
		ta.minLength = 1;
		ta.maxLength = 10000
		charLimit(ta.id,`charcount-${fullname}`);
	}
}

function post_comment(fullname, hide) {
	const pids = document.getElementsByClassName('pid') //to account for crosspost embed
	if (pids.length) { //need .length, getElementsByClassName is always True
		const pid = pids[pids.length - 1].value
		const comments = JSON.parse(localStorage.getItem("comment-counts"))
		const newTotal = parseInt(comments[pid].c) + 1
		comments[pid] = {c: newTotal, t: comments[pid].t}
		localStorage.setItem("comment-counts", JSON.stringify(comments))
	}

	close_inline_emoji_modal();

	const btn = document.getElementById('save-reply-to-'+fullname)
	const ta = document.getElementById('reply-form-body-'+fullname)
	btn.disabled = true
	btn.classList.add('disabled');

	const form = new FormData();

	form.append('formkey', formkey());
	form.append('parent_fullname', fullname);
	form.append('body', ta.value);

	try {
		for (const e of document.getElementById('file-upload-reply-'+fullname).files)
			form.append('file', e);
	}
	catch(e) {}

	const admin_note_el = document.getElementById('admin-note-'+fullname)
	if (admin_note_el)
		form.append('admin_note', admin_note_el.checked);

	const distinguished_el = document.getElementById('distinguished-'+fullname)
	if (distinguished_el)
		form.append('distinguished', distinguished_el.checked);

	const xhr = new XMLHttpRequest();
	url = '/comment';
	xhr.open("POST", url);

	const upload_prog = document.getElementById(`upload-prog-${fullname}`);
	xhr.upload.onprogress = (e) => {handleUploadProgress(e, upload_prog)};

	xhr.setRequestHeader('xhr', 'xhr');
	xhr.onload=function() {
		upload_prog.classList.add("d-none")

		let data
		try {data = JSON.parse(xhr.response)}
		catch(e) {console.error(e)}
		if (data && data["comment"]) {
			if (hide) document.getElementById(hide).classList.add('d-none');

			let name = 'comment-form-space-' + fullname;
			commentForm = document.getElementById(name);

			let comments = document.getElementById('replies-of-' + fullname);
			let comment = data["comment"].replace(/data-src/g, 'src').replace(/data-cfsrc/g, 'src').replace(/style="display:none;visibility:hidden;"/g, '').replace(/data-nonce=".*?"/g, `data-nonce="${nonce}"`).replace(/ loading="lazy"/g, '');

			comments.insertAdjacentHTML('afterbegin', comment);

			register_new_elements(comments);
			bs_trigger(comments);

			btn.disabled = false;
			btn.classList.remove('disabled');
			btn.blur();

			ta.value = ''
			autoExpand(ta);

			document.getElementById('form-preview-'+fullname).innerHTML = ''
			document.getElementById('charcount-'+fullname).innerHTML = ''

			const input = ta.parentElement.querySelector('input[type="file"]')
			input.previousElementSibling.innerHTML = '';
			input.value = null;
			oldfiles[ta.id] = new DataTransfer();

			const ghost_town_box = document.getElementById('ghost-town-box')
			if (ghost_town_box) ghost_town_box.remove()

			remove_dialog();
			if (fullname.startsWith('c_'))
				restore_reply_buttons(fullname)

			if (fullname.startsWith('p_')) {
				const viewbtn = document.getElementById('viewbtn')
				if (viewbtn)
					viewbtn.dataset.ids = viewbtn.dataset.ids.slice(0, -1) + `, ${data['id']}]`
			}

			embed_twitter_reddit()
		}
		else {
			showToast(false, getMessageFromJsonData(false, data));
			btn.disabled = false;
			btn.classList.remove('disabled');
			btn.blur();
		}
	}
	xhr.send(form)
}


function restore_reply_buttons(fullname) {
	const reply_buttons = [document.getElementById(`toggle-reply-${fullname}`)]
	const mobile_reply_button = document.getElementById(`toggle-reply-${fullname}-mobile`)
	if (mobile_reply_button) reply_buttons.push(mobile_reply_button)
	for (const t of reply_buttons) {
		let newHTML = ''
		if (t.innerHTML.includes('<i class="fas fa-'))
			newHTML += '<i class="fas fa-reply"></i>'
		if (t.textContent)
			newHTML += 'Reply'
		t.innerHTML = newHTML
	}
}

function cancel(fullname) {
	const element = document.getElementById(`reply-to-${fullname}`);
	const ta = element.getElementsByTagName('textarea')[0]
	element.classList.add('d-none')
	const cid = fullname.replace('c_','')
	ta.value = oldtext[cid];

	remove_dialog();
	restore_reply_buttons(fullname)
	close_inline_emoji_modal();
}
