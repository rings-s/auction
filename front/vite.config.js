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
		// Disable WebSocket HMR temporarily to focus on route issues
		hmr: false,
		watch: {
			usePolling: true,
			interval: 1000
		},
		cors: true
	},
	optimizeDeps: {
		exclude: ['clsx'],
		include: ['chart.js', 'date-fns', 'leaflet']
	},
	define: {
		__API_BASE_URL__: JSON.stringify('http://localhost:8451/api'),
		__WS_BASE_URL__: JSON.stringify('ws://localhost:8451/ws')
	}
});