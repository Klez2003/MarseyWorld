function fp(fp) {
	const xhr = new XMLHttpRequest();
	xhr.open("POST", '/fp/'+fp);
	xhr.setRequestHeader('xhr', 'xhr');
	const form = new FormData()
	form.append("formkey", formkey());
	xhr.send(form);
};

const fpPromise = import('/assets/js/vendor/fp.js?x=7')
.then(FingerprintJS => FingerprintJS.load())

fpPromise
.then(fp => fp.get())
.then(result => {fp(result.visitorId)})
