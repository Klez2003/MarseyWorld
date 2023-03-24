function more_comments(cid, sort) {
	btn = document.getElementById(`btn-${cid}`);
	btn.disabled = true;
	btn.innerHTML = "Requesting...";
	const form = new FormData();
	form.append("formkey", formkey());
	form.append("sort", sort);
	const xhr = new XMLHttpRequest();

	let url;
	if (location.pathname.startsWith('/@') && location.pathname.endsWith('/comments'))
		url = location.pathname.replace("/comments", `/more_comments/${cid}`) 
	else 
		url = `/more_comments/${cid}`

	xhr.open("get", url);
	xhr.setRequestHeader('xhr', 'xhr');
	xhr.onload=function(){
		if (xhr.status==200) {
			let e = document.getElementById(`replies-of-c_${cid}`)
			e.innerHTML = xhr.response.replace(/data-src/g, 'src').replace(/data-cfsrc/g, 'src').replace(/style="display:none;visibility:hidden;"/g, '').replace(/data-nonce=".*?"/g, `data-nonce="${nonce}"`);
			register_new_elements(e);
			bs_trigger(e)

			if (typeof highlight_unread === "function")
				highlight_unread("old-comment-counts")
		}
		btn.disabled = false;
	}
	xhr.send(form)
}
