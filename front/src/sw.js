/* eslint-disable no-undef */
import { registerRoute } from 'workbox-routing';
import { StaleWhileRevalidate, CacheFirst } from 'workbox-strategies';
import { precacheAndRoute } from 'workbox-precaching';

// Precache assets injected by VitePWA (this line is mandatory)
precacheAndRoute(self.__WB_MANIFEST || []);

// Cache Google Fonts CSS
registerRoute(
	/^https:\/\/fonts\.googleapis\.com\/.*/i,
	new StaleWhileRevalidate({
		cacheName: 'google-fonts-stylesheets'
	})
);

// Cache Google Fonts files
registerRoute(
	/^https:\/\/fonts\.gstatic\.com\/.*/i,
	new CacheFirst({
		cacheName: 'google-fonts-webfonts',
		plugins: [
			{
				cacheWillUpdate: async ({ response }) =>
					response && response.status === 200 ? response : null
			}
		]
	})
);

// Optional: cache images or API calls (example)
registerRoute(
	/\.(?:png|jpg|jpeg|svg|gif|webp)$/,
	new CacheFirst({
		cacheName: 'image-cache',
	})
);
