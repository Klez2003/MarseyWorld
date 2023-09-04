const deletePostButton = document.getElementById("deletePostButton");

function delete_postModal(id) {
	deletePostButton.dataset.id = id
}

deletePostButton.onclick = () => {
	const id = deletePostButton.dataset.id
	postToast(deletePostButton, `/delete/post/${id}`,
		{},
		() => {
			if (location.pathname == '/admin/reported/posts')
			{
				document.getElementById("reports-"+id).remove()
				document.getElementById("post-"+id).remove()
			}
			else
			{
				document.getElementById(`post-${id}`).classList.add('deleted');
				document.getElementById(`delete-${id}`).classList.add('d-none');
				document.getElementById(`undelete-${id}`).classList.remove('d-none');
				document.getElementById(`delete2-${id}`).classList.add('d-none');
				document.getElementById(`undelete2-${id}`).classList.remove('d-none');
			}
		}
	);
};
