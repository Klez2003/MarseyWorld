document.getElementById('new_email').addEventListener('input', function () {
	document.getElementById("email-password").classList.remove("d-none");
	document.getElementById("email-password-label").classList.remove("d-none");
	document.getElementById("emailpasswordRequired").classList.remove("d-none");
});

function emailVerifyText() {
	document.getElementById("email-verify-text").innerHTML = "Verification email sent! Please check your inbox.";
}

document.getElementById('2faToggle').addEventListener('change', () => {
	location.hash = 'm-2fa'
})
