const IMAGE_FORMATS = document.getElementById('IMAGE_FORMATS').value.split(',')

document.getElementById('post-title').value = localStorage.getItem("post-title")
document.getElementById('post-text').value = localStorage.getItem("post-text")
document.getElementById('post-url').value = localStorage.getItem("post-url")

document.getElementById('post-notify').checked = localStorage.getItem("post-notify") == 'true'
document.getElementById('post-new').checked = localStorage.getItem("post-new") == 'true'
document.getElementById('post-nsfw').checked = localStorage.getItem("post-nsfw") == 'true'
document.getElementById('post-private').checked = localStorage.getItem("post-private") == 'true'
document.getElementById('post-ghost').checked = localStorage.getItem("post-ghost") == 'true'

markdown(document.getElementById("post-text"));

function checkForRequired() {
	const title = document.getElementById("post-title");
	const url = document.getElementById("post-url");
	const text = document.getElementById("post-text");
	const button = document.getElementById("create_button");
	const image = document.getElementById("file-upload");
	const image2 = document.getElementById("file-upload-submit");

	if (url.value.length > 0 || image.files.length > 0 || image2.files.length > 0) {
		text.required = false;
		url.required=false;
	} else if (text.value.length > 0 || image.files.length > 0 || image2.files.length > 0) {
		url.required = false;
	} else {
		text.required = true;
		url.required = true;
	}

	const isValidTitle = title.checkValidity();
	const isValidURL = url.checkValidity();
	const isValidText = text.checkValidity();

	if (isValidTitle && (isValidURL || image.files.length > 0 || image2.files.length > 0)) {
		button.disabled = false;
	} else if (isValidTitle && isValidText) {
		button.disabled = false;
	} else {
		button.disabled = true;
	}
}
checkForRequired();

function hide_image() {
	x=document.getElementById('image-upload-block');
	url=document.getElementById('post-url').value;
	if (url.length>=1){
		x.classList.add('d-none');
	}
	else {
		x.classList.remove('d-none');
	}
}

document.onpaste = function(event) {
	files = structuredClone(event.clipboardData.files);

	if (files.length > 4)
	{
		alert("You can't upload more than 4 files at one time!")
		return
	}

	filename = files[0]

	if (filename)
	{
		filename = filename.name.toLowerCase()
		if (document.activeElement.id == 'post-text') {
			let filename = ''
			for (const file of files)
				filename += file.name + ', '
			filename = filename.toLowerCase().slice(0, -2)
			document.getElementById('file-upload-submit').value = files;
			document.getElementById('filename-show-submit').textContent = filename;
		}
		else {
			f=document.getElementById('file-upload');
			f.files = files;
			document.getElementById('filename-show').textContent = filename;
			document.getElementById('urlblock').classList.add('d-none');
			if (IMAGE_FORMATS.some(s => filename.endsWith(s)))
			{
				const fileReader = new FileReader();
				fileReader.readAsDataURL(f.files[0]);
				fileReader.addEventListener("load", function () {document.getElementById('image-preview').setAttribute('src', this.result);});
			}
			document.getElementById('post-url').value = null;
			localStorage.setItem("post-url", "")
			document.getElementById('image-upload-block').classList.remove('d-none')
		}
		checkForRequired();
	}
}

document.getElementById('file-upload').addEventListener('change', function(){
	f=document.getElementById('file-upload');
	document.getElementById('urlblock').classList.add('d-none');
	document.getElementById('filename-show').textContent = document.getElementById('file-upload').files[0].name.substr(0, 20);
	filename = f.files[0].name.toLowerCase()
	if (IMAGE_FORMATS.some(s => filename.endsWith(s)))
	{
		const fileReader = new FileReader();
		fileReader.readAsDataURL(f.files[0]);
		fileReader.addEventListener("load", function () {document.getElementById('image-preview').setAttribute('src', this.result);});
	}
	checkForRequired();
})

function savetext() {
	localStorage.setItem("post-title", document.getElementById('post-title').value)
	localStorage.setItem("post-text", document.getElementById('post-text').value)
	localStorage.setItem("post-url", document.getElementById('post-url').value)

	let sub = document.getElementById('sub')
	if (sub) localStorage.setItem("sub", sub.value)

	localStorage.setItem("post-notify", document.getElementById('post-notify').checked)
	localStorage.setItem("post-new", document.getElementById('post-new').checked)
	localStorage.setItem("post-nsfw", document.getElementById('post-nsfw').checked)
	localStorage.setItem("post-private", document.getElementById('post-private').checked)
	localStorage.setItem("post-ghost", document.getElementById('post-ghost').checked)
}


function autoSuggestTitle()	{

	const urlField = document.getElementById("post-url");

	const titleField = document.getElementById("post-title");

	const isValidURL = urlField.checkValidity();

	if (isValidURL && urlField.value.length > 0 && titleField.value === "") {

		const x = new XMLHttpRequest();
		x.withCredentials=true;
		x.onreadystatechange = function() {
			if (x.readyState == 4 && x.status == 200 && !titleField.value) {

				title=JSON.parse(x.responseText)["title"];
				titleField.value=title;
				checkForRequired()
			}
		}
		x.open('get','/submit/title?url=' + urlField.value);
		x.setRequestHeader('xhr', 'xhr');
		x.send(null);

	};

};

function ghost_toggle(t) {
	const followers = document.getElementById("post-notify")
	if (t.checked == true) {
		followers.checked = false;
		followers.disabled = true;
	} else {
		followers.disabled = false;
	}
}

function checkRepost() {
	const system = document.getElementById('system')
	system.innerHTML = "";
	const url = document.getElementById('post-url').value
	const min_repost_check = 9;

	if (url && url.length >= min_repost_check) {
		const xhr = new XMLHttpRequest();
		xhr.open("post", "/is_repost");
		xhr.setRequestHeader('xhr', 'xhr');
		const form = new FormData()
		form.append("url", url);

		xhr.onload=function(){
			try {data = JSON.parse(xhr.response)}
			catch(e) {console.log(e)}

			if (data && data["permalink"]) {
				const permalinkText = escapeHTML(data["permalink"]);
				const permalinkURI = encodeURI(data["permalink"]);
				if (permalinkText) {
					system.innerHTML = `This is a repost of <a href="${permalinkURI}">${permalinkText}</a>`;
				}
			}
		}
		xhr.send(form)
	}
}

document.addEventListener('keydown', (e) => {
	if(!((e.ctrlKey || e.metaKey) && e.key === "Enter"))
		return;

	const submitButton = document.getElementById('create_button')

	submitButton.click();
});

checkRepost();

if (location.href == '/submit') {
	const sub = document.getElementById('sub')
	if (sub) sub.value = localStorage.getItem("sub")
}

const filelist = document.getElementById('upload-filelist');

document.addEventListener('DOMContentLoaded', function () {
    /**
     * Sets up the elements inside file upload rows.
     *
     * @param {File} file
     * @return {HTMLLIElement} row
     */
    function addRow(file) {
        var row = document.createElement('li');

        var name = document.createElement('span');
        name.textContent = file.name;
        name.className = 'file-name';

        var progressIndicator = document.createElement('span');
        progressIndicator.className = 'progress-percent';
        progressIndicator.textContent = '0%';

        var progressBar = document.createElement('progress');
        progressBar.className = 'file-progress';
        progressBar.setAttribute('max', '100');
        progressBar.setAttribute('value', '0');

        row.appendChild(name);
        row.appendChild(progressBar);
        row.appendChild(progressIndicator);

		filelist.innerHTML = '';
        filelist.appendChild(row);
        return row;
    }

    /**
     * Updates the page while the file is being uploaded.
     *
     * @param {ProgressEvent} evt
     */
    function handleUploadProgress(evt) {
        var xhr = evt.target;
        var bar = xhr.bar;
        var percentIndicator = xhr.percent;

        /* If we have amounts of work done/left that we can calculate with
           (which, unless we're uploading dynamically resizing data, is always), calculate the percentage. */
        if (evt.lengthComputable) {
            var progressPercent = Math.floor((evt.loaded / evt.total) * 100);
            bar.setAttribute('value', progressPercent);
            percentIndicator.textContent = progressPercent + '%';
        }
    }

    /**
     * Complete the uploading process by checking the response status and, if the
     * upload was successful, writing the URL(s) and creating the copy element(s)
     * for the files.
     *
     * @param {ProgressEvent} evt
     */
    function handleUploadComplete(evt) {
        var xhr = evt.target;
        var bar = xhr.bar;
        var row = xhr.row;
        var percentIndicator = xhr.percent;

        percentIndicator.style.visibility = 'hidden';
        bar.style.visibility = 'hidden';
        row.removeChild(bar);
        row.removeChild(percentIndicator);
        var respStatus = xhr.status;

        var url = document.createElement('span');
        url.className = 'file-url';
        row.appendChild(url);

        var link = document.createElement('a');
        if (respStatus === 200) {
            var response = JSON.parse(xhr.responseText);
            if (response.success) {
                link.textContent = response.files[0].url.replace(/.*?:\/\//g, '');
                link.href = response.files[0].url;
                url.appendChild(link);
                var copy = document.createElement('button');
                copy.className = 'upload-clipboard-btn';
                var glyph = document.createElement('img');
                glyph.src = 'img/glyphicons-512-copy.png';
                copy.appendChild(glyph);
                url.appendChild(copy);
                copy.addEventListener("click", function (event) {
                    /* Why create an element?  The text needs to be on screen to be
                       selected and thus copied. The only text we have on-screen is the link
                       without the http[s]:// part. So, this creates an element with the
                       full link for a moment and then deletes it.

                       See the "Complex Example: Copy to clipboard without displaying
                       input" section at: https://stackoverflow.com/a/30810322 */
                    var element = document.createElement('a');
                    element.textContent = response.files[0].url;
                    link.appendChild(element);
                    var range = document.createRange();
                    range.selectNode(element);
                    window.getSelection().removeAllRanges();
                    window.getSelection().addRange(range);
                    document.execCommand("copy");
                    link.removeChild(element);
                });
            } else {
                bar.innerHTML = 'Error: ' + response.description;
            }
        } else if (respStatus === 413) {
            link.textContent = 'File too big!';
            url.appendChild(link);
        } else {
            var response = JSON.parse(xhr.responseText);
            link.textContent = response.description;
            url.appendChild(link);
        }
    }

    /**
     * Updates the page while the file is being uploaded.
     *
     * @param {File} file
     * @param {HTMLLIElement} row
     */
    function uploadFile(file, row) {
        var bar = row.querySelector('.file-progress');
        var percentIndicator = row.querySelector('.progress-percent');
        var xhr = new XMLHttpRequest();
        xhr.open('POST', 'upload.php');

        xhr['row'] = row;
        xhr['bar'] = bar;
        xhr['percent'] = percentIndicator;
        xhr.upload['bar'] = bar;
        xhr.upload['percent'] = percentIndicator;

        xhr.addEventListener('load', handleUploadComplete, false);
        xhr.upload.onprogress = handleUploadProgress;

        var form = new FormData();
        form.append('files[]', file);
        xhr.send(form);
    }

    /**
     * Prevents the browser for allowing the normal actions associated with an event.
     * This is used by event handlers to allow custom functionality without
     * having to worry about the other consequences of that action.
     *
     * @param {Event} evt
     */
    function stopDefaultEvent(evt) {
        evt.stopPropagation();
        evt.preventDefault();
    }

    /**
     * Adds 1 to the state and changes the text.
     *
     * @param {Object} state
     * @param {HTMLButtonElement} element
     * @param {DragEvent} evt
     */
    function handleDrag(state, element, evt) {
        stopDefaultEvent(evt);
        if (state.dragCount == 1) {
            element.textContent = 'Drop it here~';
        }
        state.dragCount += 1;
    }

    /**
     * Subtracts 1 from the state and changes the text back.
     *
     * @param {Object} state
     * @param {HTMLButtonElement} element
     * @param {DragEvent} evt
     */
    function handleDragAway(state, element, evt) {
        stopDefaultEvent(evt);
        state.dragCount -= 1;
        if (state.dragCount == 0) {
            element.textContent = 'Select or drop file(s)';
        }
    }

    /**
     * Prepares files for uploading after being added via drag-drop.
     *
     * @param {Object} state
     * @param {HTMLButtonElement} element
     * @param {DragEvent} evt
     */
    function handleDragDrop(state, element, evt) {
        stopDefaultEvent(evt);
        handleDragAway(state, element, evt);
        var len = evt.dataTransfer.files.length;
        for (var i = 0; i < len; i++) {
            var file = evt.dataTransfer.files[i];
            var row = addRow(file);
            uploadFile(file, row);
        }
    }

    /**
     * Prepares the files to be uploaded when they're added to the <input> element.
     *
     * @param {InputEvent} evt
     */
    function uploadFiles(evt) {
        var len = evt.target.files.length;
        // For each file, make a row, and upload the file.
        for (var i = 0; i < len; i++) {
            var file = evt.target.files[i];
            var row = addRow(file);
            uploadFile(file, row);
        }
    }

    /**
     * Opens up a "Select files.." dialog window to allow users to select files to upload.
     *
     * @param {HTMLInputElement} target
     * @param {InputEvent} evt
     */
    function selectFiles(target, evt) {
        stopDefaultEvent(evt);
        target.click();
    }

    /* Handles the pasting function */
    window.addEventListener("paste", e => {
        var len = e.clipboardData.files.length;
        for (var i = 0; i < len; i++) {
            var file = e.clipboardData.files[i];
            var row = addRow(file);
            uploadFile(file, row);
        }
    });


    /* Set-up the event handlers for the <button>, <input> and the window itself
       and also set the "js" class on selector "#upload-form", presumably to
       allow custom styles for clients running javascript. */
    var state = {dragCount: 0};
    var uploadButton = document.getElementById('image-upload-block');
    window.addEventListener('dragenter', handleDrag.bind(this, state, uploadButton), false);
    window.addEventListener('dragleave', handleDragAway.bind(this, state, uploadButton), false);
    window.addEventListener('drop', handleDragAway.bind(this, state, uploadButton), false);
    window.addEventListener('dragover', stopDefaultEvent, false);


    var uploadInput = document.getElementById('file-upload');
    uploadInput.addEventListener('change', uploadFiles);
    // uploadButton.addEventListener('click', selectFiles.bind(this, uploadInput));
    uploadButton.addEventListener('drop', handleDragDrop.bind(this, state, uploadButton), false);
});
