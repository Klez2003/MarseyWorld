let old_body_text, old_title_box
function togglePostEdit(id) {
	const body = document.getElementById("post-body");
	const title = document.getElementById("post-title");
	const sig = document.getElementById("post-sig");
	const notes = document.getElementById("post-notes");
	const form = document.getElementById("edit-post-body-"+id);
	const body_box = document.getElementById("post-edit-box-"+id);
	const title_box = document.getElementById("post-edit-title");

	body.classList.toggle("d-none");
	title.classList.toggle("d-none");
	sig.classList.toggle("d-none");
	notes.classList.toggle("d-none");
	form.classList.toggle("d-none");

	if (body.classList.contains('d-none')) {
		old_body_text = body_box.value;
		autoExpand(body_box);
		markdown(body_box);
		charLimit(body_box.id, 'charcount-post-edit')

		old_title_box = title_box.value;
		autoExpand(title_box);
	}
	else {
		body_box.value = old_body_text;
		title_box.value = old_title_box;
	}
	close_inline_emoji_modal();
};

document.getElementById('post-edit-title').addEventListener('keydown', (e) => {
	if (e.key === "Enter") e.preventDefault();
})
