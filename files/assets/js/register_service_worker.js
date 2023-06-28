'use strict';

function registerServiceWorker(serviceWorkerUrl){
	if ('serviceWorker' in navigator && 'PushManager' in window) {
		navigator.serviceWorker.register(serviceWorkerUrl);
	}
}

registerServiceWorker(
	"/assets/js/service_worker.js"
)
