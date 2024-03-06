function upload_banner(t, hole_name) {
	postToast(t,
		`/h/${hole_name}/settings/banners`,
		{
			"image": t.files[0]
		},
		(xhr) => {
			const list = document.getElementById('hole-banners')
			const url = JSON.parse(xhr.response)['url']
			const html = `
			<section class="mt-5 d-block hole-settings-subsection">
				<img class="mr-3" loading="lazy" alt="/h/${hole_name} banner" src="${url}">
				<button class="btn btn-danger hole-banner-delete-button mt-2" data-nonce="${nonce}" data-onclick="areyousure(this)" data-areyousure="delete_image(this, '/h/${hole_name}/settings/banners/delete')">Delete</button>
			</section>`

			list.insertAdjacentHTML('afterbegin', html);
			register_new_elements(list);

			const nobanners = document.getElementById('hole-banner-no-banners')
			if (nobanners) nobanners.remove()
		}
	);
}

function upload_sidebar(t, hole_name) {
	postToast(t,
		`/h/${hole_name}/settings/sidebars`,
		{
			"image": t.files[0]
		},
		(xhr) => {
			const list = document.getElementById('hole-sidebars')
			const url = JSON.parse(xhr.response)['url']
			const html = `
			<section class="mt-5 d-block hole-settings-subsection">
				<img class="mr-3" loading="lazy" alt="/h/${hole_name} sidebar" src="${url}">
				<button class="btn btn-danger hole-sidebar-delete-button mt-2" data-nonce="${nonce}" data-onclick="areyousure(this)" data-areyousure="delete_image(this, '/h/${hole_name}/settings/sidebars/delete')">Delete</button>
			</section>`

			list.insertAdjacentHTML('afterbegin', html);
			register_new_elements(list);

			const nosidebars = document.getElementById('hole-sidebar-no-sidebars')
			if (nosidebars) nosidebars.remove()
		}
	);
}

function delete_image(t, url) {
	postToast(t, url,
		{
			"url": t.previousElementSibling.src
		},
		() => {
			t.parentElement.remove();
		}
	);
}
