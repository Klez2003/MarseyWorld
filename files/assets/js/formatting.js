
/* addFormattingCopyButtons(): creates a button in the first column of each row of a table
	that copies the text in the second column of that row */
function addFormattingCopyButtons() {
	let allTablesGenerateCopyButtons = document.getElementsByClassName('generate-copy-buttons')

	for (let table = 0; table < allTablesGenerateCopyButtons.length; table++) {

		if (allTablesGenerateCopyButtons[table].tagName != 'TABLE') {
			continue;
		}

		for (let i = 1, row; row = allTablesGenerateCopyButtons[table].rows[i]; i++) {

			const textCopyButton = document.createElement("button");
			textCopyButton.setAttribute("type", "button");
			textCopyButton.className = "btn caction ml-1 py-0 nobackground px-1 text-muted copy-link";

			/* replace HTML newlines with text newlines */
			let cleanedText = row.cells[1].cloneNode(true)
			cleanedText.innerHTML = cleanedText.innerHTML.replace(/<br>/gi, "\n")
			/* remove lots of extraneous tabs */
			cleanedText = cleanedText.textContent.replace(/\t/g,'');
			textCopyButton.setAttribute("data-clipboard-text", cleanedText);

			copyIcon = document.createElement("i");
			copyIcon.className = "fas fa-copy";

			textCopyButton.insertAdjacentElement('afterbegin', copyIcon)

			const textCopyButtonDiv = document.createElement("div");
			textCopyButtonDiv.appendChild(textCopyButton);
			textCopyButtonDiv.className = "mr-4 ml-auto my-auto";

			const x = row.cells[1].innerHTML
			row.cells[1].innerHTML = `<div class="d-flex">${x}${textCopyButtonDiv.outerHTML}</div>`
		}
	}


}

addFormattingCopyButtons();
