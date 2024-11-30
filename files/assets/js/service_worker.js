importScripts('/assets/js/vendor/workbox-sw.js');

const CACHE = "pwabuilder-page";

const offlineFallbackPage = "/offline.html?x=15";

self.addEventListener("message", (event) => {
	if (event.data && event.data.type === "SKIP_WAITING") {
		self.skipWaiting();
	}
});

self.addEventListener('install', async (event) => {
	event.waitUntil(
		caches.open(CACHE)
			.then((cache) => cache.add(offlineFallbackPage))
	);
});

if (workbox.navigationPreload.isSupported()) {
	workbox.navigationPreload.enable();
}

self.addEventListener('fetch', (event) => {
	if (event.request.mode === 'navigate') {
		event.respondWith((async () => {
			try {
				const preloadResp = await event.preloadResponse;

				if (preloadResp) {
					return preloadResp;
				}

				const networkResp = await fetch(event.request);
				return networkResp;
			} catch (error) {

				const cache = await caches.open(CACHE);
				const cachedResp = await cache.match(offlineFallbackPage);
				return cachedResp;
			}
		})());
	}
});

self.addEventListener('push', function(event) {
	const pushData = event.data.text();
	let data, title, body, url, icon;
	try {
		data = JSON.parse(pushData);
		title = data.title;
		body = data.body;
		url = data.url;
		icon = data.icon;
	} catch(e) {
		title = "Untitled";
		body = pushData;
	}
	const options = {
		body: body,
		data: {url: url},
		icon: icon
	};

	event.waitUntil(
		self.registration.showNotification(title, options)
	);
});

self.addEventListener('notificationclick', (e) => {
	e.notification.close();
	e.waitUntil(clients.matchAll({ type: 'window' }).then((clientsArr) => {
		const hadWindowToFocus = clientsArr.some((windowClient) => windowClient.url === e.notification.data.url ? (windowClient.focus(), true) : false);
		if (!hadWindowToFocus) clients.openWindow(e.notification.data.url).then((windowClient) => windowClient ? windowClient.focus() : null);
	}));
});
