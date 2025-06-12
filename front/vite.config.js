import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit()
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
		include: ['chart.js', 'date-fns', 'leaflet']
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