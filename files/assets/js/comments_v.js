const reason_comment = document.getElementById("reason_comment")
const reportCommentButton = document.getElementById("reportCommentButton");

reason_comment.addEventListener('keydown', (e) => {
	if(!((e.ctrlKey || e.metaKey) && e.key === "Enter")) return;

	const targetDOM = document.activeElement;
	if(!(targetDOM instanceof HTMLInputElement)) return;

	reportCommentButton.click()
	bootstrap.Modal.getOrCreateInstance(document.getElementById('reportCommentModal')).hide()
});


function report_commentModal(id, author) {
	document.getElementById("comment-author").textContent = author;

	reportCommentButton.innerHTML='Report comment';
	reportCommentButton.disabled = false;
	reportCommentButton.classList.remove('disabled');
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

function toggleReplyBox(t, id) {
	const element = document.getElementById(id);
	const ta = element.getElementsByTagName('textarea')[0]
	element.classList.remove('d-none')

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
	}
	ta.focus()

	autoExpand(ta);

	let newHTML = ''
	if (t.innerHTML.includes('<i class="fas fa-'))
		newHTML += '<i class="fas fa-quotes"></i>'
	if (t.innerText)
		newHTML += 'Quote selection'
	t.innerHTML = newHTML
}

function toggleEdit(id){
	comment=document.getElementById("comment-text-"+id);
	form=document.getElementById("comment-edit-"+id);
	box=document.getElementById('comment-edit-body-'+id);
	actions = document.getElementById('comment-' + id +'-actions');

	comment.classList.toggle("d-none");
	form.classList.toggle("d-none");
	actions.classList.toggle("d-none");
	autoExpand(box);
	markdown(box);

	close_inline_speed_emoji_modal();
};


function delete_commentModal(t, id) {
	document.getElementById("deleteCommentButton").addEventListener('click', function() {
		postToast(t, `/delete/comment/${id}`,
			{
			},
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
	});
}

function post_reply(id) {
	close_inline_speed_emoji_modal();

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

	const xhr = createXhrWithFormKey("/reply", "POST", form);

	const upload_prog = document.getElementById(`upload-prog-c_${id}`);
	xhr[0].upload.onprogress = (e) => {handleUploadProgress(e, upload_prog)};

	xhr[0].onload=function(){
		upload_prog.classList.add("d-none")

		let data
		try {data = JSON.parse(xhr[0].response)}
		catch(e) {console.error(e)}
		if (data && data["comment"]) {
			const comments = document.getElementById('replies-of-c_' + id);
			const comment = data["comment"].replace(/data-src/g, 'src').replace(/data-cfsrc/g, 'src').replace(/style="display:none;visibility:hidden;"/g, '').replace(/data-nonce=".*?"/g, `data-nonce="${nonce}"`);

			comments.insertAdjacentHTML('beforeend', comment);

			register_new_elements(comments);
			bs_trigger(comments);

			btn.disabled = false;
			btn.classList.remove('disabled');

			ta.value = ''
			document.getElementById('message-reply-'+id).innerHTML = ''
			document.getElementById('reply-message-c_'+id).classList.add('d-none')

			const input = ta.parentElement.querySelector('input[type="file"]')
			input.previousElementSibling.innerHTML = '';
			input.value = null;
			oldfiles[ta.id] = []
		} else {
			showToast(false, getMessageFromJsonData(false, data));
		}
		btn.disabled = false;
		btn.classList.remove('disabled');
	}
	xhr[0].send(xhr[1]);
}

function comment_edit(id){
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
	const xhr = createXhrWithFormKey("/edit_comment/"+id, "POST", form);

	const upload_prog = document.getElementById(`upload-prog-edit-c_${id}`);
	xhr[0].upload.onprogress = (e) => {handleUploadProgress(e, upload_prog)};

	xhr[0].onload=function(){
		upload_prog.classList.add("d-none")

		let data
		try {data = JSON.parse(xhr[0].response)}
		catch(e) {console.error(e)}
		if (data && data["comment"]) {
			commentForm=document.getElementById('comment-text-'+id);
			commentForm.innerHTML = data["comment"].replace(/data-src/g, 'src').replace(/data-cfsrc/g, 'src').replace(/style="display:none;visibility:hidden;"/g, '').replace(/data-nonce=".*?"/g, `data-nonce="${nonce}"`)
			document.getElementById('cancel-edit-'+id).click()

			register_new_elements(commentForm);
			bs_trigger(commentForm);

			document.getElementById('comment-edit-body-' + id).value = data["body"];

			const input = ta.parentElement.querySelector('input[type="file"]')
			input.previousElementSibling.innerHTML = '';
			input.value = null;
			oldfiles[ta.id] = []
		}
		else {
			showToast(false, getMessageFromJsonData(false, data));
		}
		btn.disabled = false;
		btn.classList.remove('disabled');
	}
	xhr[0].send(xhr[1]);
}

function post_comment(fullname, hide){
	close_inline_speed_emoji_modal();

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

	const xhr = new XMLHttpRequest();
	url = '/comment';
	xhr.open("POST", url);

	const upload_prog = document.getElementById(`upload-prog-${fullname}`);
	xhr.upload.onprogress = (e) => {handleUploadProgress(e, upload_prog)};

	xhr.setRequestHeader('xhr', 'xhr');
	xhr.onload=function(){
		upload_prog.classList.add("d-none")

		let data
		try {data = JSON.parse(xhr.response)}
		catch(e) {console.error(e)}
		if (data && data["comment"]) {
			if (hide) document.getElementById(hide).classList.add('d-none');

			let name = 'comment-form-space-' + fullname;
			commentForm = document.getElementById(name);

			let comments = document.getElementById('replies-of-' + fullname);
			let comment = data["comment"].replace(/data-src/g, 'src').replace(/data-cfsrc/g, 'src').replace(/style="display:none;visibility:hidden;"/g, '').replace(/data-nonce=".*?"/g, `data-nonce="${nonce}"`);

			comments.insertAdjacentHTML('afterbegin', comment);

			register_new_elements(comments);
			bs_trigger(comments);

			btn.disabled = false;
			btn.classList.remove('disabled');

			ta.value = ''
			autoExpand(ta);

			document.getElementById('form-preview-'+fullname).innerHTML = ''
			document.getElementById('charcount-'+fullname).innerHTML = ''

			const input = ta.parentElement.querySelector('input[type="file"]')
			input.previousElementSibling.innerHTML = '';
			input.value = null;
			oldfiles[ta.id] = []

			const ghost_town_box = document.getElementById('ghost-town-box')
			if (ghost_town_box) ghost_town_box.remove()
		}
		else {
			showToast(false, getMessageFromJsonData(false, data));
			btn.disabled = false;
			btn.classList.remove('disabled');
		}
	}
	xhr.send(form)
}

function handle_action(type, cid, thing) {
	const btns = document.getElementsByClassName(`action-${cid}`)
	for (const btn of btns)
	{
		btn.disabled = true;
		btn.classList.add('disabled');
	}

	const form = new FormData();
	form.append('formkey', formkey());
	form.append('comment_id', cid);
	form.append('thing', thing);

	const xhr = new XMLHttpRequest();
	xhr.open("post", `/${type}/${cid}`);
	xhr.setRequestHeader('xhr', 'xhr');



	xhr.onload=function(){
		let data
		try {data = JSON.parse(xhr.response)}
		catch(e) {console.error(e)}
		if (data && data["response"]) {
			const element = document.getElementById(`${type}-${cid}`);
			element.innerHTML = data["response"].replace(/data-nonce=".*?"/g, `data-nonce="${nonce}"`)
			register_new_elements(element)
		} else {
			showToast(false, getMessageFromJsonData(false, data));
		}
		for (const btn of btns)
		{
			btn.disabled = false;
			btn.classList.remove('disabled');
		}
	}
	xhr.send(form)
}
