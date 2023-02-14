
/* addFormattingCopyButtons(): creates a button in the first column of each row of a table
	that copies the text in the second column of that row */
function addFormattingCopyButtons() {
	var allTablesGenerateCopyButtons = document.getElementsByClassName('generate-copy-buttons')

	for (let table = 0; table < allTablesGenerateCopyButtons.length; table++) {

		if(allTablesGenerateCopyButtons[table].tagName != 'TABLE') {
			continue;
		}

		for (var i = 1, row; row = allTablesGenerateCopyButtons[table].rows[i]; i++) {

			let textCopyButton = document.createElement("button");
			textCopyButton.setAttribute("type", "button");
			textCopyButton.className = "btn caction py-0 nobackground px-1 text-muted copy-link";

			/* replace HTML newlines with text newlines */
			var cleanedText = row.cells[1].cloneNode(true)
			cleanedText.innerHTML = cleanedText.innerHTML.replace(/<br>/gi, "\n")
			/* remove lots of extraneous tabs */
			cleanedText = cleanedText.textContent.replace(/\t/g,'');
			textCopyButton.setAttribute("data-clipboard-text", cleanedText);

			copyIcon = document.createElement("i");
			copyIcon.className = "fas fa-copy";

			textCopyButton.insertAdjacentElement('afterbegin', copyIcon)
			row.cells[0].appendChild(textCopyButton);
		}
	}


}

addFormattingCopyButtons();
