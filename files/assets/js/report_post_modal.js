const reason_post = document.getElementById("reason_post")
const reportPostButton = document.getElementById("reportPostButton");

reason_post.addEventListener('keydown', (e) => {
	if(!((e.ctrlKey || e.metaKey) && e.key === "Enter")) return;

	const targetDOM = document.activeElement;
	if(!(targetDOM instanceof HTMLInputElement)) return;

	reportPostButton.click()
	bootstrap.Modal.getOrCreateInstance(document.getElementById('reportPostModal')).hide()
});

function report_postModal(id) {
	reportPostButton.disabled = false;
	reportPostButton.classList.remove('disabled');
	reportPostButton.innerHTML='Report post';
	reportPostButton.dataset.id = id

	reason_post.value = ""
	setTimeout(() => {
		reason_post.focus()
	}, 500);
};

reportPostButton.onclick = function() {
	this.innerHTML='Reporting post';
	this.disabled = true;
	this.classList.add('disabled');

	postToast(this, '/report/post/' + reportPostButton.dataset.id,
		{
			"reason": reason_post.value
		},
		() => {}
	);
}
