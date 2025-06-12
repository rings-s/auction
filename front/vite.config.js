import tailwindcss from '@tailwindcss/vite';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import { VitePWA } from 'vite-plugin-pwa';

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit(),
		VitePWA({
			registerType: 'autoUpdate',
			injectRegister: 'auto',
			includeAssets: ['favicon.ico', 'apple-touch-icon.png', 'icons/*.svg'],
			manifest: {
				name: 'Auction Real Estates',
				short_name: 'Auction',
				start_url: '/',
				display: 'standalone',
				background_color: '#ffffff',
				theme_color: '#4f46e5',
				icons: [
					{
						src: 'icons/icon-192x192.png',
						sizes: '192x192',
						type: 'image/png'
					},
					{
						src: 'icons/icon-512x512.png',
						sizes: '512x512',
						type: 'image/png'
					}
				]
			},
			workbox: {
				runtimeCaching: [
					{
						urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
						handler: 'StaleWhileRevalidate',
						options: {
							cacheName: 'google-fonts-stylesheets'
						}
					},
					{
						urlPattern: /^https:\/\/fonts\.gstatic\.com\/.*/i,
						handler: 'CacheFirst',
						options: {
							cacheName: 'google-fonts-webfonts',
							expiration: {
								maxEntries: 10,
								maxAgeSeconds: 60 * 60 * 24 * 365 // 1 year
							}
						}
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
