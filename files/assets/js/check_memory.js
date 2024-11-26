if (navigator.deviceMemory < 8 && !navigator.brave) {
	const xhr = new XMLHttpRequest();
	xhr.open("POST", '/report_memory',);
	xhr.setRequestHeader('xhr', 'xhr');
	const form = new FormData()
	form.append('formkey', formkey());
	form.append("memory", navigator.deviceMemory);
	xhr.send(form);
}