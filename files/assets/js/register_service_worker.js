'use strict';

function subscribeUser(swRegistration, applicationServerPublicKey, apiEndpoint) {
	const applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);
	swRegistration.pushManager.subscribe({
		userVisibleOnly: true,
		applicationServerKey: applicationServerKey
	})
	.then(function(subscription) {
		return updateSubscriptionOnServer(subscription, apiEndpoint);

	})
	.then(function(response) {
		if (!response.ok) {
			throw new Error('Bad status code from server.');
		}
		return response.json();
	})
	.then(function(responseData) {
		if (responseData.status!=="success") {
			throw new Error('Bad response from server.');
		}
	})
	.catch(function() {
	});
}

function registerServiceWorker(serviceWorkerUrl, applicationServerPublicKey, apiEndpoint) {
	let swRegistration = null;
	if ('serviceWorker' in navigator && 'PushManager' in window) {
		navigator.serviceWorker.register(serviceWorkerUrl)
		.then(function(swReg) {
			subscribeUser(swReg, applicationServerPublicKey, apiEndpoint);

			swRegistration = swReg;
		})
		.catch(function() {
		});
	} else {
	}
	return swRegistration;
}

registerServiceWorker(
	"/service_worker.js",
	document.getElementById('VAPID_PUBLIC_KEY').value,
	"/push_subscribe"
)
