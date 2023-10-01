function togglePostEdit(id) {
	const body = document.getElementById("post-body");
	const title = document.getElementById("post-title");
	const form = document.getElementById("edit-post-body-"+id);

	body.classList.toggle("d-none");
	title.classList.toggle("d-none");
	form.classList.toggle("d-none");

	box = document.getElementById("post-edit-box-"+id);
	autoExpand(box);
	markdown(box);
	box = document.getElementById("post-edit-title");
	autoExpand(box);

	close_inline_speed_emoji_modal();
};

document.getElementById('post-edit-title').addEventListener('keydown', (e) => {
	if (e.key === "Enter") e.preventDefault();
})
