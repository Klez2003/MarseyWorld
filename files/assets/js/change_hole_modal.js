const hole_to = document.getElementById("hole_to")
const changeHoleButton = document.getElementById("changeHoleButton");

hole_to.addEventListener('keydown', (e) => {
	if (!((e.ctrlKey || e.metaKey) && e.key === "Enter")) return;

	const targetDOM = document.activeElement;
	if (!(targetDOM instanceof HTMLInputElement)) return;

	changeHoleButton.click()
	bootstrap.Modal.getOrCreateInstance(document.getElementById('changeHoleModal')).hide()
});

function change_holeModal(id) {
	changeHoleButton.disabled = false;
	changeHoleButton.classList.remove('disabled');
	changeHoleButton.blur();
	changeHoleButton.innerHTML='Change Hole';
	changeHoleButton.dataset.id = id

	hole_to.value = ""
	setTimeout(() => {
		hole_to.focus()
	}, 200);
};

changeHoleButton.onclick = function() {
	this.disabled = true;
	this.classList.add('disabled');

	postToast(this, '/change_hole/' + changeHoleButton.dataset.id,
		{
			"hole_to": hole_to.value
		},
		() => {}
	);
}
