function option_vote_no_v() {
	showToast(false, "Only logged-in users can vote!");
}

function expandMarkdown(fullname) {
	const ta = document.getElementById('markdown-'+fullname);
	ta.classList.toggle('d-none');
	document.getElementsByClassName('text-expand-icon-'+fullname)[0].classList.toggle('fa-expand-alt');
	document.getElementsByClassName('text-expand-icon-'+fullname)[0].classList.toggle('fa-compress-alt');

	const items = document.getElementsByClassName(`expand-text-${fullname}`)
	for (let i=0; i < items.length; i++)
	{
		const e = items[i]
		if (e.innerHTML == 'View Source') e.innerHTML = 'Hide source'
		else e.innerHTML = 'View Source'
	}
};

function collapse_comment(id) {
	const element = document.getElementById(`comment-${id}`)
	const closed = element.classList.toggle("collapsed")
	const top = element.getBoundingClientRect().y

	if (closed && top < 0) {
		element.scrollIntoView()
		window.scrollBy(0, - 100)
	}

	const reports = document.getElementById(`reports-${id}`)
	if (reports) reports.classList.add('d-none')

	vids = element.getElementsByTagName('video')
	for (let i=0; i < vids.length; i++)
	{
		vids[i].pause()
	}

	const ta = document.getElementById('markdown-c_'+id);
	if (ta && !ta.classList.contains('d-none'))
		expandMarkdown(`c_${id}`)

	if (closed) {
		const children_count = document.getElementById(`replies-of-c_${id}`).getElementsByClassName('comment-body').length
		let children = children_count == 1 ? 'child' : 'children'
		document.getElementById(`children-count-${id}`).innerHTML = ` (${children_count} ${children})`
	}
	else {
		document.getElementById(`children-count-${id}`).innerHTML = ''
	}
};

function uncollapse_all_messages(t, id) {
	for (const child of document.getElementById(`replies-of-c_${id}`).children) {
		child.classList.remove("collapsed")
	}
	t.classList.add('d-none')
	t.nextElementSibling.classList.remove('d-none')
};
