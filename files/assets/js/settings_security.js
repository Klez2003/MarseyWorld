document.getElementById('new_email').addEventListener('input', function() {
	document.getElementById("email-password").classList.remove("d-none");
	document.getElementById("email-password-label").classList.remove("d-none");
	document.getElementById("emailpasswordRequired").classList.remove("d-none");
});
const twoStepModal = bootstrap.Modal.getOrCreateInstance(document.getElementById('2faModal'))

function emailVerifyText() {
	document.getElementById("email-verify-text").innerHTML = "Verification email sent! Please check your inbox.";
}

document.getElementById('2faToggle').addEventListener('change', () => {twoStepModal.show()})
