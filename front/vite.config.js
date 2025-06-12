import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { SvelteKitPWA } from '@vite-pwa/sveltekit';

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit(),
		SvelteKitPWA({
			scope: '/',
			base: '/',
			registerType: 'autoUpdate',
			workbox: {
				globPatterns: ['**/*.{js,css,html,ico,png,svg,webp,woff,woff2}'],
				globIgnores: [
					'**/node_modules/**/*',
					'server/**/*',
					'**/*.map'
				],
				cleanupOutdatedCaches: true,
				clientsClaim: true,
				skipWaiting: true,
				runtimeCaching: [
					{
						urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
						handler: 'StaleWhileRevalidate',
						options: {
							cacheName: 'google-fonts-stylesheets',
						}
					},
					{
						urlPattern: /^https:\/\/fonts\.gstatic\.com\/.*/i,
						handler: 'CacheFirst',
						options: {
							cacheName: 'google-fonts-webfonts',
							expiration: {
								maxEntries: 10,
								maxAgeSeconds: 60 * 60 * 24 * 365
							}
						}
					},
					{
						urlPattern: /^\/api\/.*/,
						handler: 'NetworkFirst',
						options: {
							cacheName: 'api-cache',
							expiration: {
								maxEntries: 50,
								maxAgeSeconds: 60 * 30
							}
						}
					}
				]
			},
			devOptions: {
				enabled: true,
				suppressWarnings: true,
				type: 'module',
				navigateFallback: '/',
			},
			kit: {},
			manifest: {
				name: 'Real Estate Auction Platform',
				short_name: 'Auction',
				description: 'Discover exclusive properties through transparent auctions. Join thousands of satisfied buyers in finding their dream properties.',
				start_url: '/',
				scope: '/',
				display: 'standalone',
				orientation: 'portrait-primary',
				background_color: '#ffffff',
				theme_color: '#a78bfa',
				categories: ['business', 'finance', 'real estate'],
				lang: 'en',
				icons: [
					{
						src: '/icons/icon-72x72.png',
						sizes: '72x72',
						type: 'image/png',
						purpose: 'maskable any'
					},
					{
						src: '/icons/icon-96x96.png',
						sizes: '96x96',
						type: 'image/png',
						purpose: 'maskable any'
					},
					{
						src: '/icons/icon-128x128.png',
						sizes: '128x128',
						type: 'image/png',
						purpose: 'maskable any'
					},
					{
						src: '/icons/icon-144x144.png',
						sizes: '144x144',
						type: 'image/png',
						purpose: 'maskable any'
					},
					{
						src: '/icons/icon-152x152.png',
						sizes: '152x152',
						type: 'image/png',
						purpose: 'maskable any'
					},
					{
						src: '/icons/icon-192x192.png',
						sizes: '192x192',
						type: 'image/png',
						purpose: 'maskable any'
					},
					{
						src: '/icons/icon-384x384.png',
						sizes: '384x384',
						type: 'image/png',
						purpose: 'maskable any'
					},
					{
						src: '/icons/icon-512x512.png',
						sizes: '512x512',
						type: 'image/png',
						purpose: 'maskable any'
					}
				],
				shortcuts: [
					{
						name: 'Active Auctions',
						short_name: 'Auctions',
						description: 'View all active auctions',
						url: '/auctions',
						icons: [{ src: '/icons/shortcut-auctions.png', sizes: '192x192' }]
					},
					{
						name: 'My Bids',
						short_name: 'Bids',
						description: 'View my active bids',
						url: '/profile/bids',
						icons: [{ src: '/icons/shortcut-bids.png', sizes: '192x192' }]
					}
				]
			}
		})
	],
	server: {
		host: '0.0.0.0',
		port: 5173,
		allowedHosts: ['localhost', '127.0.0.1', 'backend', 'auction_backend'],
		watch: {
			usePolling: true,
			interval: 1000
		},
		cors: true,
		proxy: {
			'/api': {
				target: 'http://backend:7500',
				changeOrigin: true,
				secure: false
			},
			'/ws': {
				target: 'ws://backend:7500',
				ws: true,
				changeOrigin: true,
				secure: false
			}
		}
	},
	optimizeDeps: {
		exclude: ['clsx'],
		include: ['chart.js', 'date-fns', 'leaflet'],
		force: true
	},
	build: {
		rollupOptions: {
			output: {
				manualChunks: undefined
			}
		}
	},
	define: {
		__API_BASE_URL__: JSON.stringify(process.env.VITE_API_BASE_URL || 'http://localhost:8451/api'),
		__WS_BASE_URL__: JSON.stringify(process.env.VITE_WS_BASE_URL || 'ws://localhost:8451/ws')
	}
});