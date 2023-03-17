function punishModal(t, kind, link, name, fullname) {
	const kind_title = kind.charAt(0).toUpperCase() + kind.slice(1)
	
	document.getElementById(`${kind}ModalTitle`).innerHTML = `${kind_title} @${name}`;
	document.getElementById(`${kind}_reason`).value = link;

	const btn = document.getElementById(`${kind}UserButton`)
	btn.innerHTML = `${kind_title} @${name}`;

	btn.onclick = () => {
		const values = {
			"days": document.getElementById(`${kind}_days`).value,
			"reason": document.getElementById(`${kind}_reason`).value
			}
		
		if (kind == "ban") {
			values["alts"] = document.getElementById(`${kind}_alts`).value;
		}

		postToast(t, `/${kind}_user/${fullname}`,
			values,
			() => {
				document.getElementById(`un${kind}-${fullname}`).classList.remove("d-none");
				document.getElementById(`un${kind}2-${fullname}`).classList.remove("d-none");
				const days = document.getElementById(`${kind}_days`).value
				if (!days) {
					t.classList.add("d-none")
				}
			}
		);
	}
}
