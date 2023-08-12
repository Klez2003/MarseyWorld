function unbanDomain(t, domain) {
	postToast(
		t,
		`/admin/unban_domain/${domain}`,
		{},
		() => {t.parentElement.parentElement.remove()}
	);
}
